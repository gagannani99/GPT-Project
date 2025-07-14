import os
import ollama
from embeder import get_context

# Set up the Ollama client
ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
ollama_client = ollama.Client(host=ollama_host)

def ask_qwen(question):
    context = get_context(question)

    # If no relevant context is found
    if not context or context.strip() == "":
        return "I'm sorry, I can only assist with questions related to company services and operations."

    # Refined system prompt for short, direct answers
    prompt = f"""
You are Alliance GPT, an AI assistant for answering company-related queries concisely and directly based on the provided context.

Instructions:
- Provide **short, precise, and factual** answers.
- **Do not greet** the user unless they greet you first.
- If the question is not related to the context, respond with: "I'm sorry, I can only assist with questions related to company services and operations."
- Do not make assumptions or fabricate names unless explicitly mentioned in the context.
- Answer follow-up questions based on the current context only.

Context:
{context}

Question:
{question}
"""

    # Call the Ollama model
    response = ollama_client.chat(
        model="llama3:8b",
        messages=[{"role": "user", "content": prompt}]
    )

    return response['message']['content']
