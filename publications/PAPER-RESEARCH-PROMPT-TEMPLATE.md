# Reusable Prompt Template — AI Systems Landscape Research Papers

> **Purpose:** Copy this prompt and fill in the `[PLACEHOLDERS]` each time you start a new paper for AI system types 02–19.
> Run the completed prompt through your AI assistant to generate a comprehensive README, research plan, tech-stack learning path, and peer-review publishing strategy — identical in structure to `publications/01-agentic-ai/README.md`.

---

## How to Use

1. Copy the entire **PROMPT** section below
2. Replace every `[PLACEHOLDER]` with the specific values for your AI system type
3. Paste the completed prompt into your AI coding assistant (GitHub Copilot, Claude, etc.)
4. The assistant will generate a full README.md for `publications/[NN]-[system-slug]/README.md`

---

## Reference Table — Fill-In Values for Each Paper

| #  | `[PAPER_NUMBER]`                    | `[SYSTEM_NAME]`                     | `[SYSTEM_SLUG]`                   | `[PAPER_TITLE]` (from FORTHCOMING-PUBLICATIONS.md)                                                                                |
| -- | ------------------------------------- | ------------------------------------- | ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| 02 | 02                                    | Analytical AI                         | analytical-ai                       | Causal Inference at Scale: How Analytical AI Transforms Pattern Mining Into Actionable Business Intelligence                        |
| 03 | 03                                    | Autonomous AI (Non-Agentic)           | autonomous-ai                       | Autonomy Without Agency: A Formal Distinction Between Autonomous and Agentic AI Systems in Safety-Critical Domains                  |
| 04 | 04                                    | Bayesian / Probabilistic AI           | bayesian-probabilistic-ai           | From Bayes' Theorem to Clinical Deployment: Probabilistic AI for High-Stakes Decision-Making Under Uncertainty                      |
| 05 | 05                                    | Cognitive / Neuro-Symbolic AI         | cognitive-neuro-symbolic-ai         | Beyond Hallucination: How Neuro-Symbolic Fusion Enables Verifiable Reasoning in Large Language Models                               |
| 06 | 06                                    | Conversational AI                     | conversational-ai                   | Where Humans Meet Machines: A Survey of Conversational AI Pipelines From NLU to Real-Time Response Generation                       |
| 07 | 07                                    | Evolutionary / Genetic AI             | evolutionary-genetic-ai             | Population-Based Search for Neural Architecture Design: Evolutionary AI in AutoML, Drug Discovery, and Robot Morphology             |
| 08 | 08                                    | Explainable AI (XAI)                  | explainable-ai                      | SHAP, LIME, and Beyond: Post-Hoc Explanation Methods for Black-Box Models in Healthcare, Finance, and Criminal Justice              |
| 09 | 09                                    | Federated / Privacy-Preserving AI     | federated-privacy-ai                | Trustless Collaboration: Harnessing Cryptographic Computation and Federated AI for Secure Multi-Institutional Synthesis             |
| 10 | 10                                    | Generative AI                         | generative-ai                       | Architectural Evolution: From Statistical Autoregression to Grounded and Verifiable Reasoning in Generative Systems                 |
| 11 | 11                                    | Multimodal Perception AI              | multimodal-perception-ai            | Seeing, Reading, and Hearing Simultaneously: How Multimodal Perception AI Achieves Understanding Beyond Any Single Modality         |
| 12 | 12                                    | Optimisation / Operations Research AI | optimisation-operations-research-ai | Exact Solvers, Heuristics, and Hybrid AI: A Survey of Optimization Architectures for Supply Chain, Routing, and Resource Allocation |
| 13 | 13                                    | Physical / Embodied AI                | physical-embodied-ai                | AI in the Physical World: Foundation Models for Robotics, Sim-to-Real Transfer, and Real-Time Embodied Intelligence                 |
| 14 | 14                                    | Predictive / Discriminative AI        | predictive-discriminative-ai        | Supervised Learning in Production: How Predictive AI Drives Billions of Daily Decisions in Medical Diagnosis                        |
| 15 | 15                                    | Reactive AI                           | reactive-ai                         | Stateless by Design: Why Reactive AI Systems Without Memory, Learning, or Planning Remain Essential in Safety-Critical Domains      |
| 16 | 16                                    | Recommendation / Retrieval AI         | recommendation-retrieval-ai         | From Collaborative Filtering to Neural Retrieval: The Evolution of Recommendation AI in Search and Social Media Platforms           |
| 17 | 17                                    | Reinforcement Learning AI             | reinforcement-learning-ai           | Trial, Error, and Reward: How Reinforcement Learning Discovers Strategies No Human Taught — From Game Play to Protein Folding      |
| 18 | 18                                    | Scientific / Simulation AI            | scientific-simulation-ai            | AlphaFold, GNoME, and GraphCast: How Scientific AI Is Transforming Chemistry, Materials Science, and Weather Forecasting            |
| 19 | 19                                    | Symbolic / Rule-Based AI              | symbolic-rule-based-ai              | Explicit Knowledge, Traceable Reasoning: A Survey of Symbolic and Rule-Based AI From GOFAI to Modern Hybrid Systems                 |

