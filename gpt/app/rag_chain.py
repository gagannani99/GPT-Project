import os
import ollama
from embeder import get_context

ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
ollama_client = ollama.Client(host=ollama_host)

def ask_qwen(question):
    context = get_context(question)

    if not context or context.strip() == "":
        return "I'm sorry, I can only assist with questions related to company services and operations."

    prompt = f"""
You are Alliance GPT, an AI assistant designed to provide direct and helpful responses using the given context.

Answer the following question **briefly but clearly**. If the question is unrelated to the context, politely decline to answer.
Remember: if the user greets you, greet them back. Also try to retain context of this session to be helpful in follow-up questions.

Context:
{context}

Question:
{question}
"""

    response = ollama_client.chat(
        model="llama3:8b",
        messages=[{"role": "user", "content": prompt}]
    )

    return response['message']['content']
