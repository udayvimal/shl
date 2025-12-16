import pandas as pd
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# ---------------------------
# Load model, index, catalog
# ---------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("shl_faiss.index")
df_catalog = pd.read_csv("shl_final_data.csv")

# ---------------------------
# Load Test-Set
# ---------------------------
test_df = pd.read_excel("Gen_AI Dataset.xlsx", sheet_name="Test-Set")

submission_rows = []
TOP_K = 10

for _, row in test_df.iterrows():
    query = row["Query"]

    # Embed query
    query_embedding = model.encode([query]).astype("float32")

    # Search FAISS
    distances, indices = index.search(query_embedding, TOP_K * 2)

    seen_urls = set()
    rank = 1

    for idx in indices[0]:
        if idx >= len(df_catalog):
            continue

        url = df_catalog.iloc[int(idx)]["url"]

        # Avoid duplicate URLs per query
        if url in seen_urls:
            continue

        submission_rows.append({
            "Query": query,
            "Rank": rank,
            "Assessment_url": url
        })

        seen_urls.add(url)
        rank += 1

        if rank > TOP_K:
            break

# ---------------------------
# Save final CSV
# ---------------------------
submission_df = pd.DataFrame(submission_rows)
submission_df.to_csv("final_2submission.csv", index=False)

print("✅ FINAL SUBMISSION CSV GENERATED (organized)")
print("File saved as: final_submission.csv")
