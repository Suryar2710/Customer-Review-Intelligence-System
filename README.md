# 🎧 Customer Review Intelligence System (CRIS)

An AI-powered system that analyzes Amazon headphone reviews to extract insights, compare brands, and answer user queries using Retrieval-Augmented Generation (RAG).

---

## Features

- Brand-level analytics (ratings, sentiment, aspects)
- Interactive dashboard with charts (Recharts)
- AI Chat using RAG + LLaMA (via Ollama)
- Aspect-based sentiment analysis (battery, sound, comfort, etc.)
- Competitor comparison insights
- Business recommendations from user reviews
- Brand-specific dropdown filtering

---

## Tech Stack

### Backend
- FastAPI
- Pandas / NumPy
- FAISS (vector similarity search)
- Ollama (LLaMA 3)

### Frontend
- Next.js (React)
- Axios
- Recharts

### Data Processing
- Python (Colab notebooks)
- NLP + Aspect Extraction

---

## 📂 Project Structure


CRIS/
│
├── backend/
│ ├── app.py
│ ├── requirements.txt
│ └── data/
│ ├── brand_df.csv
│ ├── brand_aspect_rating.csv
│ ├── brand_negative_rate.csv
│ ├── competitor_summary_table.csv
│ ├── rag_corpus.csv
│ ├── rag_embeddings.npy
│ ├── rag_index.faiss
│
├── frontend/
│ ├── app/
│ │ ├── page.tsx
│ │ ├── layout.tsx
│ │ └── globals.css
│ ├── package.json
│ └── public/
│
├── Colab Notebooks/
| ├── CRIS
│ ├── 2aspect extraction CRIS.ipynb
│ ├── 3Trend Analysis CRIS.ipynb
│ ├── 4Competitor Analysis CRIS.ipynb
│ ├── 5RecommendationEngine CRIS.ipynb
│ ├── 6RAGPREP CRIS.ipynb
│ └── CRIS.ipynb


---

## ⚙️ Setup Instructions

### 1. Clone Repo

```bash
git clone https://github.com/Suryar2710/Customer-Review-Intelligence-System.git
cd Customer-Review-Intelligence-System
2. Backend Setup
cd backend
pip install -r requirements.txt
uvicorn app:app --reload

Backend runs at:
http://127.0.0.1:8000

3. Install Ollama (Required for AI Chat)

Download:
https://ollama.com

Run:

ollama run llama3
4. Frontend Setup
cd frontend
npm install
npm run dev

Frontend runs at:
http://localhost:3000

Example Queries
"What are the biggest problems with Bose headphones?"
"Is Sony better than Bose?"
"Which brand has best battery life?"
"What issues do users complain about most?"
Dashboard Features
Brand-specific metrics (reviews, rating, products, aspects)
Sentiment distribution (pie chart)
Top aspects (bar chart)
Review trends over time
