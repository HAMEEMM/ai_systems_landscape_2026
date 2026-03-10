# Perceive, Plan, Act, Self-Correct

**Full Title:** Perceive, Plan, Act, Self-Correct: An Architectural Framework for Goal-Directed Agentic AI Systems

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

**Author:** Hameem M Mahdi, B.S.C.S., M.S.E., Ph.D.

**Corresponding Chapter:** [Agentic AI — Interactive Architecture Chart](../../chapters/agentic-ai.html)

---

## Status

> **engrXiv Preprint Published** — DOI: [10.31224/6738](https://doi.org/10.31224/6738) (March 2026)  
> Nature Machine Intelligence peer-review submission in preparation — target Q3 2026

---

## Paper Objective

This paper presents a rigorous **architectural framework** for goal-directed Agentic AI systems, centering on the canonical loop: **Perceive → Plan → Act → Self-Correct**. It covers the complete development lifecycle and 8-layer technology stack, offers empirical validation through benchmark analysis and production case studies, and positions the framework within the broader AI systems taxonomy established in our companion paper (Paper #0, ACM Computing Surveys — under review).

---

## Research Questions

| # | Question |
|---|----------|
| RQ1 | What architectural primitives distinguish Agentic AI from other autonomous and generative AI paradigms? |
| RQ2 | How does the 8-layer agentic technology stack (foundation models → observability) map to production implementations? |
| RQ3 | What design patterns (ReAct, Reflection, Plan-and-Execute, HITL) yield the highest task-completion rates across benchmark suites? |
| RQ4 | How do inter-agent protocols (MCP, A2A, AG-UI) affect multi-agent coordination efficiency? |
| RQ5 | What are the dominant failure modes, safety risks, and mitigation strategies in deployed agentic systems? |

---

## Proposed Paper Structure

| § | Section | Content |
|---|---------|---------|
| 1 | **Introduction** | Motivation, scope, relationship to Paper #0, research questions |
| 2 | **Background & Related Work** | LLM agents survey, agent architectures history (GOFAI → ReAct), existing taxonomies |
| 3 | **The Agent Loop Framework** | Formal definition of the Perceive → Plan → Act → Self-Correct cycle; comparison with OODA, BDI, and SOAR |
| 4 | **The 8-Layer Agentic Stack** | Layer-by-layer analysis: Foundation Models, Runtime & Orchestration, Memory, Tools & Integration, Inter-Agent Protocols, Planning & Reflection, Applications, Observability & Safety |
| 5 | **Design Patterns** | ReAct, Reflection, Tree-of-Thought, Plan-and-Execute, HITL, Multi-Agent topologies (supervisor, swarm, hierarchical) |
| 6 | **Memory Architectures** | Working, short-term, long-term, episodic, semantic, procedural — design trade-offs and implementations |
| 7 | **Inter-Agent Protocols** | MCP (agent-tool), A2A (agent-agent), AG-UI (agent-frontend) — protocol design, adoption, and interoperability analysis |
| 8 | **Empirical Evaluation** | Benchmark analysis (SWE-Bench, WebArena, GAIA, BrowseComp), production case studies |
| 9 | **Market & Adoption Analysis** | Market sizing ($7.3B 2025 → $139–182B 2034), investment landscape, enterprise adoption metrics |
| 10 | **Risks, Failure Modes & Safety** | Autonomous drift, irreversible actions, resource exhaustion, prompt injection, guardrail framework |
| 11 | **Regulation & Governance** | EU AI Act implications, NIST AI RMF mapping, HITL requirements for high-risk classification |
| 12 | **Open Problems & Future Directions** | Long-horizon planning, self-improvement loops, multi-agent trust, cost-quality frontiers |
| 13 | **Conclusion** | Summary of contributions, taxonomy position, call-to-action |

---

## Full Agentic AI Development Lifecycle & Tech Stack

This is the end-to-end tech stack the paper will cover, organized as a development lifecycle you can follow hands-on.

### Phase 1 — Learn the Foundations (Weeks 1–3)

| Layer | What to Learn | Hands-On Resources |
|-------|--------------|---------------------|
| **Foundation Models** | How LLMs work — attention, tokenization, inference, RLHF, tool-calling APIs | [Andrej Karpathy — Let's Build GPT](https://www.youtube.com/watch?v=kCc8FmEb1nY), [OpenAI Cookbook](https://cookbook.openai.com/), [Anthropic Docs](https://docs.anthropic.com/) |
| **Prompt Engineering** | System prompts, few-shot, chain-of-thought, structured outputs | [Prompt Engineering Guide](https://www.promptingguide.ai/), [DeepLearning.AI Short Courses](https://www.deeplearning.ai/short-courses/) |
| **Agent Concepts** | ReAct pattern, tool use, agent loop, planning | [Lilian Weng — LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/), [Andrew Ng — Agentic Design Patterns](https://www.deeplearning.ai/the-batch/how-agents-can-improve-llm-performance/) |

### Phase 2 — Build the Agent Core (Weeks 4–6)

| Layer | What to Build | Frameworks & Tools |
|-------|--------------|---------------------|
| **Agent Runtime** | Single-agent ReAct loop with tool calling | [LangGraph](https://langchain-ai.github.io/langgraph/), [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/), [Google ADK](https://google.github.io/adk-docs/) |
| **Tool Integration** | Web search, code execution, browser, database tools | [Tavily](https://tavily.com/), [E2B](https://e2b.dev/), [Composio](https://composio.dev/), [Firecrawl](https://firecrawl.dev/) |
| **Memory Systems** | Working memory, session memory, persistent memory | [Mem0](https://mem0.ai/), [Zep](https://www.getzep.com/), [Letta/MemGPT](https://www.letta.com/), Redis |
| **Planning** | Chain-of-Thought, Tree-of-Thought, plan-and-execute | LangGraph prebuilt planners, custom ToT implementations |

### Phase 3 — Scale to Multi-Agent (Weeks 7–9)

| Layer | What to Build | Frameworks & Tools |
|-------|--------------|---------------------|
| **Multi-Agent Topologies** | Supervisor, swarm, hierarchical delegation | [CrewAI](https://www.crewai.com/), [AutoGen](https://microsoft.github.io/autogen/), LangGraph multi-agent |
| **Inter-Agent Protocols** | MCP servers, A2A communication, AG-UI streaming | [MCP Spec](https://modelcontextprotocol.io/), [A2A Spec](https://google.github.io/A2A/), [AG-UI](https://docs.ag-ui.com/) |
| **Human-in-the-Loop** | Approval gates, interrupt nodes, handoff patterns | LangGraph `interrupt()`, OpenAI SDK handoffs |

### Phase 4 — Productionize (Weeks 10–12)

| Layer | What to Build | Tools & Platforms |
|-------|--------------|-------------------|
| **Observability** | Tracing, token cost tracking, latency monitoring, eval suites | [LangSmith](https://smith.langchain.com/), [Langfuse](https://langfuse.com/), [Arize Phoenix](https://phoenix.arize.com/), [Braintrust](https://www.braintrust.dev/) |
| **Safety & Guardrails** | Input validation, output filtering, PII detection, kill switches | [Guardrails AI](https://www.guardrailsai.com/), [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails), custom circuit breakers |
| **Evaluation** | Benchmark on SWE-Bench, WebArena, GAIA; LLM-as-judge scoring | [SWE-Bench](https://www.swebench.com/), [AgentBench](https://github.com/THUDM/AgentBench), [Ragas](https://ragas.io/) |
| **Deployment** | Serve via API, integrate into enterprise platforms | AWS Bedrock Agents, Azure AI Agent Service, Google Vertex AI Agent Builder |

### Phase 5 — Research & Write (Weeks 13–16)

| Activity | What to Do | Tools |
|----------|-----------|-------|
| **Literature Review** | Systematic search across Scopus, IEEE Xplore, ACM DL, arXiv, Semantic Scholar | [Semantic Scholar API](https://www.semanticscholar.org/product/api), [Connected Papers](https://www.connectedpapers.com/), [Elicit](https://elicit.com/) |
| **Data Collection** | Aggregate benchmark results, market data (Gartner, IDC, Grand View Research), GitHub stars/adoption | Public leaderboards, company reports, arXiv papers |
| **Experimental Validation** | Reproduce key benchmark runs, case study interviews, framework comparison | Your Phase 2–4 implementations as primary evidence |
| **Writing** | LaTeX manuscript in `acmart` format, BibTeX bibliography, supplementary materials | [Overleaf](https://www.overleaf.com/), VS Code + LaTeX Workshop, [Zotero](https://www.zotero.org/) for reference management |
| **Figures** | Architecture diagrams, benchmark charts, stack visualisations | TikZ/PGFPlots (LaTeX), [Draw.io](https://draw.io/), [Excalidraw](https://excalidraw.com/) |

---

## Where to Publish — Peer-Review Platforms

### Recommended Target Venue

| Priority | Venue | Type | Why |
|----------|-------|------|-----|
| **1st choice** | **[Nature Machine Intelligence](https://www.nature.com/natmachintell/)** | Journal | Premier AI journal. Multi-agent/agent architecture is a core topic. Impact factor ~18.8. |
| **2nd choice** | **[JMLR](https://jmlr.org/)** (Journal of Machine Learning Research) | Journal | Open access. Systems + ML focus. Highly respected. |
| **3rd choice** | **[IEEE TPAMI](https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=34)** | Journal | Top-tier. If the paper takes a more architectural/systems angle. |
| **Alt: Conference** | **[NeurIPS](https://neurips.cc/) / [ICML](https://icml.cc/) / [AAAI](https://aaai.org/)** | Conference | Higher visibility, faster turnaround, but page-limited (8–10 pages). |
| **Alt: Workshop** | **NeurIPS Agent Workshop** or **ICML AgentLab** | Workshop | Lower barrier, good for early-stage feedback before journal submission. |

### Pre-Print Strategy

| Step | Platform | Purpose |
|------|----------|---------|
| 1 | **[arXiv cs.AI](https://arxiv.org/)** | Post pre-print immediately for visibility and timestamping |
| 2 | **[Semantic Scholar](https://www.semanticscholar.org/)** | Auto-indexed from arXiv; increases citation discovery |
| 3 | **[Papers with Code](https://paperswithcode.com/)** | Link paper to your GitHub repo and benchmark results |
| 4 | **[SSRN](https://www.ssrn.com/)** | Additional pre-print platform for cross-disciplinary reach |

---

## Data Sources for the Paper

| Data Type | Sources |
|-----------|---------|
| **Academic Literature** | Scopus, Web of Science, IEEE Xplore, ACM Digital Library, arXiv, Semantic Scholar |
| **Benchmarks** | SWE-Bench Verified, WebArena, GAIA, BrowseComp, Humanity's Last Exam, τ-bench, OSWorld |
| **Market Data** | Grand View Research, Gartner Hype Cycle, IDC MarketScape, McKinsey Global AI Survey, CB Insights |
| **Adoption Data** | Salesforce earnings reports, GitHub Copilot metrics, OpenAI usage reports, company press releases |
| **Investment Data** | Crunchbase, PitchBook, CB Insights, company funding announcements |
| **Framework Metrics** | GitHub stars, npm/PyPI downloads, Docker Hub pulls, framework documentation |
| **Protocol Specs** | MCP specification (Anthropic/Linux Foundation), A2A specification (Google/Linux Foundation), AG-UI specification (CopilotKit) |

---

## Repository Structure

```
publications/01-agentic-ai/
├── README.md                  ← You are here (research plan & roadmap)
├── submission/
│   ├── engrxiv-pre-print/     ← engrXiv preprint submission
│   │   ├── paper.tex          ← Full manuscript (article class, author-year citations)
│   │   ├── references.bib     ← BibTeX bibliography
│   │   └── README.md          ← engrXiv submission instructions
│   └── nature-machine-intelligence-peer-review/    ← Nature Machine Intelligence peer-review submission
│       ├── paper.tex          ← Condensed manuscript (Nature format)
│       ├── references.bib     ← Bibliography (Nature style)
│       └── README.md          ← Nature Machine Intelligence submission instructions
├── data/                      ← Raw data and analysis notebooks
│   ├── benchmarks/            ← Benchmark result aggregation
│   ├── market-data/           ← Market sizing sources
│   └── literature/            ← Citation analysis data
└── drafts/                    ← Working drafts before submission
```

---

## Corresponding Visual Assets

| Asset | Path |
|-------|------|
| Conceptual Overview GIF | [`assets/overview-gifs/01-agentic-ai-overview.gif`](../../assets/overview-gifs/01-agentic-ai-overview.gif) |
| Full Tech Stack GIF | [`assets/tech-stack-gifs/01-agentic-ai-tech-stack.gif`](../../assets/tech-stack-gifs/01-agentic-ai-tech-stack.gif) |
| Interactive Chapter | [`chapters/agentic-ai.html`](../../chapters/agentic-ai.html) |

---

## Citation

```bibtex
@article{mahdi2025agentic,
  author  = {Hameem M. Mahdi},
  title   = {Perceive, Plan, Act, Self-Correct: An Architectural Framework for Goal-Directed Agentic {AI} Systems},
  year    = {2025},
  journal = {engrXiv},
  doi     = {10.31224/6738},
  url     = {https://doi.org/10.31224/6738},
  note    = {Preprint}
}
```

---

## License

This work is shared under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).
