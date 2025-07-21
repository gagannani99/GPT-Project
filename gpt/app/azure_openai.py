import os
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials from .env
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")  # e.g., "gpt-4o"

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version="2023-07-01-preview",  # Use the latest available version
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

# Chat function
def chat_with_azure(prompt: str) -> str:
    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT_NAME,  # Use the deployment name here
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    return response.choices[0].message.content
