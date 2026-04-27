# Insurance Policy QA with PageIndex (Vectorless)

This project builds a PageIndex tree for each PDF policy and uses Gemini to traverse the tree and answer questions with reasons. It is fully vectorless (no embeddings or vector DB).

## Project Structure

```
insurance-llm/
│
├── data/
│   └── policies/                  # Input PDF policies
│       └── policy1.pdf
│
├── index_data/
│   ├── pageindex_docs.json         # Maps filename -> doc_id
│   └── pageindex_trees.json        # Cached PageIndex trees
│
├── scripts/
│   ├── pageindex_index.py          # Submit PDFs and fetch PageIndex trees
│   └── pageindex_query.py          # Tree traversal + Gemini reasoning
│
├── llm/
│   └── gemini_client.py            # Gemini API wrapper
│
├── app.py                          # CLI entry point
├── requirements.txt
├── config.py
└── README.md
```

## Setup

1) Install dependencies:
```bash
pip install -r requirements.txt
```

2) Set environment variables (API keys):
```bash
set PAGEINDEX_API_KEY=your_pageindex_key
set GEMINI_API_KEY=your_gemini_key
```

3) Put your PDF policies in `data/policies/`.

4) Run the app:
```bash
python app.py
```

## How it Works

1) PageIndex builds a hierarchical tree for each PDF.
2) Gemini selects relevant nodes by traversing the tree.
3) The system answers with reasons and cites node titles/pages.

## Notes

- PageIndex trees are cached in `index_data/` so re-runs are fast.
- If the document is still processing, the app will poll until the tree is ready.
