from llm.gemini_client import generate_text


def ask_llm(query, paragraphs):
    context = "\n".join([f"Paragraph {i + 1}: {para}" for i, para in enumerate(paragraphs)])
    prompt = f"""Based on the following insurance policy information, answer this question: {query}

Context:
{context}

Analyze the above context and provide a detailed response including:
1. Direct answer about coverage and conditions
2. Relevant policy details from the context
3. Any important limitations or exclusions
4. References to specific paragraphs that support the answer

Response:"""

    response = generate_text(prompt, temperature=0.2)
    if len(response.split()) < 20:
        response = generate_text(prompt + "\nPlease provide a detailed and complete answer.")
    return response
