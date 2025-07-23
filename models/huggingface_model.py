from sentence_transformers import SentenceTransformer
from config import EMBED_MODEL_NAME

def load_embedding_model():
    return SentenceTransformer(EMBED_MODEL_NAME)
