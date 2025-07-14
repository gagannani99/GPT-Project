import requests
from bs4 import BeautifulSoup
from googlesearch import search
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_urls(company_name, num=6):
    query = f"{company_name} site:linkedin.com OR site:crunchbase.com OR site:news.ycombinator.com OR site:techcrunch.com OR site:businessinsider.com"
    return list(search(query, num_results=num))

def scrape_text_from_url(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        text = ' '.join([p.text.strip() for p in soup.find_all("p")])
        return text[:3000]  # limit length
    except Exception as e:
        return f"[Error scraping {url}] {str(e)}"

def get_company_data(company_name):
    urls = fetch_urls(company_name)
    print(f"\n🌐 URLs for {company_name}:\n", urls)

    time.sleep(2)  # to avoid being blocked

    contents = []
    for url in urls:
        text = scrape_text_from_url(url)
        if text:
            contents.append(f"🔗 Source: {url}\n{text}")

    return "\n\n---\n\n".join(contents)
 