---

## PROMPT

Copy everything below the line and fill in the placeholders.

---

```
I am writing a peer-reviewed research paper as part of the AI Systems Landscape 2026 project.

PROJECT CONTEXT:
- Parent project: https://hameemm.github.io/ai_systems_landscape_2026/
- Paper #0 (unified taxonomy) is already submitted to ACM TIST and is under peer review.
- Paper #1 (Agentic AI) has its full research plan in publications/01-agentic-ai/README.md.
- I am now starting Paper #[PAPER_NUMBER]: "[PAPER_TITLE]"
- The paper folder: publications/[PAPER_NUMBER]-[SYSTEM_SLUG]/
- The corresponding interactive chapter: chapters/[SYSTEM_SLUG].html
- The overview GIF: assets/overview-gifs/[PAPER_NUMBER]-[SYSTEM_SLUG]-overview.gif
- The tech stack GIF: assets/tech-stack-gifs/[PAPER_NUMBER]-[SYSTEM_SLUG]-tech-stack.gif

EXISTING ASSETS TO USE AS PRIMARY SOURCE MATERIAL:
- Read and deeply analyse chapters/[SYSTEM_SLUG].html — it contains the full interactive
  knowledge base covering: architecture, tech stack layers, design patterns, frameworks,
  benchmarks, market data, use cases, risks, regulation, and glossary.
- Read publications/01-agentic-ai/README.md for the structural template to follow.
- Read publications/FORTHCOMING-PUBLICATIONS.md for the confirmed paper title.
- Read RESEARCH-PAPER-TITLES.md for the 2–3 candidate titles (title #1 is already selected).
- Read publications/README.md for the finalized preprint server and peer-review venue assignment.
- Read publications/[PAPER_NUMBER]-[SYSTEM_SLUG]/submission/{server}-pre-print/README.md for preprint submission steps.
- Read publications/[PAPER_NUMBER]-[SYSTEM_SLUG]/submission/{journal}-peer-review/README.md for journal submission steps.

AUTHOR: Hameem M Mahdi, B.S.C.S., M.S.E., Ph.D.
ORCID: 0009-0007-0005-3080
EMAIL: mahdi.hameem@mayo.edu
AFFILIATION: Mayo Clinic, Rochester, MN, USA

DELIVERABLE — Generate a comprehensive README.md for publications/[PAPER_NUMBER]-[SYSTEM_SLUG]/README.md that includes ALL of the following sections. Match the exact structure and depth of publications/01-agentic-ai/README.md:

1. HEADER
   - Paper title and subtitle
   - CC BY 4.0 badge
   - Author, corresponding chapter link
   - Status line: "Manuscript in preparation — target submission Q[X] 2026"

2. PAPER OBJECTIVE
   - 3–4 sentence description of what the paper contributes
   - How it connects to Paper #0 (the taxonomy paper)

3. RESEARCH QUESTIONS
   - 4–6 specific, answerable research questions tailored to [SYSTEM_NAME]
   - Cover architecture, tech stack, empirical evaluation, and practical impact

4. PROPOSED PAPER STRUCTURE
   - Full section outline (§1 through §12+) with section title and 1-line content description
   - Must cover: Introduction, Background, Core Architecture/Framework, Tech Stack,
     Design Patterns, Empirical Evaluation, Market Analysis, Risks & Safety,
     Regulation, Open Problems, Conclusion

5. FULL DEVELOPMENT LIFECYCLE & TECH STACK
   This is the most important section. Organize as 5 phases:

   Phase 1 — Learn the Foundations (Weeks 1–3):
   - List every foundational concept specific to [SYSTEM_NAME]
   - Provide hands-on learning resources: YouTube lectures, courses, official docs, blog posts
   - Focus on what makes [SYSTEM_NAME] architecturally unique

   Phase 2 — Build the Core (Weeks 4–6):
   - Identify the core frameworks, libraries, and tools used to BUILD [SYSTEM_NAME] systems
   - Provide links to official documentation
   - Include specific hands-on projects to implement

   Phase 3 — Scale & Integrate (Weeks 7–9):
   - Advanced patterns, scaling strategies, and integration with other AI system types
   - Multi-system combinations (refer to the "System Combos" section on index.html)

   Phase 4 — Productionize (Weeks 10–12):
   - Observability, evaluation, benchmarking, deployment tools
   - Specific benchmarks relevant to [SYSTEM_NAME]
   - Safety, guardrails, and monitoring

   Phase 5 — Research & Write (Weeks 13–16):
   - Literature review strategy (which databases, which search queries)
   - Data collection sources specific to [SYSTEM_NAME]
   - Experimental validation approach
   - Writing tools (LaTeX, Overleaf, Zotero, etc.)
   - Figure creation tools

6. WHERE TO PUBLISH — DUAL-SUBMISSION STRATEGY
   Each paper has a FINALIZED preprint + peer-review assignment (see publications/README.md).
   - Reference the assigned preprint server from publications/[PAPER_NUMBER]-[SYSTEM_SLUG]/submission/{server}-pre-print/README.md
   - Reference the assigned peer-review journal from publications/[PAPER_NUMBER]-[SYSTEM_SLUG]/submission/{journal}-peer-review/README.md
   - Include 2-3 backup peer-review venues in case of rejection
   - Conference alternatives: NeurIPS, ICML, AAAI, or domain-specific conferences
   - Workshop alternative for early feedback

7. DATA SOURCES FOR THE PAPER
   Table of data types and specific sources relevant to [SYSTEM_NAME]

8. REPOSITORY STRUCTURE
   Show the planned folder structure matching the first paper's pattern:
   data/ (benchmarks/, market-data/, literature/) — at the publication root, NOT inside submission/
   submission/
     {server}-pre-print/            — Preprint server submission (folder named by platform)
       paper.tex, references.bib, README.md
     {journal}-peer-review/          — Journal submission (folder named by venue)
       paper.tex, references.bib, README.md

9. CORRESPONDING VISUAL ASSETS
   Link to the overview GIF, tech stack GIF, and interactive chapter

10. CITATION
    BibTeX entry in the same format as the Agentic AI paper

11. LICENSE
    CC BY 4.0

IMPORTANT GUIDELINES:
- Extract ALL technical content from chapters/[SYSTEM_SLUG].html — frameworks, tools,
  benchmarks, market data, vendors, use cases — these are your primary data source.
- Every framework and tool mentioned should link to its official documentation.
- The tech stack phases must be specific and actionable, not generic.
- Match the quality and depth of publications/01-agentic-ai/README.md exactly.
- The peer-review venue recommendation should consider which journal/conference
  best fits the specific topic of [SYSTEM_NAME], not just always default to ACM TIST.
- Do NOT generate the actual LaTeX paper — only the README research plan.
```

