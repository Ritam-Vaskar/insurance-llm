# scripts/embed_and_store.py
import json
import chromadb
import os
from models.huggingface_model import load_embedding_model
from config import VECTOR_DB_DIR, COLLECTION_NAME

def embed_chunks():
    """Embed text chunks and store them in ChromaDB"""
    print("🔄 Starting embedding and storage process...")
    
    # Check if chunks exist
    if not os.path.exists("chunks/chunked_docs.json"):
        print("❌ Error: No chunked documents found!")
        print("Please run document parsing first.")
        return
    
    # Load the embedding model
    print("📥 Loading embedding model...")
    try:
        model = load_embedding_model()
        print(f"✅ Loaded embedding model: {model}")
    except Exception as e:
        print(f"❌ Error loading embedding model: {e}")
        return
    
    # Initialize ChromaDB
    print(f"🗄️  Initializing ChromaDB at: {VECTOR_DB_DIR}")
    os.makedirs(VECTOR_DB_DIR, exist_ok=True)
    
    try:
        client = chromadb.PersistentClient(path=VECTOR_DB_DIR)
        
        # Delete existing collection if it exists (for fresh start)
        try:
            client.delete_collection(COLLECTION_NAME)
            print(f"🗑️  Deleted existing collection: {COLLECTION_NAME}")
        except:
            pass
        
        collection = client.create_collection(COLLECTION_NAME)
        print(f"✅ Created new collection: {COLLECTION_NAME}")
    except Exception as e:
        print(f"❌ Error initializing ChromaDB: {e}")
        return
    
    # Load and process chunks
    with open("chunks/chunked_docs.json", "r", encoding='utf-8') as f:
        docs = json.load(f)
    
    print(f"📊 Processing {len(docs)} text chunks...")
    
    batch_size = 100
    processed = 0
    
    for i in range(0, len(docs), batch_size):
        batch = docs[i:i + batch_size]
        
        try:
            # Prepare batch data
            texts = []
            embeddings = []
            metadatas = []
            ids = []
            
            for chunk in batch:
                # Generate embedding
                embedding = model.encode(chunk["text"])
                
                texts.append(chunk["text"])
                embeddings.append(embedding.tolist())
                metadatas.append({
                    "doc_id": chunk["doc_id"],
                    "index": chunk["index"],
                    "section": chunk.get("section", "N/A"),
                    "clause": chunk.get("clause", "N/A")
                })
                ids.append(f"{chunk['doc_id']}_{chunk['index']}")
            
            # Add batch to collection
            collection.add(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            processed += len(batch)
            print(f"  Processed {processed}/{len(docs)} chunks...")
            
        except Exception as e:
            print(f"❌ Error processing batch {i//batch_size + 1}: {e}")
            continue
    
    print(f"✅ Successfully embedded and stored {processed} text chunks")
    print(f"🗄️  Database location: {VECTOR_DB_DIR}")