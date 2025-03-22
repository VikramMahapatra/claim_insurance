from extract_text import clean_text, extract_text_from_image, extract_images_and_text, extract_tables,extract_text_from_pdf
import faiss
import numpy as np
import os
import json
import logging
import requests

from fastapi import FastAPI, File, UploadFile, HTTPException, Request, APIRouter
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import spacy
import networkx as nx
import fitz  # PyMuPDF for handling PDF files
from typing import Any, List, Dict, Tuple
import pickle

import os
STATIC_DIRECTORY = os.path.join(os.path.dirname(__file__), "static")

# Initialize FastAPI app
router = APIRouter()

# Load SentenceTransformer model for embedding generation
model = SentenceTransformer('all-MiniLM-L6-v2')

dimension = 384  # Dimension of the SentenceTransformer embeddings
index = faiss.IndexFlatL2(dimension)  # L2 distance-based FAISS index

file_metadata = []  # To store metadata like filenames

# Initialize a directed graph for the knowledge graph
knowledge_graph = nx.DiGraph()

# Load spaCy model for entity recognition
nlp = spacy.load("en_core_web_sm")

# Function to extract entities and relationships from text
def extract_entities_and_relationships(text: str) -> List[Tuple[str, str]]: 
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities

# File paths
metadata_file = "file_metadata.json"
faiss_index_file = "faiss_index.bin"
knowledge_graph_file = "knowledge_graph.pkl"

# Load metadata
def load_metadata():
    global file_metadata
    if os.path.exists(metadata_file):
        with open(metadata_file, "r") as f:
            file_metadata = json.load(f)
    else:
        file_metadata = []

# Load FAISS index
def load_faiss_index():
    global index
    if os.path.exists(faiss_index_file):
        index = faiss.read_index(faiss_index_file)
    else:
        index = faiss.IndexFlatL2(dimension)

# Load the knowledge graph
def load_knowledge_graph():
    global knowledge_graph
    if os.path.exists(knowledge_graph_file):
        try:
            with open(knowledge_graph_file, "rb") as f:
                knowledge_graph = pickle.load(f)
        except (EOFError, pickle.UnpicklingError):
            logging.warning(f"File {knowledge_graph_file} is empty or corrupted. Initializing a new knowledge graph.")
            knowledge_graph = nx.DiGraph()
    else:
        logging.info(f"File {knowledge_graph_file} not found. Initializing a new knowledge graph.")
        knowledge_graph = nx.DiGraph()

# Save metadata
def save_metadata():
    with open(metadata_file, "w") as f:
        json.dump(file_metadata, f)

# Save FAISS index
def save_faiss_index():
    faiss.write_index(index, faiss_index_file)

# Save the knowledge graph
def save_knowledge_graph():
    with open(knowledge_graph_file, "wb") as f:
        pickle.dump(knowledge_graph, f)

# Load all components during initialization
def initialize_components():
    load_metadata()
    load_faiss_index()
    load_knowledge_graph()

# Initialize components when the module is loaded
initialize_components()

# Function to generate embeddings from text
def generate_embeddings(text: str) -> np.ndarray:
    return model.encode([text])[0]

