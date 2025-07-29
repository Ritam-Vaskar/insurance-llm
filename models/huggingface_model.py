from sentence_transformers import SentenceTransformer
from config import EMBED_MODEL_NAME

def load_embedding_model():
    """Load and return the sentence transformer model for embeddings"""
    return SentenceTransformer(EMBED_MODEL_NAME)