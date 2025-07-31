# llm/generate_answer.py
import json
from datetime import datetime
from groq import Groq
from config import GROQ_MODEL, GROQ_API_KEY, EMBED_MODEL_NAME
import os

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
def ask_llm(query, paragraphs, doc_metadata=None):
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not set in environment variables")
    
    # Initialize Groq client
    client = Groq(api_key='GROQ_API_KEY')
    
    # Format paragraphs with metadata
    context_texts = []
    for i, para in enumerate(paragraphs[:5]):  # Using top 5 paragraphs
        doc_id = doc_metadata[i]['doc_id'] if doc_metadata else 'Unknown'
        section = doc_metadata[i].get('section', 'N/A') if doc_metadata else 'N/A'
        clause = doc_metadata[i].get('clause', 'N/A') if doc_metadata else 'N/A'
        context_texts.append(f"[{i+1}] Source: {doc_id} (Section {section}, Clause {clause})\nText: {para}")
    
    context = "\n\n".join(context_texts)
    
    system_prompt = """You are an expert insurance policy analyzer. Analyze queries and provide accurate responses based on policy documents.

Key requirements:
1. Always respond with valid JSON only - no additional text before or after
2. Include specific quotes from policy documents
3. Be precise about waiting periods and conditions
4. Provide confidence levels based on available information
5. Format numbers and dates consistently
6. Use only the provided policy excerpts for your analysis"""
    
    user_prompt = f"""Analyze this insurance query based on the provided policy excerpts:

QUERY: {query}

POLICY EXCERPTS:
{context}

Provide your analysis as a JSON object with this exact structure:
{{
    "final_answer": "Approved/Rejected/Partial/Needs More Info",
    "confidence": "High/Medium/Low",
    "reasoning": "Detailed explanation of the decision based on policy excerpts",
    "supporting_paragraphs": [
        {{
            "index": 1,
            "doc_id": "document_name.pdf",
            "text": "exact quote from the policy text",
            "section": "section reference if available"
        }}
    ],
    "limitations": ["list of relevant limitations found in policy"],
    "waiting_periods": "applicable waiting periods mentioned in policy",
    "payout_amount": "coverage amount if specified in policy",
    "conditions": ["specific conditions that must be met"],
    "recommendations": "suggestions for the policyholder based on policy terms"
}}

Important: Return ONLY the JSON object, no other text."""

    try:
        # Call Groq API
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=2048,
            top_p=0.9
        )
        
        # Extract the response
        response_text = response.choices[0].message.content.strip()
        
        # Clean up the response to ensure it starts and ends with JSON braces
        if not response_text.startswith('{'):
            # Find the first opening brace
            start_idx = response_text.find('{')
            if start_idx != -1:
                response_text = response_text[start_idx:]
        
        if not response_text.endswith('}'):
            # Find the last closing brace
            end_idx = response_text.rfind('}')
            if end_idx != -1:
                response_text = response_text[:end_idx + 1]
        
        # Try to parse as JSON to ensure valid structure
        response_json = json.loads(response_text)
        
        # Add metadata
        response_json["query"] = {
            "text": query,
            "language": "en",
            "timestamp": datetime.now().isoformat()
        }
        
        response_json["audit_log"] = {
            "generated_by": "Groq",
            "model_name": GROQ_MODEL,
            "retrieval_method": "ChromaDB (Top-5 vector matches)",
            "embedding_model": EMBED_MODEL_NAME,
            "execution_time_ms": None
        }
        
        return json.dumps(response_json, indent=2)
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Raw response: {response_text}")
        
        # Fallback response structure
        fallback_response = {
            "final_answer": "Needs Review",
            "confidence": "Low",
            "reasoning": "Could not parse LLM response properly. Raw response included for manual review.",
            "supporting_paragraphs": [],
            "limitations": ["Response parsing failed"],
            "waiting_periods": "N/A",
            "payout_amount": "N/A",
            "conditions": ["Manual review required"],
            "recommendations": "Please review the raw response manually",
            "error": "JSON parsing failed",
            "raw_response": response_text,
            "query": {
                "text": query,
                "language": "en",
                "timestamp": datetime.now().isoformat()
            },
            "audit_log": {
                "generated_by": "Groq",
                "model_name": GROQ_MODEL,
                "retrieval_method": "ChromaDB (Top-5 vector matches)",
                "embedding_model": EMBED_MODEL_NAME,
                "execution_time_ms": None
            }
        }
        return json.dumps(fallback_response, indent=2)
    
    except Exception as e:
        print(f"API call error: {e}")
        
        # Error response structure
        error_response = {
            "final_answer": "Error",
            "confidence": "Low",
            "reasoning": f"API call failed: {str(e)}",
            "supporting_paragraphs": [],
            "limitations": ["API error occurred"],
            "waiting_periods": "N/A",
            "payout_amount": "N/A",
            "conditions": ["System error - please try again"],
            "recommendations": "Please try your query again",
            "error": str(e),
            "query": {
                "text": query,
                "language": "en",
                "timestamp": datetime.now().isoformat()
            },
            "audit_log": {
                "generated_by": "Groq",
                "model_name": GROQ_MODEL,
                "retrieval_method": "ChromaDB (Top-5 vector matches)",
                "embedding_model": EMBED_MODEL_NAME,
                "execution_time_ms": None
            }
        }
        return json.dumps(error_response, indent=2)