# Function to extract entities and relationships from text
def extract_entities_and_relationships(text: str) -> List[Tuple[str, str]]:
    doc = spacy.load("en_core_web_sm")(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities

# Function to update the knowledge graph
def update_knowledge_graph(text: str, filename: str):
    entities = extract_entities_and_relationships(text)
    for ent, label in entities:
        knowledge_graph.add_node(ent, label=label)  # Add entities as nodes
        knowledge_graph.add_edge(filename, ent, relationship="contains")  # Connect file to entity
    save_knowledge_graph()


# Function to process the uploaded file and extract information
@router.post("/process-file/")
async def process_file(file: UploadFile = File(...)):
    content_type = file.content_type
    file_bytes = await file.read()

    # Check for HTML, XML, or PDF file type
    if content_type == "text/html" or file.filename.endswith(".html"):
        soup = BeautifulSoup(file_bytes, "html.parser")
    elif content_type == "text/xml" or file.filename.endswith(".xml"):
        soup = BeautifulSoup(file_bytes, "lxml-xml")
    elif content_type == "application/pdf" or file.filename.endswith(".pdf"):
        # Save the PDF file temporarily to extract text
        with open(file.filename, "wb") as f:
            f.write(file_bytes)
        pdf_text = extract_text_from_pdf(file.filename)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Please upload an HTML, XML, or PDF file.")

    # If it's an HTML or XML file, extract the text
    if content_type == "text/html" or file.filename.endswith(".html") or content_type == "text/xml" or file.filename.endswith(".xml"):
        cleaned_text = clean_text(soup.get_text())
        image_text = extract_images_and_text(soup)
        tables = extract_tables(soup)
        combined_text = cleaned_text + "\n\n" + image_text
        for table in tables:
            combined_text += "\n\n" + str(table)
    elif content_type == "application/pdf" or file.filename.endswith(".pdf"):
        combined_text = clean_text(pdf_text)

    # Generate embeddings for combined text
    embeddings = generate_embeddings(combined_text)

    # Store the embeddings in FAISS
    index.add(np.array([embeddings]))

    # Store the metadata about the file
    file_metadata.append({"filename": file.filename, "text": combined_text})

    save_metadata()
    save_faiss_index()

    # Update the knowledge graph with extracted entities and relationships
    update_knowledge_graph(combined_text, file.filename)

    return {"message": f"File '{file.filename}' processed and stored successfully."}

def convert_numpy_types(data: Any) -> Any:
    if isinstance(data, dict):
        return {key: convert_numpy_types(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_numpy_types(item) for item in data]
    elif isinstance(data, (np.float32, np.float64)):
        return float(data)
    return data

def extract_relevant_snippet(text, query):
    query_words = query.lower().split()  # Break query into words
    for word in query_words:
        if word in text.lower():
            start_index = text.lower().find(word)
            end_index = start_index + 200  # Capture the surrounding context (e.g., 200 chars)
            return text[start_index:end_index]  # Return the snippet of relevant text
    return "No relevant information found."


async def query_gpt4(most_relevant_doc):
    try:
        response = requests.post(
            url="https://swara-m8kd01zj-eastus2.cognitiveservices.azure.com/openai/deployments/gpt-35-turbo/chat/completions?api-version=2025-01-01-preview",
            headers={
                "Content-Type": "application/json",
                "api-key": "21V4PTl382IbMgm1IGD2NT2Fj0azR5U314QhTaNF2mwcX95BJDFxJQQJ99BCACHYHv6XJ3w3AAAAACOGL4yC",  # Ensure this is securely stored
            },
            json={
                "messages": [
                    {"role": "system", "content": "You are an expert at summarizing documents."},
                    {"role": "user", "content": most_relevant_doc}
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
        )

        if response.status_code == 200:
            response_data = response.json()
            choices = response_data.get("choices", [])
            return {"answer": choices[0].get("message", {}).get("content", "No response generated.") if choices else "No response generated."}
        else:
            return {"error": response.json()}

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    
# Modify FastAPI route to handle async properly
@router.post("/faiss/search/")
async def search_in_faiss(query: str):
    global index

    if len(file_metadata) == 0:
        return {"error": "No metadata available. Please store a file first."}

    # Generate embeddings for the query
    query_embedding = generate_embeddings(query)
    query_embedding = np.array(query_embedding, dtype=np.float32).reshape(1, -1)

    # Search in FAISS index
    distances, indices = index.search(query_embedding, k=1)

    # Retrieve relevant text
    top_results = []
    for distance, idx in zip(distances[0], indices[0]):
        if idx < len(file_metadata):
            text_content = file_metadata[idx]["text"]
            relevant_text = extract_relevant_snippet(text_content, query)
            top_results.append({
                "filename": file_metadata[idx]["filename"],
                "text": relevant_text,
                "distance": float(distance)  # Ensure JSON serializability
            })

    # Re-rank results
    ranked_results = re_rank_results(top_results, query)
    print("ranked_results", ranked_results)

    # Construct structured context for GPT summarization
    retrieved_context = "\n\n".join([
        f"Document: {res['filename']}\nSnippet: {res['text']}" for res in ranked_results
    ])
    full_prompt = (
        f"Context:\n{retrieved_context}\n\n"
        f"User Query: {query}\n\n"
        "Summarize the relevant information from the context in a concise manner."
    )

    # Call GPT for summarization (now properly using WebSockets)
    gpt_response = await query_gpt4(full_prompt)

    return {"results": ranked_results, "llm_response": gpt_response}




# Function to re-rank results based on the knowledge graph
def re_rank_results(results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    query_entities = extract_entities_and_relationships(query)
    entity_scores = {ent[0]: 0 for ent in query_entities}

    # Calculate scores based on knowledge graph relationships
    for result in results:
        for entity, _ in query_entities:
            if knowledge_graph.has_edge(result["filename"], entity):
                entity_scores[entity] += 1

    # Re-rank based on entity scores
    ranked_results = sorted(results, key=lambda x: sum(entity_scores.get(ent[0], 0) for ent in query_entities), reverse=True)

    return ranked_results

