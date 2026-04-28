"""
phase-2-core-techniques/03-association-rules/01_market_basket.py
─────────────────────────────────────────────────────────────────
Paper §5 — Association Rule Mining: Apriori & FP-Growth

Demonstrates:
 • Encoding transactions into a binary matrix
 • Apriori algorithm (mlxtend) — frequent itemsets
 • FP-Growth — same itemsets, faster on large data
 • Filtering rules by confidence and lift
 • Actionable output: cross-sell / upsell recommendations

Run:  python phase-2-core-techniques/03-association-rules/01_market_basket.py
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "shared"))

import numpy as np
import pandas as pd
from mlxtend.frequent_patterns import apriori, fpgrowth, association_rules
from mlxtend.preprocessing import TransactionEncoder
from rich.console import Console
from utils.data_utils import print_df

console = Console()


# ── Synthetic transaction generator ──────────────────────────────────────

def make_transactions(n: int = 1_000, seed: int = 42) -> list[list[str]]:
    """Synthetic basket data: laptop buyers often buy mouse/keyboard."""
    rng = np.random.default_rng(seed)
    items = ["Laptop", "Mouse", "Keyboard", "Monitor", "USB-Hub",
             "Webcam", "Headset", "Desk-Lamp", "Phone", "Tablet"]
    co_occur = {
        "Laptop":  ["Mouse", "Keyboard", "Monitor", "USB-Hub"],
        "Phone":   ["USB-Hub", "Headset"],
        "Tablet":  ["Keyboard", "Headset"],
    }
    baskets = []
    for _ in range(n):
        basket = set()
        anchor = rng.choice(["Laptop", "Phone", "Tablet", "Webcam"])
        basket.add(anchor)
        if anchor in co_occur:
            extras = rng.choice(co_occur[anchor],
                                size=rng.integers(1, len(co_occur[anchor])+1),
                                replace=False)
            basket.update(extras)
        # random add
        if rng.random() < 0.4:
            basket.add(rng.choice(items))
        baskets.append(list(basket))
    return baskets


# ── Encode + mine ────────────────────────────────────────────────────────

def encode(transactions: list) -> pd.DataFrame:
    te = TransactionEncoder()
    te_array = te.fit(transactions).transform(transactions)
    return pd.DataFrame(te_array, columns=te.columns_)


def mine_rules(df_encoded: pd.DataFrame, algo: str = "fpgrowth",
               min_support: float = 0.05, min_confidence: float = 0.5) -> pd.DataFrame:
    if algo == "apriori":
        freq = apriori(df_encoded, min_support=min_support, use_colnames=True)
    else:
        freq = fpgrowth(df_encoded, min_support=min_support, use_colnames=True)

    console.print(f"[cyan]{algo.upper()}[/cyan] — {len(freq)} frequent itemsets "
                  f"(min_support={min_support})")

    rules = association_rules(freq, metric="confidence", min_threshold=min_confidence)
    rules = rules.sort_values("lift", ascending=False)
    console.print(f"  {len(rules)} rules (min_confidence={min_confidence})")
    return rules


def show_top_rules(rules: pd.DataFrame, n: int = 10) -> None:
    top = rules.head(n)[["antecedents", "consequents",
                          "support", "confidence", "lift"]].copy()
    top["antecedents"]  = top["antecedents"].apply(lambda s: ", ".join(sorted(s)))
    top["consequents"]  = top["consequents"].apply(lambda s: ", ".join(sorted(s)))
    top = top.round({"support": 3, "confidence": 3, "lift": 3})
    print_df(top, title=f"Top {n} Rules by Lift")


def recommend(rules: pd.DataFrame, basket: list[str]) -> list[str]:
    """Given current basket items, find consequents from matching antecedent rules."""
    basket_set = frozenset(basket)
    matches = rules[rules["antecedents"].apply(lambda a: a.issubset(basket_set))]
    recs = set()
    for _, row in matches.iterrows():
        recs.update(row["consequents"])
    recs -= basket_set
    return sorted(recs)


# ── MAIN ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    console.rule("[bold]Phase 2 — Market Basket / Association Rules")

    txns       = make_transactions(n=2_000)
    df_encoded = encode(txns)

    console.rule("Apriori")
    rules_apriori = mine_rules(df_encoded, algo="apriori",  min_support=0.04)

    console.rule("FP-Growth")
    rules_fp      = mine_rules(df_encoded, algo="fpgrowth", min_support=0.04)

    show_top_rules(rules_fp)

    test_basket = ["Laptop", "Mouse"]
    recs = recommend(rules_fp, test_basket)
    console.print(f"\n[yellow]Cross-sell recommendations for {test_basket}:[/yellow]")
    console.print(f"  → {recs}")

    console.print("\n[green]✓ Association rule mining complete.[/green]")
