from fastapi import FastAPI
from pydantic import BaseModel
import faiss
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

# -------------------------
# Load resources at startup
# -------------------------

app = FastAPI()

print("🔹 Loading FAISS index...")
index = faiss.read_index("shl_faiss.index")

print("🔹 Loading SHL data...")
df = pd.read_csv("shl_final_data.csv")

print("🔹 Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# -------------------------
# Request schema
# -------------------------

class RecommendRequest(BaseModel):
    query: str
    top_k: int = 10

# -------------------------
# Health endpoint (MANDATORY)
# -------------------------

@app.get("/health")
def health():
    return {"status": "healthy"}

# -------------------------
# Recommend endpoint (MANDATORY)
# -------------------------

@app.post("/recommend")
def recommend(req: RecommendRequest):
    # Convert query to embedding
    query_embedding = model.encode([req.query]).astype("float32")

    # FAISS search
    distances, indices = index.search(query_embedding, req.top_k)

    results = []

    for idx in indices[0]:
        # SAFETY CHECK: index bounds
        if idx < 0 or idx >= len(df):
            continue

        row = df.iloc[int(idx)]

        results.append({
            "name": str(row["name"]),
            "url": str(row["url"]),
            "test_type": str(row["test_type"]),
            "remote_testing": str(row["remote_testing"]),
            "adaptive_irt": str(row["adaptive_irt"]),
            "duration": str(row["duration"])
        })

    return {
        "query": str(req.query),
        "recommendations": results
    }

    return {
        "query": req.query,
        "recommendations": results
    }
