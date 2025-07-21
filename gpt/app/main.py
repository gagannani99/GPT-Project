import hashlib
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.embeder import collection, embedding_model
from app.rag_chain import ask_qwen

app = FastAPI(title="AllianceGPT API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can replace * with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic request model
class AskRequest(BaseModel):
    question: str
    role: str = "customer"  # Optional field with default

@app.get("/")
def read_root():
    return {"message": "AllianceGPT is live!"}

# ✅ Updated /ask endpoint
@app.post("/ask")
def ask_question(data: AskRequest):
    question = data.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Missing question")

    role = data.role.lower() if data.role else "customer"
    result = ask_qwen(question, role=role)

    return result

# ✅ File upload to embed .txt documents
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are supported")

    try:
        content = await file.read()
        content = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Unsupported file encoding")

    chunks = [content[i:i + 512] for i in range(0, len(content), 512)]
    existing_ids = set(collection.get().get("ids", []))

    new_chunks = 0
    for chunk in chunks:
        id_hash = hashlib.md5(chunk.encode("utf-8")).hexdigest()
        if id_hash not in existing_ids:
            print("\n🧩 New Chunk Preview:", chunk[:200])
            emb = embedding_model.encode(chunk).tolist()
            collection.add(documents=[chunk], embeddings=[emb], ids=[id_hash])
            new_chunks += 1

    return {"message": f"{new_chunks} new unique chunks added from {file.filename}."}

# ✅ Check current embeddings
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
