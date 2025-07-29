# scripts/query_pipeline.py
import json
import chromadb
import os
from models.huggingface_model import load_embedding_model
from config import VECTOR_DB_DIR, COLLECTION_NAME
from llm.generate_answer import ask_llm

def query_system(user_query):
    """Query the insurance document system"""
    try:
        # Check if database exists
        if not os.path.exists(VECTOR_DB_DIR):
            print(f"\n❌ Error: Vector database not found at {VECTOR_DB_DIR}")
            print("Please run document processing and embedding steps first.")
            return
        
        # Initialize ChromaDB client
        client = chromadb.PersistentClient(path=VECTOR_DB_DIR)
        
        try:
            collection = client.get_collection(COLLECTION_NAME)
        except Exception as e:
            print(f"\n❌ Error: Collection '{COLLECTION_NAME}' not found.")
            print("Please run document processing and embedding steps first.")
            return
        
        # Load embedding model and create query embedding
        print("\n🔍 Searching relevant policy sections...")
        model = load_embedding_model()
        embedding = model.encode(user_query)

        # Get results with metadata
        results = collection.query(
            query_embeddings=[embedding.tolist()],
            n_results=5,
            include=["metadatas", "documents", "distances"]
        )

        if not results['documents'][0]:
            print("❌ No relevant documents found for your query.")
            return

        top_paragraphs = results['documents'][0]
        metadata = results['metadatas'][0]
        distances = results['distances'][0]

        print("\n📋 Retrieved Context:")
        for i, (para, meta, dist) in enumerate(zip(top_paragraphs, metadata, distances), 1):
            print(f"\n[{i}] From {meta.get('doc_id', 'Unknown Document')} (Relevance: {1-dist:.3f})")
            print(f"Section: {meta.get('section', 'N/A')}")
            print(f"Clause: {meta.get('clause', 'N/A')}")
            print(f"Text: {para[:200]}{'...' if len(para) > 200 else ''}")

            

        print("\n🤖 Analyzing with Groq LLM...")
        response = ask_llm(user_query, top_paragraphs, metadata)
        
        try:
            # Parse and display the structured response
            response_dict = json.loads(response)
            
            print("\n" + "="*60)
            print("📋 INSURANCE POLICY ANALYSIS RESULTS")
            print("="*60)
            
            print(f"\n🎯 Final Decision: {response_dict.get('final_answer', 'N/A')}")
            print(f"🎯 Confidence Level: {response_dict.get('confidence', 'N/A')}")
            
            print(f"\n📝 Reasoning:")
            print(f"   {response_dict.get('reasoning', 'N/A')}")
            
            if response_dict.get('payout_amount') and response_dict['payout_amount'] != 'N/A':
                print(f"\n💰 Payout Amount: {response_dict['payout_amount']}")
            
            if response_dict.get('waiting_periods') and response_dict['waiting_periods'] != 'N/A':
                print(f"\n⏱️  Waiting Periods: {response_dict['waiting_periods']}")
            
            if response_dict.get('conditions'):
                conditions = response_dict['conditions']
                if isinstance(conditions, list) and conditions:
                    print(f"\n✅ Conditions to Meet:")
                    for condition in conditions:
                        print(f"   • {condition}")
                elif isinstance(conditions, str) and conditions != 'N/A':
                    print(f"\n✅ Conditions: {conditions}")
            
            if response_dict.get('limitations'):
                limitations = response_dict['limitations']
                if isinstance(limitations, list) and limitations:
                    print(f"\n⚠️  Policy Limitations:")
                    for limitation in limitations:
                        print(f"   • {limitation}")
                elif isinstance(limitations, str) and limitations != 'N/A':
                    print(f"\n⚠️  Limitations: {limitations}")
            
            if response_dict.get('recommendations') and response_dict['recommendations'] != 'N/A':
                print(f"\n💡 Recommendations:")
                print(f"   {response_dict['recommendations']}")
            
            print(f"\n📚 Supporting Evidence:")
            supporting_paras = response_dict.get('supporting_paragraphs', [])
            if supporting_paras:
                for i, para in enumerate(supporting_paras, 1):
                    print(f"\n   [{i}] Document: {para.get('doc_id', 'N/A')}")
                    print(f"       Section: {para.get('section', 'N/A')}")
                    print(f"       Quote: \"{para.get('text', 'N/A')[:300]}{'...' if len(para.get('text', '')) > 300 else ''}\"")
            else:
                print("   No specific supporting paragraphs identified.")
            
            # Show audit information
            audit_log = response_dict.get('audit_log', {})
            print(f"\n🔍 Analysis Details:")
            print(f"   Generated by: {audit_log.get('generated_by', 'N/A')}")
            print(f"   Model: {audit_log.get('model_name', 'N/A')}")
            print(f"   Timestamp: {response_dict.get('query', {}).get('timestamp', 'N/A')}")
            
            print("\n" + "="*60)
            
        except json.JSONDecodeError:
            print("\n❌ Error: Could not parse the structured response")
            print("Raw Response:")
            print(response)
            
    except Exception as e:
        print(f"\n❌ Error during query processing: {e}")
        import traceback
        traceback.print_exc()