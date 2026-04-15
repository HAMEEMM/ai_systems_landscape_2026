# Data — Paper #2: Analytical AI

## Public Datasets for Analytical AI Research

This folder contains scripts and metadata for publicly available datasets used in the paper.

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

### Quick Start

```bash
# Navigate to the data folder first
cd publications/02-analytical-ai/data

# Install dependencies
pip install requests pandas scikit-learn dowhy causalml

# Run the scripts
python benchmarks/collect_benchmarks.py
python literature/search_literature.py
python market-data/compare_platforms.py
```

### Key Datasets

| Dataset           | Source                             | Description                                |
| ----------------- | ---------------------------------- | ------------------------------------------ |
| Spider            | https://yale-lily.github.io/spider | NL2SQL benchmark (10K questions, 200 DBs)  |
| BIRD-SQL          | https://bird-bench.github.io/      | Value-grounded NL2SQL (12.7K questions)    |
| UCI ML Repository | https://archive.ics.uci.edu/       | Clustering & analytical technique datasets |
| IHDP / Twins      | Included in `causalml` package     | Causal inference evaluation datasets       |
| DoWhy examples    | https://py-why.github.io/dowhy/    | Causal estimation benchmarks               |

See [FREE-DATASETS-GUIDE.md](FREE-DATASETS-GUIDE.md) for the complete list with download instructions.
