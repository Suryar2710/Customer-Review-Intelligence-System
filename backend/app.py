from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import faiss
import ast
import re
import requests
from sentence_transformers import SentenceTransformer

app = FastAPI(
    title="Customer Review Intelligence System",
    description="AI-powered system for analyzing customer reviews, extracting insights, and enabling intelligent product decisions.",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = "data"

df_merged = pd.read_csv(f"{DATA_DIR}/df_merged_full.csv")
pivot = pd.read_csv(f"{DATA_DIR}/brand_aspect_rating.csv", index_col=0)
neg_pivot = pd.read_csv(f"{DATA_DIR}/brand_negative_rate.csv", index_col=0)
summary = pd.read_csv(f"{DATA_DIR}/competitor_summary_table.csv", index_col=0)
business_recs = pd.read_csv(f"{DATA_DIR}/business_recommendations.csv")
pm_summary = pd.read_csv(f"{DATA_DIR}/pm_summary.csv")
corpus_df = pd.read_csv(f"{DATA_DIR}/rag_corpus.csv")

documents = corpus_df["document"].tolist()
metadata = [ast.literal_eval(x) for x in corpus_df["metadata"].tolist()]

index = faiss.read_index(f"{DATA_DIR}/rag_index.faiss")
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


class ChatRequest(BaseModel):
    query: str
    k: int = 3
    model: str = "llama3:latest"


class BrandRequest(BaseModel):
    brand: str


class BrandDashboardRequest(BaseModel):
    brand: str


class CompareRequest(BaseModel):
    brand_1: str
    brand_2: str


def clean_dict(d):
    cleaned = {}
    for k, v in d.items():
        if pd.isna(v):
            cleaned[k] = None
        elif isinstance(v, (np.integer, np.floating)):
            cleaned[k] = float(v)
        else:
            cleaned[k] = v
    return cleaned


def get_matching_brand(brand_input: str, available_brands):
    brand_input = brand_input.strip().lower()
    for brand in available_brands:
        if str(brand).strip().lower() == brand_input:
            return brand
    return None


def retrieve_documents(query: str, k: int = 3):
    query_embedding = embedding_model.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")

    distances, indices = index.search(query_embedding, k * 10)

    seen_reviews = set()
    seen_keys = set()
    results = []

    for rank_idx, idx in enumerate(indices[0]):
        meta = metadata[idx]
        doc = documents[idx]

        review_key = doc.split("Review:")[-1].strip() if "Review:" in doc else doc
        aspect_key = tuple(meta["aspects"]) if "aspects" in meta else meta.get("aspect")
        key = (meta.get("brand"), aspect_key, meta.get("type"))

        if review_key in seen_reviews or key in seen_keys:
            continue

        seen_reviews.add(review_key)
        seen_keys.add(key)

        results.append({
            "rank": len(results) + 1,
            "document": doc,
            "metadata": meta,
            "distance": float(distances[0][rank_idx])
        })

        if len(results) >= k:
            break

    return results


def build_rag_prompt(query: str, k: int = 3):
    retrieved = retrieve_documents(query, k=k)

    context = "\n\n".join(
        [f"[Document {i+1}]\n{item['document']}" for i, item in enumerate(retrieved)]
    )

    prompt = f"""
You are a Customer Review Intelligence Assistant.

Your job is to answer questions using ONLY the provided review-analysis context.

Rules:
- Do not make up facts.
- If the context does not support an answer, say: "The available review data does not provide enough evidence."
- Keep the answer concise and business-focused.
- Use clean bullet points.
- Mention evidence from the retrieved reviews when useful.

User Question:
{query}

Retrieved Context:
{context}

Write the answer in this format:

Summary:
- One short overall answer.

Key Evidence:
- Bullet point 1
- Bullet point 2
- Bullet point 3

Product Team Recommendation:
- One practical recommendation based on the evidence.
"""
    return prompt, retrieved


def ask_ollama_chat(prompt: str, model: str = "llama3:latest"):
    url = "http://localhost:11434/api/chat"

    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a clean UI-ready assistant. "
                    "Format answers clearly using bullet points and proper spacing."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = requests.post(url, json=payload, timeout=300)
    response.raise_for_status()

    answer = response.json()["message"]["content"]
    answer = answer.replace("\\n", "\n")
    answer = answer.replace("Summary:", "\nSummary:\n")
    answer = answer.replace("Key Evidence:", "\nKey Evidence:\n")
    answer = answer.replace("Product Team Recommendation:", "\nProduct Team Recommendation:\n")

    return answer.strip()


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/brands")
def get_brands():
    brands = summary.index.tolist()
    return {
        "brands": sorted(brands)
    }


@app.get("/dashboard")
def dashboard():
    sentiment_counts = df_merged["sentiment_label"].value_counts(normalize=True).to_dict()

    top_aspects = (
        df_merged.groupby("aspects")["rating"]
        .mean()
        .sort_values(ascending=False)
        .head(5)
        .to_dict()
    )

    review_volume = (
        df_merged.groupby("review_month")
        .size()
        .sort_index()
        .tail(6)
        .to_dict()
    )

    common_issues = (
        df_merged[df_merged["rating"] <= 2]["aspects"]
        .value_counts()
        .head(5)
        .to_dict()
    )

    return {
        "scope": "global",
        "total_reviews": int(len(df_merged)),
        "average_rating": float(round(df_merged["rating"].mean(), 2)),
        "total_brands": int(df_merged["store"].nunique()),
        "total_products": int(df_merged["parent_asin"].nunique()),
        "total_aspects": int(df_merged["aspects"].nunique()),
        "sentiment_overview": clean_dict(sentiment_counts),
        "top_aspects": clean_dict(top_aspects),
        "review_volume": clean_dict(review_volume),
        "common_issues": clean_dict(common_issues)
    }


@app.post("/brand-dashboard")
def brand_dashboard(req: BrandDashboardRequest):
    available_brands = df_merged["store"].dropna().astype(str).str.strip().unique().tolist()
    matched_brand = get_matching_brand(req.brand, available_brands)

    if matched_brand is None:
        return {
            "brand": req.brand,
            "error": "Brand not found"
        }

    brand_df = df_merged[df_merged["store"].astype(str).str.strip() == matched_brand].copy()

    sentiment_counts = (
        brand_df["sentiment_label"]
        .value_counts(normalize=True)
        .to_dict()
    )

    top_aspects = (
        brand_df.groupby("aspects")["rating"]
        .mean()
        .sort_values(ascending=False)
        .head(5)
        .to_dict()
    )

    review_volume = (
        brand_df.groupby("review_month")
        .size()
        .sort_index()
        .tail(6)
        .to_dict()
    )

    common_issues = (
        brand_df[brand_df["rating"] <= 2]["aspects"]
        .value_counts()
        .head(5)
        .to_dict()
    )

    pm_text = None
    pm_temp = pm_summary.copy()
    pm_temp["brand_lower"] = pm_temp["brand"].astype(str).str.strip().str.lower()
    pm_match = pm_temp[pm_temp["brand_lower"] == matched_brand.lower()]
    if len(pm_match) > 0:
        pm_text = pm_match.iloc[0]["pm_summary"]

    return {
        "scope": "brand",
        "brand": matched_brand,
        "total_reviews": int(len(brand_df)),
        "average_rating": float(round(brand_df["rating"].mean(), 2)),
        "total_products": int(brand_df["parent_asin"].nunique()),
        "total_aspects": int(brand_df["aspects"].nunique()),
        "sentiment_overview": clean_dict(sentiment_counts),
        "top_aspects": clean_dict(top_aspects),
        "review_volume": clean_dict(review_volume),
        "common_issues": clean_dict(common_issues),
        "pm_summary": pm_text
    }


@app.post("/brand-summary")
def brand_summary(req: BrandRequest):
    brand = req.brand.strip().lower()

    df_temp = pm_summary.copy()
    df_temp["brand"] = df_temp["brand"].str.lower()

    result = df_temp[df_temp["brand"] == brand]

    if result.empty:
        return {
            "brand": req.brand,
            "summary": "No data found for this brand"
        }

    return {
        "brand": req.brand,
        "summary": result.iloc[0]["pm_summary"]
    }


@app.post("/compare")
def compare_brands(req: CompareRequest):
    result = {}

    for brand in [req.brand_1, req.brand_2]:
        matched_brand = None

        for existing_brand in summary.index:
            if existing_brand.lower() == brand.strip().lower():
                matched_brand = existing_brand
                break

        if matched_brand is None:
            result[brand] = {"error": "Brand not found"}
            continue

        result[matched_brand] = {
            "summary": clean_dict(summary.loc[matched_brand].to_dict()),
            "aspect_scores": clean_dict(pivot.loc[matched_brand].to_dict()) if matched_brand in pivot.index else {},
            "negative_rates": clean_dict(neg_pivot.loc[matched_brand].to_dict()) if matched_brand in neg_pivot.index else {}
        }

    return result


@app.post("/chat")
def chat(req: ChatRequest):
    prompt, retrieved = build_rag_prompt(req.query, k=req.k)
    answer = ask_ollama_chat(prompt, model=req.model)

    answer = answer.replace("\\n", "\n")
    answer = re.sub(r"\n{2,}", "\n\n", answer).strip()

    summary_text = answer
    key_evidence = ""
    recommendation = ""

    if "Key Evidence:" in answer:
        summary_text = answer.split("Key Evidence:")[0].replace("Summary:", "").strip()
        rest = answer.split("Key Evidence:")[1]

        if "Product Team Recommendation:" in rest:
            key_evidence = rest.split("Product Team Recommendation:")[0].strip()
            recommendation = rest.split("Product Team Recommendation:")[1].strip()
        else:
            key_evidence = rest.strip()

    return {
        "query": req.query,
        "summary": summary_text,
        "key_evidence": key_evidence,
        "recommendation": recommendation,
        "answer_raw": answer,
        "retrieved": retrieved
    }