"""
search_literature.py — Systematic Literature Search via Semantic Scholar API
Paper #2: Causal Inference at Scale

Uses the FREE Semantic Scholar Academic Graph API to:
  - Search for papers on analytical AI, causal inference, NL2SQL, data observability
  - Retrieve citation counts, publication venues, years
  - Export structured data for the Background & Related Work section

API Docs: https://api.semanticscholar.org/api-docs/
Rate Limit: 1 request/second (unauthenticated), 10 req/sec (with free API key)
API Key:   https://www.semanticscholar.org/product/api#api-key-form (free)

Usage:
    pip install requests pandas
    python search_literature.py
    # Optional: set S2_API_KEY env var for higher rate limits
"""

import os
import json
import csv
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

try:
    import requests
except ImportError:
    print("Install requests: pip install requests")
    raise

OUTPUT_DIR = Path(__file__).parent
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

S2_BASE = "https://api.semanticscholar.org/graph/v1"
S2_API_KEY = os.environ.get("S2_API_KEY", "")

HEADERS = {}
if S2_API_KEY:
    HEADERS["x-api-key"] = S2_API_KEY

# Search queries covering the paper's scope
SEARCH_QUERIES = [
    # Causal inference
    "causal inference machine learning survey",
    "structural causal models Pearl do-calculus",
    "DoWhy causal inference Python",
    "CausalML uplift modelling treatment effects",
    "CausalImpact Bayesian time series",
    "difference-in-differences causal estimation",
    "propensity score matching causal",
    "synthetic control method causal",
    # Business intelligence & analytics
    "business intelligence analytics survey",
    "augmented analytics AI-powered insights",
    "self-service BI data democratisation",
    "data warehouse dimensional modelling Kimball",
    # NL2SQL / natural language querying
    "NL2SQL text-to-SQL large language models",
    "Spider benchmark text-to-SQL evaluation",
    "BIRD-SQL benchmark database grounding",
    "natural language interface database",
    # Data observability & quality
    "data observability monitoring anomaly detection",
    "data quality management DAMA-DMBOK",
    "data lineage governance metadata",
    "data mesh distributed architecture",
    # Clustering & analytical techniques
    "HDBSCAN density clustering",
    "anomaly detection time series KPI",
    "SHAP feature importance explainability",
    # Process mining
    "process mining conformance checking",
]

FIELDS = "paperId,title,authors,year,citationCount,venue,publicationDate,openAccessPdf,externalIds"


def search_papers(query, limit=20):
    """Search Semantic Scholar for papers matching query."""
    url = f"{S2_BASE}/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "fields": FIELDS,
        "year": "2018-2026",  # Broader window for foundational causal inference work
    }
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return resp.json().get("data", [])
    except requests.RequestException as e:
        print(f"    Warning: API error for '{query}': {e}")
        return []


def flatten_paper(paper):
    """Flatten a Semantic Scholar paper record into a dict."""
    authors = paper.get("authors", [])
    first_author = authors[0].get("name", "") if authors else ""
    n_authors = len(authors)
    pdf_url = ""
    oa = paper.get("openAccessPdf")
    if oa and isinstance(oa, dict):
        pdf_url = oa.get("url", "")
    ext = paper.get("externalIds", {}) or {}
    doi = ext.get("DOI", "")
    arxiv = ext.get("ArXiv", "")

    return {
        "paperId": paper.get("paperId", ""),
        "title": paper.get("title", ""),
        "firstAuthor": first_author,
        "nAuthors": n_authors,
        "year": paper.get("year", ""),
        "venue": paper.get("venue", ""),
        "citationCount": paper.get("citationCount", 0),
        "doi": doi,
        "arxiv": arxiv,
        "pdfUrl": pdf_url,
        "publicationDate": paper.get("publicationDate", ""),
    }


def run_all_searches():
    """Run all search queries and collect unique papers."""
    all_papers = {}
    for i, query in enumerate(SEARCH_QUERIES, 1):
        print(f"  [{i}/{len(SEARCH_QUERIES)}] Searching: '{query}'")
        results = search_papers(query)
        for paper in results:
            pid = paper.get("paperId", "")
            if pid and pid not in all_papers:
                all_papers[pid] = flatten_paper(paper)
        time.sleep(1.1)  # respect rate limit
    return list(all_papers.values())


def save_results(papers):
    """Save collected papers to CSV and JSON."""
    if not papers:
        print("  No papers collected (API may be unreachable).")
        return

    # Sort by citation count descending
    papers.sort(key=lambda p: p.get("citationCount", 0), reverse=True)

    # CSV
    csv_path = OUTPUT_DIR / "literature_search_results.csv"
    keys = papers[0].keys()
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(papers)
    print(f"  Wrote {len(papers)} papers to {csv_path}")

    # JSON
    json_path = OUTPUT_DIR / "literature_search_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(papers, f, indent=2, ensure_ascii=False)
    print(f"  Wrote {len(papers)} papers to {json_path}")

    # Summary stats
    total_citations = sum(p.get("citationCount", 0) for p in papers)
    years = [p.get("year") for p in papers if p.get("year")]
    venues = set(p.get("venue") for p in papers if p.get("venue"))
    print(f"\n  Summary:")
    print(f"    Total unique papers: {len(papers)}")
    print(f"    Total citations:     {total_citations:,}")
    print(f"    Year range:          {min(years) if years else 'N/A'} — {max(years) if years else 'N/A'}")
    print(f"    Unique venues:       {len(venues)}")


# ================================================================
# MAIN
# ================================================================
if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"Analytical AI Literature Search")
    print(f"Paper #2: Causal Inference at Scale")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Output: {OUTPUT_DIR}")
    print(f"{'='*60}\n")

    print("Running Semantic Scholar searches...")
    papers = run_all_searches()
    save_results(papers)

    print(f"\nDone.")
