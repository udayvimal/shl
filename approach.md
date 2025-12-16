# SHL Assessment Recommendation System – Technical Approach

## 1. Problem Understanding

Recruiters typically describe job roles using free-form natural language, while SHL’s assessment catalog is structured and static.
The objective of this task is to bridge this gap by recommending the most relevant SHL assessments for a given job description using semantic similarity.

Key constraints provided by SHL:
- No chatbot or generative LLM usage
- Semantic recommendation approach
- Evaluation using Recall@10
- API-based solution with reproducible results

---

## 2. Data Collection

SHL Individual Assessments were scraped from the official SHL product catalog.
Only **Individual Tests** were retained, as instructed.
The scraped catalog was cached locally to ensure reproducibility and avoid dependence on live website availability.

Fields captured:
- Assessment name
- Assessment URL
- Test type
- Remote testing availability
- Adaptive / IRT availability

---

## 3. Text Representation

Each assessment was converted into a structured textual representation by combining:
- Assessment name
- Test type
- Delivery attributes (remote testing, adaptive/IRT)

This representation allows semantic comparison with recruiter queries while keeping the approach simple and interpretable.

---

## 4. Embedding Generation

Semantic embeddings were generated using the `all-MiniLM-L6-v2` SentenceTransformer model.

Reasons for choosing this model:
- Lightweight and fast
- Strong semantic performance
- CPU-friendly
- Suitable for production systems

All embeddings were generated deterministically and cached.

---

## 5. Vector Indexing (FAISS)

A FAISS index was built over the assessment embeddings to enable efficient similarity search.
FAISS allows fast nearest-neighbor search even for larger catalogs and is widely used in production recommendation systems.

---

## 6. Recommendation Logic

For a given recruiter query:
1. The query is converted into an embedding
2. FAISS retrieves the top-K most similar assessments
3. Results are ranked by semantic similarity

This approach ensures:
- Low latency
- Deterministic output
- No dependency on LLM APIs

---

## 7. API Layer (FastAPI)

The recommendation logic is exposed via a FastAPI backend.

Available endpoints:
- `/health` – health check
- `/recommend` – returns top-K recommended assessments

FastAPI was chosen for:
- Automatic API documentation (Swagger UI)
- Ease of integration with ATS or HR systems
- Clean request/response validation

---

## 8. Web Application (Streamlit)

A Streamlit web interface was built to allow recruiters to interactively:
- Enter job descriptions
- Select Top-K results
- Explore recommended assessments

The web app uses the same backend logic as the API and is intended for demonstration and usability testing.

---

## 9. Evaluation Methodology

Evaluation was conducted using the **Train-Set** provided in `Gen_AI Dataset.xlsx`.

Metric used:
- **Recall@10**

Recall@10 measures whether at least one ground-truth assessment appears within the top 10 recommendations.

---

## 10. Results

- Total evaluation queries: 10
- Mean Recall@10: **0.70**

This indicates that the system successfully retrieves relevant assessments for most recruiter queries.

---

## 11. Final Submission

The final submission file (`final_submission.csv`) was generated using the Test-Set queries.
Each query is paired with the top 10 recommended SHL assessment URLs, as required.

---

## 12. Design Philosophy

The solution intentionally avoids unnecessary complexity and focuses on:
- Simplicity
- Reproducibility
- SHL compliance
- Real-world applicability

This mirrors how recommendation systems are commonly built and evaluated in production HR technology platforms.
