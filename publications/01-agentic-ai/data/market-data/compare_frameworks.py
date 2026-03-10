"""
compare_frameworks.py — Agentic AI Framework Comparison via GitHub API
Paper #1: Perceive, Plan, Act, Self-Correct

Collects PUBLIC GitHub metrics for 15+ agentic AI frameworks:
  - Stars, forks, open issues, contributors, last commit
  - License, language, creation date
  - Exports to CSV for the paper's Section 4 (8-Layer Stack)

GitHub API: https://docs.github.com/en/rest (free, 60 req/hr unauthenticated)
For higher limits: set GITHUB_TOKEN env var (free personal access token)

Usage:
    pip install requests pandas
    python compare_frameworks.py
"""

import os
import json
import csv
import time
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("Install requests: pip install requests")
    raise

OUTPUT_DIR = Path(__file__).parent
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
HEADERS = {"Accept": "application/vnd.github+json"}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"

# ================================================================
# FRAMEWORKS TO COMPARE (Layer 2: Orchestration & Runtime)
# ================================================================
ORCHESTRATION_FRAMEWORKS = [
    # (owner/repo, display_name, category)
    ("langchain-ai/langgraph", "LangGraph", "Orchestration"),
    ("openai/openai-agents-python", "OpenAI Agents SDK", "Orchestration"),
    ("google/adk-python", "Google ADK", "Orchestration"),
    ("crewAIInc/crewAI", "CrewAI", "Multi-Agent"),
    ("microsoft/autogen", "AutoGen", "Multi-Agent"),
    ("microsoft/semantic-kernel", "Semantic Kernel", "Orchestration"),
    ("langchain-ai/langchain", "LangChain", "Foundation"),
    ("huggingface/smolagents", "Smolagents", "Orchestration"),
    ("pydantic/pydantic-ai", "Pydantic AI", "Orchestration"),
]

# Layer 3: Memory
MEMORY_TOOLS = [
    ("mem0ai/mem0", "Mem0", "Memory"),
    ("getzep/zep", "Zep", "Memory"),
    ("letta-ai/letta", "Letta (MemGPT)", "Memory"),
]

# Layer 4: Tool Integration
TOOL_INFRA = [
    ("tavily-ai/tavily-python", "Tavily", "Search Tool"),
    ("e2b-dev/e2b", "E2B", "Code Execution"),
    ("browser-use/browser-use", "Browser Use", "Browser Tool"),
    ("Skyvern-AI/skyvern", "Skyvern", "Browser Tool"),
    ("composiohq/composio", "Composio", "Integration"),
]

# Layer 8: Observability
OBSERVABILITY = [
    ("langfuse/langfuse", "Langfuse", "Observability"),
    ("Arize-ai/phoenix", "Arize Phoenix", "Observability"),
]

# Benchmarks (for reference)
BENCHMARKS = [
    ("princeton-nlp/SWE-bench", "SWE-Bench", "Benchmark"),
    ("web-arena-x/webarena", "WebArena", "Benchmark"),
    ("THUDM/AgentBench", "AgentBench", "Benchmark"),
    ("xlang-ai/OSWorld", "OSWorld", "Benchmark"),
]

ALL_REPOS = ORCHESTRATION_FRAMEWORKS + MEMORY_TOOLS + TOOL_INFRA + OBSERVABILITY + BENCHMARKS


def get_repo_info(owner_repo):
    """Fetch repository information from GitHub API."""
    url = f"https://api.github.com/repos/{owner_repo}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code == 403:
            print(f"    Rate limited. Set GITHUB_TOKEN for higher limits.")
            return None
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        print(f"    Warning: API error for {owner_repo}: {e}")
        return None


def collect_all():
    """Collect GitHub metrics for all repositories."""
    results = []
    rate_delay = 1.0 if not GITHUB_TOKEN else 0.3

    for i, (repo, name, category) in enumerate(ALL_REPOS, 1):
        print(f"  [{i}/{len(ALL_REPOS)}] Fetching: {repo}")
        info = get_repo_info(repo)
        if info:
            results.append({
                "name": name,
                "repo": repo,
                "category": category,
                "stars": info.get("stargazers_count", 0),
                "forks": info.get("forks_count", 0),
                "open_issues": info.get("open_issues_count", 0),
                "language": info.get("language", ""),
                "license": (info.get("license") or {}).get("spdx_id", ""),
                "created_at": info.get("created_at", "")[:10],
                "updated_at": info.get("pushed_at", "")[:10],
                "description": (info.get("description") or "")[:100],
                "url": info.get("html_url", ""),
            })
        time.sleep(rate_delay)

    return results


def export_results(results):
    """Export to CSV and JSON."""
    results.sort(key=lambda r: r["stars"], reverse=True)

    # CSV
    csv_path = OUTPUT_DIR / "framework_comparison.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "name", "repo", "category", "stars", "forks", "open_issues",
            "language", "license", "created_at", "updated_at", "description", "url"
        ])
        writer.writeheader()
        writer.writerows(results)
    print(f"  Wrote {len(results)} repos to {csv_path}")

    # JSON
    json_path = OUTPUT_DIR / "framework_comparison.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "collection_date": datetime.now().isoformat(),
            "total_repos": len(results),
            "repos": results
        }, f, indent=2)
    print(f"  Wrote full data to {json_path}")

    # Summary table
    print(f"\n  {'Name':<25} {'Category':<15} {'Stars':>8} {'Forks':>7} {'License':<12}")
    print(f"  {'-'*25} {'-'*15} {'-'*8} {'-'*7} {'-'*12}")
    for r in results:
        print(f"  {r['name']:<25} {r['category']:<15} {r['stars']:>8,} {r['forks']:>7,} {r['license']:<12}")


if __name__ == "__main__":
    print("=" * 60)
    print("Agentic AI Framework Comparison — GitHub Metrics")
    print(f"Run date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"GitHub Token: {'Set' if GITHUB_TOKEN else 'Not set (60 req/hr limit)'}")
    print("=" * 60)

    print(f"\nCollecting data for {len(ALL_REPOS)} repositories...")
    results = collect_all()

    print("\nExporting results...")
    export_results(results)

    print("\n" + "=" * 60)
    print("DONE.")
    print("\nNext steps:")
    print("  1. Review framework_comparison.csv")
    print("  2. Update paper.tex Section 4 (8-Layer Stack) with fresh numbers")
    print("  3. For higher API limits: set GITHUB_TOKEN=ghp_xxx")
    print("=" * 60)
