"""
compare_platforms.py — Analytical AI Platform Comparison via GitHub API
Paper #2: Causal Inference at Scale

Collects PUBLIC GitHub metrics for analytical AI tools and platforms:
  - Stars, forks, open issues, contributors, last commit
  - License, language, creation date
  - Exports to CSV for the paper's Section 4 (8-Layer Stack)

GitHub API: https://docs.github.com/en/rest (free, 60 req/hr unauthenticated)
For higher limits: set GITHUB_TOKEN env var (free personal access token)

Usage:
    pip install requests pandas
    python compare_platforms.py
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
# TOOLS BY LAYER (Layer → owner/repo, display_name, category)
# ================================================================

# Layer 1: Data Sources & Ingestion
INGESTION_TOOLS = [
    ("airbytehq/airbyte", "Airbyte", "L1-Ingestion"),
    ("apache/kafka", "Apache Kafka", "L1-Ingestion"),
    ("debezium/debezium", "Debezium", "L1-CDC"),
    ("apache/flink", "Apache Flink", "L1-Streaming"),
    ("meltano/meltano", "Meltano", "L1-EL"),
]

# Layer 2: Data Integration & Storage (open-source components)
INTEGRATION_TOOLS = [
    ("dbt-labs/dbt-core", "dbt Core", "L2-Transform"),
    ("apache/spark", "Apache Spark", "L2-Processing"),
    ("delta-io/delta", "Delta Lake", "L2-Storage"),
    ("apache/iceberg", "Apache Iceberg", "L2-Storage"),
    ("apache/hudi", "Apache Hudi", "L2-Storage"),
    ("trinodb/trino", "Trino", "L2-Query Engine"),
    ("ClickHouse/ClickHouse", "ClickHouse", "L2-OLAP"),
    ("apache/druid", "Apache Druid", "L2-OLAP"),
]

# Layer 3: Semantic & Metric Layer
SEMANTIC_TOOLS = [
    ("cube-js/cube", "Cube.dev", "L3-Semantic"),
]

# Layer 4: Analytical Engine
ANALYTICS_TOOLS = [
    ("scikit-learn/scikit-learn", "scikit-learn", "L4-ML"),
    ("pandas-dev/pandas", "pandas", "L4-DataFrames"),
    ("yzhao062/pyod", "PyOD", "L4-Anomaly"),
    ("statsmodels/statsmodels", "statsmodels", "L4-Stats"),
    ("scipy/scipy", "SciPy", "L4-Scientific"),
]

# Layer 5: NLQ / NL2SQL
NLQ_TOOLS = [
    ("vanna-ai/vanna", "Vanna.ai", "L5-NL2SQL"),
]

# Layer 6: Causal & Diagnostic AI
CAUSAL_TOOLS = [
    ("py-why/dowhy", "DoWhy", "L6-Causal"),
    ("uber/causalml", "CausalML", "L6-Causal"),
    ("py-why/EconML", "EconML", "L6-Causal"),
    ("microsoft/causica", "Causica", "L6-Causal"),
    ("google/CausalImpact", "CausalImpact (R)", "L6-Causal"),
    ("jakobrunge/tigramite", "Tigramite", "L6-Causal"),
]

# Layer 7: Visualisation & Reporting
VIZ_TOOLS = [
    ("apache/superset", "Apache Superset", "L7-Viz"),
    ("metabase/metabase", "Metabase", "L7-Viz"),
    ("grafana/grafana", "Grafana", "L7-Viz"),
    ("getredash/redash", "Redash", "L7-Viz"),
    ("lightdash/lightdash", "Lightdash", "L7-Viz"),
]

# Layer 8: Governance, Lineage & Access
GOVERNANCE_TOOLS = [
    ("great-expectations/great_expectations", "Great Expectations", "L8-Quality"),
    ("sodadata/soda-core", "Soda Core", "L8-Quality"),
    ("datahub-project/datahub", "DataHub", "L8-Catalog"),
    ("OpenLineage/OpenLineage", "OpenLineage", "L8-Lineage"),
    ("MarquezProject/marquez", "Marquez", "L8-Lineage"),
    ("amundsen-io/amundsen", "Amundsen", "L8-Catalog"),
]

ALL_TOOLS = (
    INGESTION_TOOLS + INTEGRATION_TOOLS + SEMANTIC_TOOLS +
    ANALYTICS_TOOLS + NLQ_TOOLS + CAUSAL_TOOLS +
    VIZ_TOOLS + GOVERNANCE_TOOLS
)


def fetch_repo(owner_repo):
    """Fetch repository metadata from GitHub API."""
    url = f"https://api.github.com/repos/{owner_repo}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code == 403:
            print(f"    Rate limited. Set GITHUB_TOKEN for higher limits.")
            return None
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        print(f"    Warning: {owner_repo}: {e}")
        return None


def extract_metrics(repo_json, display_name, category):
    """Extract key metrics from GitHub API response."""
    return {
        "name": display_name,
        "category": category,
        "full_name": repo_json.get("full_name", ""),
        "stars": repo_json.get("stargazers_count", 0),
        "forks": repo_json.get("forks_count", 0),
        "open_issues": repo_json.get("open_issues_count", 0),
        "language": repo_json.get("language", ""),
        "license": (repo_json.get("license") or {}).get("spdx_id", ""),
        "created": repo_json.get("created_at", "")[:10],
        "updated": repo_json.get("pushed_at", "")[:10],
        "description": (repo_json.get("description") or "")[:120],
    }


def collect_all():
    """Fetch metrics for all tools."""
    results = []
    for i, (owner_repo, name, category) in enumerate(ALL_TOOLS, 1):
        print(f"  [{i}/{len(ALL_TOOLS)}] {name} ({owner_repo})")
        data = fetch_repo(owner_repo)
        if data:
            results.append(extract_metrics(data, name, category))
        time.sleep(0.8)  # stay within rate limits
    return results


def save_results(results):
    """Save to CSV and JSON."""
    if not results:
        print("  No results collected.")
        return

    results.sort(key=lambda r: r.get("stars", 0), reverse=True)

    csv_path = OUTPUT_DIR / "platform_comparison.csv"
    keys = results[0].keys()
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)
    print(f"  Wrote {len(results)} tools to {csv_path}")

    json_path = OUTPUT_DIR / "platform_comparison.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"  Wrote {len(results)} tools to {json_path}")


# ================================================================
# MAIN
# ================================================================
if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"Analytical AI Platform Comparison")
    print(f"Paper #2: Causal Inference at Scale")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Output: {OUTPUT_DIR}")
    print(f"{'='*60}\n")

    print("Fetching GitHub metrics...")
    results = collect_all()
    save_results(results)

    print(f"\nDone.")
