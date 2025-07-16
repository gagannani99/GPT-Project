import hashlib
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from embeder import collection, embedding_model

visited = set()

def clean_text(text):
    return ' '.join(text.strip().split())

def extract_visible_text(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Remove unwanted tags
    for tag in soup(["script", "style", "meta", "noscript", "header", "footer", "svg"]):
        tag.decompose()

    return clean_text(soup.get_text())

def crawl_and_embed_site(base_url, max_pages=20):
    to_visit = [base_url]
    chunks_added = 0

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f"❌ Failed to crawl {url}: {e}")
            continue

        text = extract_visible_text(response.text)

        chunks = [text[i:i+512] for i in range(0, len(text), 512)]
        existing_ids = set(collection.get().get("ids", []))

        for chunk in chunks:
            id_hash = hashlib.md5(chunk.encode("utf-8")).hexdigest()
            if id_hash not in existing_ids:
                emb = embedding_model.encode(chunk).tolist()
                collection.add(documents=[chunk], embeddings=[emb], ids=[id_hash])
                chunks_added += 1
                print("🧩 Added chunk:", chunk[:100])

        # Extract internal links to follow
        soup = BeautifulSoup(response.text, "html.parser")
        for link_tag in soup.find_all("a", href=True):
            href = link_tag["href"]
            next_url = urljoin(url, href)
            if urlparse(next_url).netloc == urlparse(base_url).netloc:
                to_visit.append(next_url)

    return chunks_added
