import os
import ollama
from embeder import get_context
from utils.scraper import get_company_data

# Set up the Ollama client
ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
ollama_client = ollama.Client(host=ollama_host)

# Update with your actual company name (case-insensitive match)
YOUR_COMPANY_NAME = "Alliance Solutions"

def ask_qwen(question):
    lower_q = question.lower()

    # Case 1: Question is about your own company
    if YOUR_COMPANY_NAME.lower() in lower_q or "your company" in lower_q or "about your services" in lower_q:
        print("📂 Using internal document context (ChromaDB)")
        local_context = get_context(question)
        if not local_context.strip():
            return "I'm sorry, I couldn't find details in our internal documents."

        prompt = f"""
You are Alliance GPT, an internal AI assistant.

Answer the following question based ONLY on the internal documentation:

Context:
{local_context}

Question:
{question}

Instructions:
- Be factual, short, and concise.
- Do not guess if the info is not in context.
"""
        response = ollama_client.chat(
            model="llama3:8b",
            messages=[{"role": "user", "content": prompt}]
        )
        return response['message']['content']

    # Case 2: Question about a collaboration/project with other companies
    else:
        print("🌐 Using web scraping for collaboration/project info")
        scraped_info = get_company_data(question)

        if not scraped_info.strip():
            return "Sorry, I couldn't find any public information about that collaboration."

        prompt = f"""
You are Alliance GPT, an AI assistant.

Answer the question based on public web data provided below:

Context:
{scraped_info}

Question:
{question}

Instructions:
- Be specific about the collaboration or project.
- Mention technologies, timelines, company names if available.
- If no relevant data, say you couldn’t find anything concrete.
"""
        response = ollama_client.chat(
            model="llama3:8b",
            messages=[{"role": "user", "content": prompt}]
        )
        return response['message']['content']
