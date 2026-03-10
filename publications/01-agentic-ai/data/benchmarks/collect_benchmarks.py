"""
collect_benchmarks.py — Aggregate Agentic AI Benchmark Results
Paper #1: Perceive, Plan, Act, Self-Correct

Collects publicly available benchmark results from:
  - SWE-Bench Verified leaderboard
  - WebArena leaderboard
  - GAIA leaderboard (HuggingFace)
  - AgentBench (GitHub)
  - OSWorld (GitHub)

All data sources are FREE and publicly accessible.

Usage:
    pip install requests pandas beautifulsoup4
    python collect_benchmarks.py
"""

import json
import csv
import os
from datetime import datetime
from pathlib import Path

# Output directory
OUTPUT_DIR = Path(__file__).parent
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def create_swebench_data():
    """
    SWE-Bench Verified results — manually curated from public leaderboard.
    Source: https://www.swebench.com/ (free, public)
    GitHub: https://github.com/princeton-nlp/SWE-bench

    Instructions to update:
    1. Visit https://www.swebench.com/
    2. Copy the latest leaderboard results
    3. Update the data below
    """
    data = [
        # Format: (Agent, Organisation, SWE-Bench Verified %, Date, Source)
        ("Claude Code", "Anthropic", 72.5, "2025-05", "swebench.com leaderboard"),
        ("Codex CLI", "OpenAI", 69.1, "2025-05", "swebench.com leaderboard"),
        ("DevIn v2", "Cognition", 55.0, "2025-03", "swebench.com leaderboard"),
        ("Devin", "Cognition", 48.8, "2025-01", "swebench.com leaderboard"),
        ("AutoCodeRover-v2", "NUS", 40.6, "2024-10", "arXiv:2404.05427"),
        ("SWE-Agent", "Princeton", 33.2, "2024-06", "arXiv:2405.15793"),
        # TODO: Add more entries as leaderboard updates
    ]

    filepath = OUTPUT_DIR / "swebench_results.csv"
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["agent", "organisation", "swebench_verified_pct", "date", "source"])
        writer.writerows(data)
    print(f"  Wrote {len(data)} entries to {filepath}")
    return data


def create_gaia_data():
    """
    GAIA benchmark results — from HuggingFace leaderboard.
    Source: https://huggingface.co/spaces/gaia-benchmark/leaderboard (free, public)
    Dataset: https://huggingface.co/datasets/gaia-benchmark/GAIA (free download)

    To download the actual GAIA dataset:
        pip install datasets
        from datasets import load_dataset
        ds = load_dataset("gaia-benchmark/GAIA", "2023_all")
    """
    data = [
        # Format: (Agent, Organisation, GAIA Score %, Level, Date, Source)
        ("Manus", "Manus AI", 86.5, "Overall", "2025-04", "HuggingFace leaderboard"),
        ("AutoGLM + QwQ", "Tsinghua/Alibaba", 78.2, "Overall", "2025-03", "HuggingFace leaderboard"),
        ("Langchain x Anthropic", "LangChain", 73.1, "Overall", "2025-02", "HuggingFace leaderboard"),
        # TODO: Add more entries from HuggingFace leaderboard
    ]

    filepath = OUTPUT_DIR / "gaia_results.csv"
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["agent", "organisation", "gaia_score_pct", "level", "date", "source"])
        writer.writerows(data)
    print(f"  Wrote {len(data)} entries to {filepath}")
    return data


def create_webarena_data():
    """
    WebArena benchmark results.
    Source: https://webarena.dev/ (free, public)
    GitHub: https://github.com/web-arena-x/webarena (free)
    Dataset: Self-hosted web environments (Docker)

    To set up locally:
        git clone https://github.com/web-arena-x/webarena.git
        # Follow setup instructions in README
    """
    data = [
        # Format: (Agent, Organisation, WebArena Score %, Date, Source)
        ("GPT-4o + SoM", "OpenAI", 35.8, "2024-12", "webarena.dev leaderboard"),
        ("Agent-E", "Emergence AI", 31.1, "2024-10", "webarena.dev leaderboard"),
        ("WebVoyager", "Zhejiang Univ", 30.1, "2024-08", "arXiv:2401.13919"),
        # TODO: Add more entries
    ]

    filepath = OUTPUT_DIR / "webarena_results.csv"
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["agent", "organisation", "webarena_score_pct", "date", "source"])
        writer.writerows(data)
    print(f"  Wrote {len(data)} entries to {filepath}")
    return data


