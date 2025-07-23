# Insurance Policy Question Answering System

This project implements a question-answering system for insurance policies using Natural Language Processing and Large Language Models.

## Project Structure

```
insurance-llm/
│
├── data/
│   └── policies/                  # Your input PDF/Word/email files
│       └── policy1.pdf
│
├── chunks/
│   └── chunked_docs.json         # Extracted paragraph-wise chunks
│
├── embeddings/
│   └── chroma/                   # ChromaDB vector store
│
├── models/
│   └── huggingface_model.py      # Load HuggingFace embedding model
│
├── scripts/
│   ├── parse_documents.py        # Extracts paragraphs from PDFs
│   ├── embed_and_store.py        # Generates embeddings & stores in ChromaDB
│   ├── query_pipeline.py         # User query interface + LLM inference
│
├── llm/
│   └── generate_answer.py        # Uses HuggingFace LLM to answer queries
│
├── requirements.txt
├── config.py                     # Settings like model names, db path, etc.
└── README.md
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Place your insurance policy PDFs in the `data/policies/` directory.

3. Process the documents:
```bash
python scripts/parse_documents.py
```

4. Generate embeddings and store in ChromaDB:
```bash
python scripts/embed_and_store.py
```

5. Run the query interface:
```bash
python scripts/query_pipeline.py
```

## Usage

Run the query pipeline and enter your questions about the insurance policies. The system will:
1. Search for relevant passages using semantic similarity
2. Generate a natural language answer using a Large Language Model
3. Provide source passages for reference

## Dependencies

- PyPDF2: PDF parsing
- ChromaDB: Vector storage and similarity search
- Transformers: HuggingFace models for embeddings and LLM
- Torch: Deep learning framework
