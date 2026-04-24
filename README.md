# Customer Review Intelligence System (CRIS)

AI-powered platform to analyze Amazon headphone reviews using NLP, RAG, and interactive dashboards.

---

## Overview

The Customer Review Intelligence System (CRIS) transforms raw customer reviews into actionable insights.

It combines:
- Data analytics
- NLP and aspect extraction
- Retrieval-Augmented Generation (RAG)

to help users:
- Understand product issues
- Compare brands
- Make informed decisions

---

## Key Highlights

- AI Chat (RAG-based)  
  Ask natural language questions and receive evidence-backed answers

- Brand Analytics Dashboard  
  Ratings, sentiment, trends, and aspect-level insights

- Aspect-Based Analysis  
  Battery, sound, comfort, ANC, build quality

- Trend and Sentiment Visualization  
  Interactive charts powered by real review data

- Business Insights Engine  
  Converts user reviews into product improvement recommendations

---

## System Architecture


User → Frontend (Next.js)
→ Backend (FastAPI)
→ Data Layer (CSV + FAISS Index)
→ LLM (LLaMA via Ollama)
→ Response (RAG + Analytics)


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

### Data and NLP
- Python (Colab notebooks)
- NLP and Aspect Extraction
- Sentiment Analysis

---

## Dashboard Capabilities

- Brand-level metrics:
  - Total reviews
  - Average rating
  - Number of products
  - Aspects tracked

- Visual insights:
  - Sentiment distribution (pie chart)
  - Top aspects (bar chart)
  - Review trends over time

---

## AI Chat (RAG)

Example queries:


What are the biggest problems with Bose headphones?
Is Sony better than Bose?
Which brand has best battery life?


The system:
1. Retrieves relevant review chunks using FAISS
2. Passes context to the language model
3. Generates structured responses including:
   - Summary
   - Key evidence
   - Recommendation

---

## Project Structure


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
│ ├── df_exploded.csv
│ ├── df_merged_full.csv
│ ├── negative_brand_reviews.csv
│ ├── pm_summary.csv
│ ├── rag_corpus.csv
│ ├── rag_embeddings.npy
│ ├── rag_index.faiss
│ └── rag_test_queries.csv
│
├── frontend/
│ ├── app/
│ │ ├── page.tsx
│ │ ├── layout.tsx
│ │ └── globals.css
│ ├── package.json
│ ├── tsconfig.json
│ └── public/
│
├── Colab Notebooks/
│ ├── aspect extraction
│ ├── trend analysis
│ ├── competitor analysis
│ ├── recommendation engine
│ └── RAG prep


---

## Setup Instructions

### 1. Clone Repository

```bash
git clone https://github.com/Suryar2710/Customer-Review-Intelligence-System.git
cd Customer-Review-Intelligence-System
2. Backend Setup
cd backend
pip install -r requirements.txt
uvicorn app:app --reload

Backend runs at:
http://127.0.0.1:8000

3. Install Ollama (for AI Chat)

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
``` 

## Use Cases

Product research
Market analysis
Competitive benchmarking
Customer experience insights


## Future Improvements
Cloud deployment (Vercel and Render)
Replace Ollama with hosted LLM
Real-time streaming responses
UI upgrade
