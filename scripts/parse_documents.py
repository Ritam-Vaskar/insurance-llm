# scripts/parse_documents.py
import os
import json
from unstructured.partition.pdf import partition_pdf
from config import DOCS_DIR

def parse_all():
    """Parse all PDF documents in the docs directory and extract text chunks"""
    print("📄 Starting document parsing...")
    
    if not os.path.exists(DOCS_DIR):
        print(f"❌ Error: Documents directory '{DOCS_DIR}' not found!")
        print(f"Please create the directory and add your PDF files there.")
        return
    
    pdf_files = [f for f in os.listdir(DOCS_DIR) if f.endswith(".pdf")]
    if not pdf_files:
        print(f"❌ Error: No PDF files found in '{DOCS_DIR}'!")
        print(f"Please add your insurance policy PDF files to this directory.")
        return
    
    print(f"Found {len(pdf_files)} PDF files: {pdf_files}")
    
    output = []
    for fname in pdf_files:
        print(f"Processing: {fname}")
        try:
            file_path = os.path.join(DOCS_DIR, fname)
            elements = partition_pdf(file_path)
            
            chunk_count = 0
            for i, el in enumerate(elements):
                if el.text and len(el.text.strip()) > 20:  # Only include meaningful text chunks
                    # Try to extract section info from text if available
                    text = el.text.strip()
                    section = "N/A"
                    clause = "N/A"
                    
                    # Simple heuristics to extract section/clause info
                    lines = text.split('\n')
                    for line in lines[:3]:  # Check first few lines
                        if any(keyword in line.lower() for keyword in ['section', 'clause', 'article']):
                            if 'section' in line.lower():
                                section = line.strip()
                            elif 'clause' in line.lower():
                                clause = line.strip()
                    
                    output.append({
                        "doc_id": fname,
                        "index": i,
                        "text": text,
                        "section": section,
                        "clause": clause
                    })
                    chunk_count += 1
            
            print(f"  Extracted {chunk_count} text chunks from {fname}")
            
        except Exception as e:
            print(f"❌ Error processing {fname}: {e}")
            continue

    if not output:
        print("❌ No text content extracted from any documents!")
        return
    
    # Create output directory
    os.makedirs("chunks", exist_ok=True)
    
    # Save parsed chunks
    with open("chunks/chunked_docs.json", "w", encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Successfully parsed {len(output)} text chunks from {len(pdf_files)} documents")
    print(f"📁 Saved to: chunks/chunked_docs.json")