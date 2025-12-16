import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# STEP 1: Load cleaned SHL data
df = pd.read_csv("shl_assessments_prepared.csv")
print("Total assessments loaded:", len(df))

# STEP 2: Load embedding model (FREE, LOCAL)
model = SentenceTransformer("all-MiniLM-L6-v2")

# STEP 3: Get text to embed
texts = df["combined_text"].tolist()

print("Creating embeddings...")

# STEP 4: Generate embeddings
embeddings = model.encode(texts, show_progress_bar=True)

# STEP 5: Convert to float32 (FAISS requirement)
embeddings = np.array(embeddings).astype("float32")

# STEP 6: Create FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

# STEP 7: Save FAISS index
faiss.write_index(index, "shl_faiss.index")

# STEP 8: Save final data (metadata)
df.to_csv("shl_final_data.csv", index=False)

print("✅ STEP 6 COMPLETE")
print("FAISS index saved as shl_faiss.index")
print("Final data saved as shl_final_data.csv")
