import hashlib
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from embeder import collection, embedding_model
from rag_chain import ask_qwen
from scraper import crawl_and_embed_site

app = FastAPI(title="AllianceGPT API")

# CORS 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskRequest(BaseModel):
    question: str

@app.get("/")
def read_root():
    return {"message": "AllianceGPT is live!"}

@app.post("/ask")
def ask_question(data: AskRequest):
    question = data.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Missing question")
    answer = ask_qwen(question)
    return {"answer": answer}

@app.post("/crawl")
def crawl_website():
    url = "https://allianceproit.com/"
    chunks_added = crawl_and_embed_site(url)
    return {"message": f"{chunks_added} new unique chunks added from crawling {url}."}

@app.get("/vectors")
def get_all_vectors():
    try:
        results = collection.get()

        if not results:
            raise HTTPException(status_code=404, detail="No vectors found.")

        documents = results.get("documents")
        ids = results.get("ids")
        embeddings = results.get("embeddings")

        if not isinstance(documents, list) or not isinstance(ids, list) or not isinstance(embeddings, list):
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Invalid result format from collection.get()",
                    "details": {
                        "documents": str(type(documents)),
                        "ids": str(type(ids)),
                        "embeddings": str(type(embeddings))
                    }
                }
            )

        response = []
        for i in range(len(ids)):
            doc = documents[i] if i < len(documents) else None
            emb = embeddings[i] if i < len(embeddings) else None
            if emb is None:
                raise HTTPException(status_code=500, detail=f"Embedding at index {i} is None")
            response.append({
                "id": ids[i],
                "document": doc,
                "embedding_preview": emb[:5],
                "embedding_size": len(emb)
            })

        return {"total": len(response), "vectors": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
