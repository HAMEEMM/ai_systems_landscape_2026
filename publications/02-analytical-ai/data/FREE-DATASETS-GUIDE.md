# FREE Datasets Guide — Analytical AI Paper #2

> Every benchmark, dataset, and API used in this paper is **free** and **publicly accessible**.
> No paid subscriptions, licences, or institutional access required.

---

## 1. NL2SQL Benchmarks

| Dataset                | Size                            | Download                                                                                                         | Notes                            |
| ---------------------- | ------------------------------- | ---------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| **Spider**             | 10,181 questions, 200 databases | `git clone https://github.com/taoyds/spider` or [yale-lily.github.io/spider](https://yale-lily.github.io/spider) | Cross-database NL2SQL benchmark  |
| **BIRD-SQL**           | 12,751 questions, 95 databases  | [bird-bench.github.io](https://bird-bench.github.io/)                                                            | Value-grounded, bigger databases |
| **WikiTableQuestions** | 22,033 questions                | `pip install datasets && python -c "from datasets import load_dataset; ds = load_dataset('wikitablequestions')"` | Table QA benchmark               |
| **SParC**              | 4,298 multi-turn questions      | [yale-lily.github.io/sparc](https://yale-lily.github.io/sparc)                                                   | Context-dependent NL2SQL         |
| **CoSQL**              | 3,007 conversational questions  | [yale-lily.github.io/cosql](https://yale-lily.github.io/cosql)                                                   | Dialogue-based NL2SQL            |

---

## 2. Clustering & Analytical Technique Datasets

| Dataset               | Size                     | Download                                                                              | Notes                         |
| --------------------- | ------------------------ | ------------------------------------------------------------------------------------- | ----------------------------- |
| **UCI ML Repository** | 600+ datasets            | [archive.ics.uci.edu](https://archive.ics.uci.edu/)                                   | Classic ML benchmark datasets |
| **Iris**              | 150 samples, 4 features  | `from sklearn.datasets import load_iris`                                              | Standard clustering benchmark |
| **Wine**              | 178 samples, 13 features | `from sklearn.datasets import load_wine`                                              | Multi-class clustering        |
| **Mall Customers**    | 200 samples, 5 features  | [Kaggle](https://www.kaggle.com/datasets/vjchoudhary7/customer-segmentation-tutorial) | Customer segmentation         |
| **Credit Card Fraud** | 284,807 transactions     | [Kaggle](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)                     | Anomaly detection benchmark   |
| **NYC Taxi**          | 1B+ trips                | [nyc.gov/tlc](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)           | Time-series analytics         |

---

## 3. Causal Inference Datasets

| Dataset                      | Size          | Download                                                                          | Notes                            |
| ---------------------------- | ------------- | --------------------------------------------------------------------------------- | -------------------------------- |
| **IHDP**                     | 747 samples   | Included in `causalml` package: `pip install causalml`                            | Infant health, semi-synthetic    |
| **Twins**                    | 11,400 pairs  | Included in `causalml` package                                                    | Twin births, binary treatment    |
| **Jobs (LaLonde)**           | 722 samples   | `pip install dowhy` (bundled example)                                             | Job training RCT + observational |
| **Smoking/Birth Weight**     | ~4,642        | DoWhy tutorials: [py-why.github.io/dowhy](https://py-why.github.io/dowhy/)        | Causal effect estimation         |
| **Card (Angrist & Krueger)** | 3,010 samples | `import statsmodels.datasets; statsmodels.datasets.get_rdataset("card", "Ecdat")` | IV estimation                    |

---

## 4. Data Quality & Observability

| Resource               | Access                                                                     | Notes                     |
| ---------------------- | -------------------------------------------------------------------------- | ------------------------- |
| **Great Expectations** | `pip install great_expectations`                                           | Data validation framework |
| **Soda Core**          | `pip install soda-core`                                                    | Data quality checks       |
| **dbt test datasets**  | [github.com/dbt-labs/jaffle_shop](https://github.com/dbt-labs/jaffle_shop) | Sample dbt project        |
| **NYC Open Data**      | [data.cityofnewyork.us](https://data.cityofnewyork.us/)                    | 2,000+ public datasets    |

---

## 5. BI & Analytics Leaderboards

| Resource               | URL                                                                   | Notes                          |
| ---------------------- | --------------------------------------------------------------------- | ------------------------------ |
| **Spider Leaderboard** | [yale-lily.github.io/spider](https://yale-lily.github.io/spider)      | NL2SQL accuracy rankings       |
| **BIRD Leaderboard**   | [bird-bench.github.io](https://bird-bench.github.io/)                 | Value-grounded NL2SQL rankings |
| **Gartner MQ for BI**  | Published annually (summary available via vendor blogs)               | BI platform positioning        |
| **db-benchmark**       | [h2oai.github.io/db-benchmark](https://h2oai.github.io/db-benchmark/) | DataFrame library performance  |

---

## 6. Market Data Sources (Free)

| Source                                   | URL                                                                            | Notes                         |
| ---------------------------------------- | ------------------------------------------------------------------------------ | ----------------------------- |
| **Statista (free tier)**                 | [statista.com](https://www.statista.com/)                                      | Market sizing summaries       |
| **Grand View Research (press releases)** | [grandviewresearch.com](https://www.grandviewresearch.com/)                    | Free executive summaries      |
| **GitHub Stars History**                 | [star-history.com](https://star-history.com/)                                  | Track tool adoption over time |
| **StackOverflow Trends**                 | [insights.stackoverflow.com/trends](https://insights.stackoverflow.com/trends) | Technology popularity         |
| **Google Trends**                        | [trends.google.com](https://trends.google.com/)                                | Search interest over time     |
| **Papers With Code**                     | [paperswithcode.com](https://paperswithcode.com/)                              | Benchmark leaderboards        |

---

## Quick Start

```bash
# Install core analysis dependencies
pip install pandas scikit-learn matplotlib seaborn requests

# Install causal inference libraries
pip install dowhy causalml econml

# Install data quality tools
pip install great_expectations soda-core

# Download Spider benchmark
git clone https://github.com/taoyds/spider

# Run benchmark collection
python benchmarks/collect_benchmarks.py

# Run literature search
python literature/search_literature.py

# Run platform comparison
python market-data/compare_platforms.py
```
