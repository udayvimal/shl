import pandas as pd

# Load scraped data
df = pd.read_csv("shl_assessments.csv")

print("Total rows before cleaning:", len(df))

# OPTIONAL: Remove job solution-like entries
job_keywords = ["solution", "manager solution"]

df = df[~df["name"].str.lower().str.contains("|".join(job_keywords))]

print("Total rows after filtering:", len(df))

# Create combined text for embeddings
df["combined_text"] = (
    "Assessment Name: " + df["name"] +
    ". Test Type: " + df["test_type"] +
    ". Remote Testing: " + df["remote_testing"] +
    ". Adaptive: " + df["adaptive_irt"]
)

# Save prepared file
df.to_csv("shl_assessments_prepared.csv", index=False)

print("✅ Saved shl_assessments_prepared.csv")
