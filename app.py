import streamlit as st
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

# ==================================================
# SHL Assessment Recommender – Streamlit App
# ==================================================
# • Semantic search using FAISS
# • No LLMs (SHL compliant)
# • Duration treated as a soft preference
# • Clickable assessment buttons
# ==================================================

# ---------------------------
# Load resources (cached)
# ---------------------------
@st.cache_resource
def load_resources():
    model = SentenceTransformer("all-MiniLM-L6-v2")
    index = faiss.read_index("shl_faiss.index")
    df = pd.read_csv("shl_final_data.csv")
    return model, index, df

model, index, df_catalog = load_resources()

# ---------------------------
# Helper functions
# ---------------------------
def decode_test_type(code):
    mapping = {
        "A": "Ability",
        "B": "Behavior",
        "C": "Cognitive",
        "K": "Knowledge",
        "P": "Personality",
        "S": "Simulation"
    }
    return ", ".join(mapping.get(c.strip(), c) for c in str(code).split(","))

def format_duration(val):
    if pd.isna(val) or str(val).lower() in ["nan", "n/a", "none"]:
        return "Not specified"
    return str(val)

# ---------------------------
# Page config
# ---------------------------
st.set_page_config(
    page_title="SHL Assessment Recommender - UDAY VIMAL",
    page_icon="🧠",
    layout="wide"
)

# ---------------------------
# UI Header
# ---------------------------
st.title("🧠 SHL Assessment Recommender")
st.caption(
    "Semantic recommendation system for SHL assessments "
    "using FAISS-based similarity search (no LLMs)."
)

st.info(
    "⏱ **Duration constraints are treated as preferences, not strict filters.** "
    "If exact duration data is unavailable, semantic relevance is prioritized "
    "to maintain high recommendation quality."
)

# ---------------------------
# Input section
# ---------------------------
query = st.text_area(
    "📄 Job Description",
    height=160,
    placeholder="e.g. Hiring a customer service executive with strong communication and problem-solving skills..."
)

top_k = st.slider(
    "🔢 Number of recommendations",
    min_value=5,
    max_value=10,
    value=7
)

# ---------------------------
# Recommendation logic
# ---------------------------
if st.button("🔍 Recommend Assessments"):
    if not query.strip():
        st.warning("Please enter a job description.")
    else:
        with st.spinner("Finding best matching SHL assessments..."):
            query_embedding = model.encode([query]).astype("float32")
            distances, indices = index.search(query_embedding, top_k)

        st.subheader("📌 Recommended Assessments")

        for rank, idx in enumerate(indices[0], start=1):
            if idx >= len(df_catalog):
                continue

            row = df_catalog.iloc[int(idx)]

            st.markdown(f"### {rank}. {row['name']}")

            with st.expander("🔎 Load more details"):
                # Clickable button (NOT raw link)
                st.link_button(
                    "🔗 Open Assessment on SHL",
                    row["url"],
                    use_container_width=True
                )

                st.write(f"⏱ **Duration:** {format_duration(row.get('duration'))}")
                st.write(f"🧠 **Test Type:** {decode_test_type(row.get('test_type'))}")
                st.write(f"🌐 **Remote Testing:** {row.get('remote_testing')}")
                st.write(f"📊 **Adaptive / IRT:** {row.get('adaptive_irt')}")

        st.divider()
        st.success("Recommendations generated successfully.")

# ---------------------------
# Footer
# ---------------------------
st.caption(
    "Built by **Uday Vimal** | SHL Assessment Recommendation Task | "
    "Semantic Search • FAISS • Streamlit"
)