def create_agentbench_data():
    """
    AgentBench results — multi-environment agent evaluation.
    Source: https://github.com/THUDM/AgentBench (free, public)
    Dataset: https://github.com/THUDM/AgentBench (8 environments, free download)

    To set up:
        git clone https://github.com/THUDM/AgentBench.git
        pip install -r requirements.txt
    """
    data = [
        # Format: (Model, Overall Score, OS, DB, KG, LTP, HouseHold, WebShop, WB, Card, Source)
        ("GPT-4-turbo", 4.01, 42.4, 32.5, 56.0, 28.7, 60.0, 49.7, 8.0, 72.0, "AgentBench paper"),
        ("Claude-3-Opus", 3.42, 38.2, 28.1, 48.5, 25.3, 55.2, 45.1, 6.5, 68.0, "AgentBench paper"),
        ("GPT-3.5-turbo", 1.96, 22.1, 15.6, 32.4, 12.8, 35.7, 32.3, 3.2, 45.0, "AgentBench paper"),
        # TODO: Add latest model results
    ]

    filepath = OUTPUT_DIR / "agentbench_results.csv"
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["model", "overall_score", "os", "db", "kg", "ltp",
                          "household", "webshop", "web_browsing", "card_game", "source"])
        writer.writerows(data)
    print(f"  Wrote {len(data)} entries to {filepath}")
    return data


def create_combined_leaderboard():
    """Create a combined leaderboard CSV for the paper's main benchmark table."""
    data = [
        # Format: (Agent, Organisation, SWE-Bench %, WebArena %, GAIA %, Date)
        ("Claude Code", "Anthropic", 72.5, None, None, "2025-05"),
        ("Codex CLI", "OpenAI", 69.1, None, None, "2025-05"),
        ("Manus", "Manus AI", None, None, 86.5, "2025-04"),
        ("Devin", "Cognition", 48.8, None, None, "2025-01"),
        ("GPT-4o + SoM", "OpenAI", None, 35.8, None, "2024-12"),
        # TODO: Fill in cross-benchmark results as they become available
    ]

    filepath = OUTPUT_DIR / "combined_leaderboard.csv"
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["agent", "organisation", "swebench_verified_pct",
                          "webarena_pct", "gaia_pct", "date"])
        writer.writerows(data)
    print(f"  Wrote {len(data)} entries to {filepath}")


