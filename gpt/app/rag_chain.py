import re
from app.azure_openai import chat_with_azure
from app.scraper import get_company_data

YOUR_COMPANY_NAME = "Alliance Pro"

def is_company_name_only(query: str) -> bool:
    return (
        len(query.strip().split()) <= 4
        and not re.search(r"\b(who|what|how|should|can|will|when|where|does|is|are)\b", query, re.IGNORECASE)
    )

def extract_target_company(question):
    match = re.search(r"(?:to|with|about|for)\s+([A-Z][\w\s&\-]+)", question, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def ask_qwen(question, role="customer"):
    question = question.strip()

    # ✅ EMPLOYEE ONLY: If question looks like just a company name
    if role == "employee" and is_company_name_only(question):
        scraped_text = get_company_data(question)

        if not scraped_text.strip():
            return {
                "answer": f"❌ Couldn’t find enough public data for '{question}'."
            }

        prompt = f"""
You are Alliance GPT, an assistant for Alliance Pro employees.

Summarize the company '{question}' in 5-6 concise and informative lines using only the context below.

Context:
{scraped_text}
"""
        answer = chat_with_azure(prompt)
        return {"answer": answer}

    # ✅ CUSTOMER FLOW
    if role == "customer":
        scraped_text = get_company_data(YOUR_COMPANY_NAME)

        if not scraped_text.strip():
            return {
                "answer": "❌ Couldn't find enough information about Alliance Pro.",
            }

        prompt = f"""
You are Alliance GPT, a chatbot for Alliance Pro.

Use the context below to answer the user's question in a short, friendly, and informative manner.

Context:
{scraped_text}

Question:
{question}
"""
        answer = chat_with_azure(prompt)
        return {
            "answer": answer
        }

    # ✅ EMPLOYEE FLOW (Collaboration-style queries)
    else:
        target_company = extract_target_company(question)

        if not target_company:
            return {
                "error": "❌ Could not detect the other company in your query. Please mention a company name clearly."
            }

        scraped_text = get_company_data(target_company)

        if not scraped_text.strip():
            return {
                "error": f"❌ No sufficient public data found for '{target_company}'."
            }

        def run_prompt(task_description):
            prompt = f"""
You are Alliance GPT, an assistant for Alliance Pro employees.

Your task: {task_description}

Use only the following context (scraped data about {target_company}) to complete your response:

Context:
{scraped_text}
"""
            return chat_with_azure(prompt)

        return {
            "employee_special_output": {
                "about": run_prompt(f"Summarize {target_company} in 5-6 lines."),
                "email": run_prompt(f"Write a follow-up email proposing how Alliance Pro's services can help {target_company}."),
                "pitch": run_prompt(f"Write a short phone pitch to convince {target_company} to explore a partnership.")
            }
        }