---

## Quick-Start Example

To start Paper #02 (Analytical AI), fill in:

```
[PAPER_NUMBER] = 02
[SYSTEM_NAME] = Analytical AI
[SYSTEM_SLUG] = analytical-ai
[PAPER_TITLE] = Causal Inference at Scale: How Analytical AI Transforms Pattern Mining Into Actionable Business Intelligence
```

Then paste the completed prompt into your AI assistant.

---

## Venue Selection Cheat Sheet

Different AI system types map better to different journals/conferences. Use this as a guide:

| AI System Type                | Best-Fit Journal                     | Best-Fit Conference      | Rationale                         |
| ----------------------------- | ------------------------------------ | ------------------------ | --------------------------------- |
| Analytical AI                 | ACM TIST, VLDB Journal               | KDD, SIGMOD              | Data mining & analytics focus     |
| Autonomous AI                 | IEEE T-ASE, Automatica               | IROS, ICRA               | Automation & control systems      |
| Bayesian AI                   | Bayesian Analysis, JMLR              | UAI, AISTATS             | Probabilistic methods community   |
| Cognitive / Neuro-Symbolic AI | Artificial Intelligence (AIJ), JAIR  | AAAI, NeurIPS            | Hybrid reasoning community        |
| Conversational AI             | ACM TOIS, CL (MIT)                   | ACL, EMNLP, SIGDIAL      | NLP & dialogue community          |
| Evolutionary AI               | Evolutionary Computation (MIT), TEVC | GECCO, PPSN              | EC community                      |
| Explainable AI                | ACM TIST, Nature MI                  | FAccT, AAAI, NeurIPS     | XAI & responsible AI              |
| Federated AI                  | IEEE TIFS, JMLR                      | NeurIPS, ICML, PPML      | Privacy & distributed learning    |
| Generative AI                 | JMLR, TMLR                           | NeurIPS, ICML, ICLR      | Foundation model community        |
| Multimodal AI                 | IEEE TPAMI, IJCV                     | CVPR, NeurIPS, ACL       | Vision-language community         |
| Optimisation / OR AI          | Operations Research, INFORMS         | CPAIOR, CP, AAAI         | OR & mathematical optimisation    |
| Physical / Embodied AI        | IJRR, IEEE T-RO                      | ICRA, IROS, CoRL         | Robotics community                |
| Predictive AI                 | JMLR, IEEE TKDE                      | NeurIPS, ICML, KDD       | Core ML classification/regression |
| Reactive AI                   | Real-Time Systems, ACM TECS          | RTSS, EMSOFT             | Real-time systems community       |
| Recommendation AI             | ACM TOIS, RecSys                     | RecSys, WWW, KDD         | IR & recommender community        |
| Reinforcement Learning AI     | JMLR, TMLR                           | NeurIPS, ICML, ICLR      | Core RL community                 |
| Scientific AI                 | Nature Computational Science         | NeurIPS AI4Science, ICML | Scientific ML community           |
| Symbolic AI                   | Artificial Intelligence (AIJ), JAIR  | AAAI, IJCAI, KR          | Knowledge representation          |

---

## Checklist — Before Submitting Each Paper

- [ ] README.md research plan completed and reviewed
- [ ] Literature search executed (Scopus, IEEE Xplore, ACM DL, arXiv)
- [ ] Tech stack hands-on phases 1–4 completed with working code/demos
- [ ] Benchmark data collected and reproduced where possible
- [ ] Market data sourced from 3+ analyst reports
- [ ] LaTeX manuscript written in `acmart` format
- [ ] Figures created (TikZ/PGFPlots or Draw.io)
- [ ] BibTeX bibliography complete with 50+ references
- [ ] Supplementary materials prepared
- [ ] Pre-print posted to assigned server (see {server}-pre-print/README.md)
- [ ] Submitted to assigned journal (see {journal}-peer-review/README.md)
- [ ] LinkedIn post drafted (see LINKEDIN-POSTS.md)

---

*Hameem M Mahdi, B.S.C.S., M.S.E., Ph.D. — AI Systems Landscape 2026*
