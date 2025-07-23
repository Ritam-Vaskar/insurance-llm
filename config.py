# config.py
EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL_NAME = "google/flan-t5-base"  # Using base model for better response quality
VECTOR_DB_DIR = "embeddings/chroma"
DOCS_DIR = "data/policies"
COLLECTION_NAME = "insurance_docs"  # Consistent collection name across the application
