import faiss
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

# STEP 1: Load FAISS index
index = faiss.read_index("shl_faiss.index")

# STEP 2: Load assessment metadata
df = pd.read_csv("shl_final_data.csv")

# STEP 3: Load same embedding model used earlier
model = SentenceTransformer("all-MiniLM-L6-v2")

def recommend_assessments(query, top_k=10):
    """
    Takes a job description / query
    Returns top_k relevant SHL assessments
    """

    # Convert query to embedding
    query_embedding = model.encode([query]).astype("float32")

    # Search FAISS index
    distances, indices = index.search(query_embedding, top_k)

    # Collect results
    results = []
    for idx in indices[0]:
        row = df.iloc[idx]
        results.append({
            "name": row["name"],
            "url": row["url"],
            "test_type": row["test_type"],
            "remote_testing": row["remote_testing"],
            "adaptive_irt": row["adaptive_irt"],
            "duration": row["duration"]
        })

    return results


# TEST THE FUNCTION
if __name__ == "__main__":
    test_query = "Need a customer service role with communication and problem solving skills"

    recommendations = recommend_assessments(test_query, top_k=5)

    print("\nTop Recommended Assessments:\n")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['name']}")
        print(f"   URL: {rec['url']}")
        print(f"   Test Type: {rec['test_type']}")
        print(f"   Remote: {rec['remote_testing']} | Adaptive: {rec['adaptive_irt']}")
        print()
