"""
search_literature.py — Systematic Literature Search via Semantic Scholar API
Paper #1: Perceive, Plan, Act, Self-Correct

Uses the FREE Semantic Scholar Academic Graph API to:
  - Search for papers on agentic AI, LLM agents, multi-agent systems
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
    "LLM autonomous agents survey",
    "agentic AI architecture framework",
    "multi-agent LLM systems",
    "ReAct reasoning acting language models",
    "Reflexion self-correction language agents",
    "tool use language models function calling",
    "SWE-Bench software engineering benchmark",
    "WebArena web agent benchmark",
    "agent-to-agent protocol communication",
    "model context protocol MCP",
    "LLM agent memory architecture",
    "human-in-the-loop AI agents",
    "tree of thoughts deliberate problem solving",
    "agent benchmark evaluation LLM",
    "plan and execute language model agent",
]

FIELDS = "paperId,title,authors,year,citationCount,venue,publicationDate,openAccessPdf,externalIds"


def search_papers(query, limit=20):
    """Search Semantic Scholar for papers matching query."""
    url = f"{S2_BASE}/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "fields": FIELDS,
        "year": "2022-2025",  # Focus on recent work
    }
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return resp.json().get("data", [])
    except requests.RequestException as e:
        print(f"    Warning: API error for '{query}': {e}")
        return []


def get_paper_details(paper_id):
    """Get detailed info for a specific paper by Semantic Scholar ID."""
    url = f"{S2_BASE}/paper/{paper_id}"
    params = {"fields": FIELDS + ",abstract,references,citations"}
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        print(f"    Warning: API error for paper {paper_id}: {e}")
        return None


def deduplicate(papers):
    """Remove duplicate papers by paperId."""
    seen = set()
    unique = []
    for p in papers:
        pid = p.get("paperId")
        if pid and pid not in seen:
            seen.add(pid)
            unique.append(p)
    return unique


def search_all():
    """Run all search queries and collect results."""
    all_papers = []
    for i, query in enumerate(SEARCH_QUERIES, 1):
        print(f"  [{i}/{len(SEARCH_QUERIES)}] Searching: '{query}'")
        papers = search_papers(query, limit=20)
        all_papers.extend(papers)
        print(f"    Found {len(papers)} results")
        time.sleep(1.1)  # Rate limiting

    unique = deduplicate(all_papers)
    print(f"\n  Total: {len(all_papers)} results, {len(unique)} unique papers")
    return unique


def export_results(papers):
    """Export papers to CSV and JSON."""
    # Sort by citation count descending
    papers.sort(key=lambda p: p.get("citationCount", 0) or 0, reverse=True)

    # CSV export
    csv_path = OUTPUT_DIR / "literature_search_results.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["paper_id", "title", "authors", "year", "citation_count",
                          "venue", "publication_date", "has_pdf", "doi", "arxiv_id"])
        for p in papers:
            authors = "; ".join(a.get("name", "") for a in (p.get("authors") or [])[:5])
            ext_ids = p.get("externalIds") or {}
            writer.writerow([
                p.get("paperId", ""),
                p.get("title", ""),
                authors,
                p.get("year", ""),
                p.get("citationCount", 0),
                p.get("venue", ""),
                p.get("publicationDate", ""),
                "Yes" if p.get("openAccessPdf") else "No",
                ext_ids.get("DOI", ""),
                ext_ids.get("ArXiv", ""),
            ])
    print(f"  Wrote {len(papers)} papers to {csv_path}")

    # JSON export (full data)
    json_path = OUTPUT_DIR / "literature_search_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "search_date": datetime.now().isoformat(),
            "queries": SEARCH_QUERIES,
            "total_unique_papers": len(papers),
            "papers": papers
        }, f, indent=2, default=str)
    print(f"  Wrote full data to {json_path}")

    # Top-cited summary
    print(f"\n  Top 15 most-cited papers:")
    print(f"  {'Citations':>10}  {'Year':>4}  Title")
    print(f"  {'-'*10}  {'-'*4}  {'-'*60}")
    for p in papers[:15]:
        title = (p.get("title") or "")[:60]
        print(f"  {p.get('citationCount', 0):>10}  {p.get('year', ''):>4}  {title}")


# ================================================================
# KEY PAPERS — manually curated must-cite list
# ================================================================
KEY_PAPERS = [
    "649def34f8be52c8b66281af98ae884c09aef38b",  # ReAct
    "2e12d6b6afe4c5dcf3fcb6e3eabc7e0aa12f2e71",  # Reflexion
    # Add Semantic Scholar IDs of key papers as you find them
]


if __name__ == "__main__":
    print("=" * 60)
    print("Systematic Literature Search — Agentic AI")
    print(f"Run date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"API Key: {'Set' if S2_API_KEY else 'Not set (1 req/sec limit)'}")
    print("=" * 60)

    print("\n[1/2] Running search queries...")
    papers = search_all()

    print("\n[2/2] Exporting results...")
    export_results(papers)

    print("\n" + "=" * 60)
    print("DONE.")
    print("\nNext steps:")
    print("  1. Review literature_search_results.csv for relevance")
    print("  2. Add missing key papers to KEY_PAPERS list")
    print("  3. Export selected papers to references.bib (manually or with Zotero)")
    print("  4. Run with S2_API_KEY for higher rate limits:")
    print("     set S2_API_KEY=your_key_here && python search_literature.py")
    print("=" * 60)
