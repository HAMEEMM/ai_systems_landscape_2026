# Data — Paper #2: Analytical AI

## What This Folder Contains

This folder has **three helper scripts** that collect publicly available data to support the
Analytical AI paper. Each script gathers a different type of evidence:

| Script                               | What It Does                                                                                                                                                                                          | Output                                                       |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| `benchmarks/collect_benchmarks.py` | Downloads and runs standard AI benchmarks (NL2SQL accuracy, clustering quality, causal inference metrics) using free datasets like Spider, BIRD-SQL, UCI, and DoWhy                                   | Benchmark scores in `benchmarks/`                          |
| `literature/search_literature.py`  | Searches [Semantic Scholar](https://www.semanticscholar.org/) (a free academic search engine) for published research papers on topics covered in the paper (causal inference, NL2SQL, BI, data quality) | CSV + JSON of papers with citation counts in `literature/` |
| `market-data/compare_platforms.py` | Fetches GitHub stars, forks, and activity for 40+ open-source analytical tools (pandas, dbt, Apache Superset, etc.) to compare platform adoption                                                      | Platform comparison data in `market-data/`                 |

> **All data sources are free.** No paid subscriptions or institutional access required.

### Folder Structure

```
data/
├── README.md                        ← You are here
├── FREE-DATASETS-GUIDE.md           ← Complete guide to all free datasets
├── benchmarks/
│   └── collect_benchmarks.py        ← NL2SQL, clustering, BI, causal benchmarks
├── literature/
│   └── search_literature.py         ← Semantic Scholar API search
└── market-data/
    └── compare_platforms.py         ← GitHub metrics for 40+ analytical tools
```

---

## How to Run

### Step 1: Install dependencies

```bash
pip install requests pandas scikit-learn dowhy causalml
```

### Step 2: Navigate to this folder

```bash
cd publications/02-analytical-ai/data
```

### Step 3: Run any script

```bash
python benchmarks/collect_benchmarks.py
python literature/search_literature.py
python market-data/compare_platforms.py
```

> **Important:** Always `cd` into `publications/02-analytical-ai/data/` first.
> Do **not** pass file paths as arguments — the scripts take no arguments.

---

## About `literature/search_literature.py`

This script uses the **Semantic Scholar Academic Graph API** (free, public) to search for
research papers. It runs 24 keyword searches (e.g., "causal inference machine learning survey",
"NL2SQL text-to-SQL large language models") and saves all unique results as
`literature/literature_search_results.csv` and `.json`.

### Rate Limiting

Semantic Scholar limits unauthenticated requests to **1 request per second**. The script
includes retry logic, but if you run it multiple times in quick succession you may see
`429 (Too Many Requests)` or `500 (Server Error)` messages. This is normal.

**Two ways to handle this:**

1. **Without an API key (default):** Just wait 5–10 minutes between runs. The script has
   built-in retry with exponential backoff and will recover on its own.
2. **With a free API key (recommended):** Get a free key from
   https://www.semanticscholar.org/product/api#api-key-form — then set it before running:

   ```bash
   # Windows (Command Prompt)
   set S2_API_KEY=your_key_here
   python literature/search_literature.py

   # Windows (PowerShell)
   $env:S2_API_KEY="your_key_here"
   python literature/search_literature.py

   # Linux / macOS / Git Bash
   S2_API_KEY=your_key_here python literature/search_literature.py
   ```

   This increases the limit to **10 requests/second** and eliminates rate-limit errors.

---

## Key Datasets

| Dataset           | Source                             | Description                                |
| ----------------- | ---------------------------------- | ------------------------------------------ |
| Spider            | https://yale-lily.github.io/spider | NL2SQL benchmark (10K questions, 200 DBs)  |
| BIRD-SQL          | https://bird-bench.github.io/      | Value-grounded NL2SQL (12.7K questions)    |
| UCI ML Repository | https://archive.ics.uci.edu/       | Clustering & analytical technique datasets |
| IHDP / Twins      | Included in `causalml` package   | Causal inference evaluation datasets       |
| DoWhy examples    | https://py-why.github.io/dowhy/    | Causal estimation benchmarks               |

See [FREE-DATASETS-GUIDE.md](FREE-DATASETS-GUIDE.md) for the complete list with download instructions.
