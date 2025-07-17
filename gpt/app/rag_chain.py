from dotenv import load_dotenv
import os
from openai import AzureOpenAI
from embeder import get_context

# Load environment variables from .env
load_dotenv()

# Initialize OpenAI Azure client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-12-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)

deployment_name = os.getenv("AZURE_DEPLOYMENT_NAME")

def ask_qwen(question: str, selected_options: list = None) -> str:
    context = get_context(question)

    if not context.strip():
        return "I'm sorry, I can only assist with questions related to company services and operations."

    # Begin prompt construction
    prompt = """
You are Alliance GPT, an AI assistant for answering company-related queries concisely and directly based on the provided context.

Instructions:
- Provide **short, precise, and factual** answers.
- **Do not greet** the user unless they greet you first.
- If the question is not related to the context, respond with: "I'm sorry, I can only assist with questions related to company services and operations."
- Do not make assumptions or fabricate names unless explicitly mentioned in the context.
- Answer follow-up questions based on the current context only.
"""

    # Alli mode: include sales intent if present
    if selected_options:
        formatted_options = ", ".join(selected_options)
        prompt += f"\n- The employee has selected the following sales options: {formatted_options}."
        prompt += "\n- Format the answer as a sales pitch, demo script, or lead communication depending on the selected options."

    # Append context and question
    prompt += f"""

Context:
{context}

Question:
{question}
"""

    try:
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Failed to generate response: {str(e)}"
