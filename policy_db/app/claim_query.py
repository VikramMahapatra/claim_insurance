import torch
from transformers import BertTokenizer, BertForSequenceClassification
from transformers import pipeline
from fastapi import FastAPI,APIRouter

router = APIRouter()

# Load pre-trained BERT model for intent classification
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=5)  # Assume 5 claim stages

# Define claim stages and corresponding fields
claim_stages = {
    "Initiation": ["policy number", "hospital admission proof", "claim form"],
    "Document Submission": ["medical bills", "prescriptions", "hospital invoices"],
    "Review": ["document verification time", "additional information request"],
    "Approval": ["approval notification", "claim amount", "denial reason"],
    "Reimbursement": ["bank account details", "reimbursement timeline", "payment confirmation"]
}

def classify_intent(user_query):
    inputs = tokenizer(user_query, return_tensors="pt", padding=True, truncation=True)
    outputs = model(**inputs)
    logits = outputs.logits
    predicted_label = torch.argmax(logits, dim=1).item()
    return list(claim_stages.keys())[predicted_label]

# Load LLM for answering queries
qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

knowledge_base = {
    "Initiation": "To initiate a claim, you need to provide policy details and hospital admission proof.",
    "Document Submission": "Submit medical bills, prescriptions, and hospital invoices online or via email.",
    "Review": "The insurer will verify the submitted documents within 7-10 business days.",
    "Approval": "If approved, you will receive an approval notification with the claim amount.",
    "Reimbursement": "Once approved, the reimbursement is processed to your registered bank account."
}

def extract_relevant_field(user_query, stage):
    for field in claim_stages[stage]:
        if field in user_query.lower():
            return field
    return "general"

def answer_query(user_query):
    stage = classify_intent(user_query)
    field = extract_relevant_field(user_query, stage)
    # Use more precise context by incorporating both stage and field details
    context = knowledge_base.get(stage, "I'm not sure. Please contact support.")
    if field != "general":
        context += f" Also, details about {field} are required."
    response = qa_pipeline(question=user_query, context=context)
    return {"stage": stage, "field": field, "response": response['answer']}

@router.post("/query")
def handle_query(query: dict):
    user_query = query.get("question", "")
    return answer_query(user_query)

