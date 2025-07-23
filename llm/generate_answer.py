from transformers import pipeline
from config import LLM_MODEL_NAME

def ask_llm(query, paragraphs):
    # Initialize the model with text2text generation pipeline
    generator = pipeline(
        "text2text-generation",
        model=LLM_MODEL_NAME,
        max_length=512,
        do_sample=True,
        top_p=0.95,
        top_k=50
    )
    
    # Construct a clear prompt
    context = "\n".join([f"Paragraph {i+1}: {para}" for i, para in enumerate(paragraphs)])
    prompt = f"""Based on the following insurance policy information, answer this question: {query}

Context:
{context}

Analyze the above context and provide a detailed response including:
1. Direct answer about coverage and conditions
2. Relevant policy details from the context
3. Any important limitations or exclusions
4. References to specific paragraphs that support the answer

Response:"""

    # Generate response
    response = generator(prompt, max_length=512)[0]['generated_text']
    
    # If response is too short, try to generate a more detailed one
    if len(response.split()) < 20:
        prompt += "\nPlease provide a detailed and complete answer."
        response = generator(prompt, max_length=512)[0]['generated_text']
    
    return response
