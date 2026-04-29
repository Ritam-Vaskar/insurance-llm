# scripts/parse_documents.py

import os, json
import fitz  # PyMuPDF
from config import DOCS_DIR

def parse_documents(input_dir):
    output = []
    for fname in os.listdir(input_dir):
        if fname.endswith(".pdf"):
            doc_path = os.path.join(input_dir, fname)
            try:
                doc = fitz.open(doc_path)
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    text = page.get_text().strip()
                    if text:
                        output.append({
                            "doc_id": fname,
                            "page_num": page_num + 1,
                            "text": text
                        })
                doc.close()
            except Exception as e:
                print(f"Error reading {fname}: {e}")

    os.makedirs("chunks", exist_ok=True)
    with open("chunks/chunked_docs.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
