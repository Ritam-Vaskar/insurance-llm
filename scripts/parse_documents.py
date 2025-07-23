# scripts/parse_documents.py

import os, json
from unstructured.partition.pdf import partition_pdf
from config import DOCS_DIR

def parse_all():
    output = []
    for fname in os.listdir(DOCS_DIR):
        if fname.endswith(".pdf"):
            elements = partition_pdf(os.path.join(DOCS_DIR, fname))
            for i, el in enumerate(elements):
                if el.text:
                    output.append({
                        "doc_id": fname,
                        "index": i,
                        "text": el.text.strip()
                    })

    os.makedirs("chunks", exist_ok=True)
    with open("chunks/chunked_docs.json", "w") as f:
        json.dump(output, f, indent=2)
