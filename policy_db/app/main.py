from fastapi import FastAPI
from app.database import engine, Base
from app.routes import router
# from app.vector_db import router as vector_db_router  # Rename router to avoid conflict
# from app.claim_query import router as claim_query_router  # Rename router

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


app = FastAPI(title="Policy Management API")

# Create tables
Base.metadata.create_all(bind=engine)

# Include routes
app.include_router(router)
# app.include_router(vector_db_router)
# app.include_router(claim_query_router)
