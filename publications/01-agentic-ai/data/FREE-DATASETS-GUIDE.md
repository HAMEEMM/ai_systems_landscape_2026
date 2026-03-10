# Free Datasets & Data Sources Guide
## Paper #1: Perceive, Plan, Act, Self-Correct

All datasets listed here are **free** and **publicly accessible**.

---

## 1. Agent Benchmarks (Direct Download)

| Dataset | Size | Download | License |
|---------|------|----------|---------|
| **SWE-Bench Verified** | 500 tasks | `pip install datasets` → `load_dataset("princeton-nlp/SWE-bench_Verified")` | MIT |
| **SWE-Bench Lite** | 300 tasks | `load_dataset("princeton-nlp/SWE-bench_Lite")` | MIT |
| **GAIA** | 466 questions | `load_dataset("gaia-benchmark/GAIA", "2023_all")` | CC-BY-4.0 |
| **WebArena** | 812 tasks | `git clone https://github.com/web-arena-x/webarena` | Apache-2.0 |
| **AgentBench** | 8 envs, 1000+ tasks | `git clone https://github.com/THUDM/AgentBench` | Apache-2.0 |
| **OSWorld** | 369 tasks | `git clone https://github.com/xlang-ai/OSWorld` | Apache-2.0 |
| **τ-bench** | Retail + airline | `git clone https://github.com/sierra-research/tau-bench` | MIT |
| **HumanEval** | 164 problems | `load_dataset("openai/openai_humaneval")` | MIT |
| **HotpotQA** | 113k QA pairs | `load_dataset("hotpot_qa", "fullwiki")` | CC-BY-SA-4.0 |
| **ALFWorld** | 3500+ tasks | `pip install alfworld` | MIT |
| **ToolBench** | 16,000+ APIs | `git clone https://github.com/OpenBMB/ToolBench` | Apache-2.0 |

### Quick Start
```bash
pip install datasets
python -c "
from datasets import load_dataset
# SWE-Bench
swe = load_dataset('princeton-nlp/SWE-bench_Verified')
print(f'SWE-Bench Verified: {len(swe[\"test\"])} tasks')

# GAIA
gaia = load_dataset('gaia-benchmark/GAIA', '2023_all')
print(f'GAIA: {sum(len(gaia[s]) for s in gaia)} questions')
"
```

---

## 2. Leaderboards (Scrape or Manual Copy)

| Leaderboard | URL | What it provides |
|-------------|-----|------------------|
| SWE-Bench | https://www.swebench.com/ | Agent scores on software engineering tasks |
| GAIA | https://huggingface.co/spaces/gaia-benchmark/leaderboard | Multi-step reasoning scores |
| WebArena | https://webarena.dev/ | Browser agent scores |
| LMSYS Chatbot Arena | https://chat.lmsys.org/?leaderboard | LLM Elo ratings (foundation model layer) |
| Open LLM Leaderboard | https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard | Open model benchmarks |

---

## 3. Academic Literature (Free APIs)

| Source | API | Free Tier |
|--------|-----|-----------|
| **Semantic Scholar** | https://api.semanticscholar.org/ | 1 req/sec (no key), 10 req/sec (free key) |
| **OpenAlex** | https://openalex.org/ | Unlimited (free, open) |
| **arXiv** | https://arxiv.org/help/api | Free, rate-limited |
| **CORE** | https://core.ac.uk/services/api | Free with registration |
| **Crossref** | https://www.crossref.org/documentation/retrieve-metadata/ | Free ("polite" pool) |

### Recommended: Use `search_literature.py`
```bash
cd data/literature
python search_literature.py
# Optional: set S2_API_KEY for 10x rate limit (free key from semanticscholar.org)
```

---

## 4. GitHub Metrics (Free API)

| Data Point | Source |
|------------|--------|
| Stars, forks, issues | GitHub REST API (60 req/hr free, 5000 with token) |
| Contributor count | GitHub REST API |
| Commit frequency | GitHub REST API |
| PyPI/npm downloads | https://pypistats.org/api/ (free) / https://api.npmjs.org/ (free) |

### Recommended: Use `compare_frameworks.py`
```bash
cd data/market-data
python compare_frameworks.py
# Optional: set GITHUB_TOKEN for higher rate limits
```

---

## 5. Market & Investment Data (Free Sources)

| Data Type | Free Sources |
|-----------|-------------|
| **Market sizing** | Grand View Research (press releases), Statista (limited free), Precedence Research (free summaries) |
| **Investment rounds** | Crunchbase (free tier), TechCrunch articles, company press releases |
| **Enterprise adoption** | Quarterly earnings transcripts (SEC EDGAR, free), investor presentations |
| **Gartner Hype Cycle** | Gartner press releases (free), analyst blog posts |
| **AI adoption surveys** | McKinsey Global AI Survey (free PDF), Stanford AI Index (free PDF) |
| **GitHub ecosystem** | GitHub State of the Octoverse (free annual report) |

### Key Free Reports
- **Stanford HAI AI Index 2025**: https://aiindex.stanford.edu/report/
- **McKinsey State of AI 2024**: https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai
- **GitHub Octoverse**: https://octoverse.github.com/
- **State of AI Report**: https://www.stateof.ai/ (annual, free)

---

## 6. Protocol Specifications (Free, Open)

| Protocol | Specification | License |
|----------|--------------|---------|
| **MCP** | https://spec.modelcontextprotocol.io/ | Open (Linux Foundation) |
| **A2A** | https://google.github.io/A2A/ | Apache-2.0 (Linux Foundation) |
| **AG-UI** | https://docs.ag-ui.com/ | Open (CopilotKit) |

---

## 7. Google Dataset Search & Kaggle

### Google Dataset Search
URL: https://datasetsearch.research.google.com/

Recommended searches:
- `"LLM agent" benchmark`
- `"autonomous agent" evaluation dataset`
- `"tool use" language model`
- `"multi-agent" coordination`

### Kaggle
URL: https://www.kaggle.com/datasets

Recommended searches:
- `AI agent benchmark`
- `LLM evaluation`
- `code generation benchmark`

### HuggingFace Datasets Hub
URL: https://huggingface.co/datasets

Filter by:
- Task: question-answering, text-generation
- Search: "agent", "benchmark", "tool-use"

---

## Pipeline Execution Order

Run the data collection scripts in this order:

```
Step 1: Collect benchmark data
  cd publications/01-agentic-ai/data/benchmarks
  python collect_benchmarks.py

Step 2: Search academic literature
  cd publications/01-agentic-ai/data/literature
  python search_literature.py

Step 3: Collect framework GitHub metrics
  cd publications/01-agentic-ai/data/market-data
  python compare_frameworks.py

Step 4: Update paper.tex with collected data
  - Fill in benchmark tables (Table 4, 5)
  - Update framework comparison (Table 2)
  - Add citation counts to Related Work
  - Update market figures with latest data

Step 5: Compile the paper
  cd publications/01-agentic-ai/submission
  pdflatex paper.tex
  bibtex paper
  pdflatex paper.tex
  pdflatex paper.tex
```
