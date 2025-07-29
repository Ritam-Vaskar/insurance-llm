# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Model Settings
EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
GROQ_MODEL = "llama3-8b-8192"  # Groq's Llama model
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")  # Set your Groq API key in environment variables

# Directory Settings
VECTOR_DB_DIR = "embeddings/chroma"
DOCS_DIR = "data/policies"
COLLECTION_NAME = "insurance_docs"