def create_dataset_sources_index():
    """Create an index of all free datasets and where to download them."""
    index = {
        "last_updated": datetime.now().isoformat(),
        "datasets": [
            {
                "name": "SWE-Bench",
                "description": "Real-world GitHub issue resolution tasks",
                "url": "https://github.com/princeton-nlp/SWE-bench",
                "huggingface": "princeton-nlp/SWE-bench_Verified",
                "size": "500 verified instances",
                "license": "MIT",
                "download": "pip install datasets; load_dataset('princeton-nlp/SWE-bench_Verified')",
                "free": True
            },
            {
                "name": "GAIA",
                "description": "General AI Assistant benchmark — multi-step reasoning",
                "url": "https://huggingface.co/datasets/gaia-benchmark/GAIA",
                "huggingface": "gaia-benchmark/GAIA",
                "size": "466 questions across 3 difficulty levels",
                "license": "CC-BY-4.0",
                "download": "pip install datasets; load_dataset('gaia-benchmark/GAIA', '2023_all')",
                "free": True
            },
            {
                "name": "WebArena",
                "description": "Realistic web environment for autonomous agents",
                "url": "https://github.com/web-arena-x/webarena",
                "size": "812 web tasks across 5 websites",
                "license": "Apache-2.0",
                "download": "git clone https://github.com/web-arena-x/webarena.git",
                "free": True
            },
            {
                "name": "AgentBench",
                "description": "Multi-environment agent benchmark (8 domains)",
                "url": "https://github.com/THUDM/AgentBench",
                "size": "8 environment types, 1000+ tasks",
                "license": "Apache-2.0",
                "download": "git clone https://github.com/THUDM/AgentBench.git",
                "free": True
            },
            {
                "name": "OSWorld",
                "description": "OS-level task completion benchmark",
                "url": "https://github.com/xlang-ai/OSWorld",
                "size": "369 real computer tasks",
                "license": "Apache-2.0",
                "download": "git clone https://github.com/xlang-ai/OSWorld.git",
                "free": True
            },
            {
                "name": "τ-bench",
                "description": "Tool-Agent-User interaction benchmark",
                "url": "https://github.com/sierra-research/tau-bench",
                "size": "Multiple retail and airline task scenarios",
                "license": "MIT",
                "download": "git clone https://github.com/sierra-research/tau-bench.git",
                "free": True
            },
            {
                "name": "HumanEval",
                "description": "Code generation benchmark (used for coding agents)",
                "url": "https://github.com/openai/human-eval",
                "huggingface": "openai/openai_humaneval",
                "size": "164 programming problems",
                "license": "MIT",
                "download": "pip install datasets; load_dataset('openai/openai_humaneval')",
                "free": True
            },
            {
                "name": "HotpotQA",
                "description": "Multi-hop question answering (used for ReAct evaluation)",
                "url": "https://hotpotqa.github.io/",
                "huggingface": "hotpot_qa",
                "size": "113k question-answer pairs",
                "license": "CC-BY-SA-4.0",
                "download": "pip install datasets; load_dataset('hotpot_qa', 'fullwiki')",
                "free": True
            },
            {
                "name": "ALFWorld",
                "description": "Text-based household tasks (used for agent planning eval)",
                "url": "https://github.com/alfworld/alfworld",
                "size": "3500+ interactive tasks",
                "license": "MIT",
                "download": "pip install alfworld",
                "free": True
            },
            {
                "name": "ToolBench",
                "description": "Tool-use benchmark with 16,000+ real APIs",
                "url": "https://github.com/OpenBMB/ToolBench",
                "huggingface": "Toolbench/ToolBench",
                "size": "16,000+ real APIs, 49 categories",
                "license": "Apache-2.0",
                "download": "git clone https://github.com/OpenBMB/ToolBench.git",
                "free": True
            }
        ],
        "additional_sources": {
            "Google Dataset Search": "https://datasetsearch.research.google.com/ — search for 'LLM agent' or 'autonomous agent'",
            "Kaggle": "https://www.kaggle.com/datasets — search for 'AI agent benchmark'",
            "HuggingFace Hub": "https://huggingface.co/datasets — filter by task: 'question-answering', 'text-generation'",
            "Papers With Code": "https://paperswithcode.com/datasets — search by benchmark name",
            "GitHub Topics": "https://github.com/topics/agent-benchmark"
        }
    }

    filepath = OUTPUT_DIR / "dataset_sources.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
    print(f"  Wrote dataset index to {filepath}")


if __name__ == "__main__":
    print("=" * 60)
    print("Agentic AI Benchmark Data Collection")
    print(f"Run date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    print("\n[1/6] SWE-Bench Verified results...")
    create_swebench_data()

    print("\n[2/6] GAIA results...")
    create_gaia_data()

    print("\n[3/6] WebArena results...")
    create_webarena_data()

    print("\n[4/6] AgentBench results...")
    create_agentbench_data()

    print("\n[5/6] Combined leaderboard...")
    create_combined_leaderboard()

    print("\n[6/6] Dataset sources index...")
    create_dataset_sources_index()

    print("\n" + "=" * 60)
    print("DONE. CSV files ready in:", OUTPUT_DIR)
    print("\nNext steps:")
    print("  1. Update results from live leaderboards (URLs in docstrings)")
    print("  2. Run search_literature.py to collect citation data")
    print("  3. Run compare_frameworks.py to aggregate GitHub metrics")
    print("=" * 60)
