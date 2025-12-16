import pandas as pd
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from collections import defaultdict

# ---------------------------
# Helper: URL normalization
# ---------------------------
def normalize_url(url):
    """
    Normalize SHL URLs to compare assessment identity
    Handles legacy vs new URL formats
    """
    if not isinstance(url, str):
        return ""
    url = url.lower().strip()
    url = url.split("?")[0]
    url = url.rstrip("/")
    return url.split("/")[-1]  # take slug only


# ---------------------------
# Load model, index, catalog
# ---------------------------
print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

print("Loading FAISS index...")
index = faiss.read_index("shl_faiss.index")

print("Loading SHL catalog data...")
df_catalog = pd.read_csv("shl_final_data.csv")

print(f"Catalog size: {len(df_catalog)}")

# ---------------------------
# Load TRAIN dataset
# ---------------------------
print("Loading Train-Set from Excel...")
train_df = pd.read_excel("Gen_AI Dataset.xlsx", sheet_name="Train-Set")

# Group ground-truth URLs per query
ground_truth = defaultdict(set)

for _, row in train_df.iterrows():
    query = row["Query"]
    url = row["Assessment_url"]
    ground_truth[query].add(url)

print(f"Total training queries: {len(ground_truth)}")

# ---------------------------
# Recall@10 evaluation
# ---------------------------
recall_scores = []

print("\nStarting Recall@10 evaluation...\n")

for query, relevant_urls in ground_truth.items():
    # Embed query
    query_embedding = model.encode([query]).astype("float32")

    # Search FAISS
    distances, indices = index.search(query_embedding, 10)

    # Normalize retrieved URLs
    retrieved_slugs = set()
    for idx in indices[0]:
        if idx < len(df_catalog):
            retrieved_slugs.add(
                normalize_url(df_catalog.iloc[int(idx)]["url"])
            )

    # Normalize ground-truth URLs
    relevant_slugs = {normalize_url(u) for u in relevant_urls}

    # Recall@10 logic
    recall = 1 if len(retrieved_slugs & relevant_slugs) > 0 else 0
    recall_scores.append(recall)

    print("Query:")
    print(query[:200] + ("..." if len(query) > 200 else ""))
    print(f"Recall@10: {recall}")
    print("-" * 70)

# ---------------------------
# Mean Recall@10
# ---------------------------
mean_recall = sum(recall_scores) / len(recall_scores)

print("\n==============================")
print(f"MEAN RECALL@10: {mean_recall:.3f}")
print("==============================")
