# Best-Paper Awards & Career Trajectories in Computer Science

**Master Thesis** | Uppsala University | Spring 2026
**Student**: Shaheryar (AppleShay) | **Supervisors**: [Georgios Panayiotou](https://www.uu.se/kontakt-och-organisation/personal?query=N20-1603) & [Davide Vega](https://davidevega.eu/) | **Subject Reviewer**: [Arjun Menon](https://www.uu.se/kontakt-och-organisation/personal?query=N26-77)

> *"Is the Best, the Best?"* — Do early-career best-paper awards predict distinct trajectories (productivity, citations), or merely reflect pre-existing excellence?

## 📄 Thesis Significant Milestones
[Proposal](docs/thesis_proposal.pdf)

[80% Thesis](docs/thesis_report_80.pdf)


[![OpenAlex](https://img.shields.io/badge/Data-OpenAlex-blue)](https://openalex.org/)
[![Python](https://img.shields.io/badge/Tools-Python%20%7C%20Pandas%20%7C%20scikit--learn-green)](https://python.org/)

---

## 🔬 Research Questions

- **RQ1**: Is the career of a junior winner (career age ≤ 5 at award year) better than a matched senior co-author after the award — in terms of citations and publications?
- **RQ2**: Is an award-winning paper actually better than non-award papers at the same venue and year — in terms of citation impact and disruption (CD index)?

---

## 📊 Current Status

| Milestone | Detail |
|-----------|--------|
| Awards corpus | 1,506 cleaned award records, 22 conferences, 2000–2018 |
| OpenAlex match rate | >95% via multi-step ID resolution (SemanticScholar → DOI → OpenAlex) |
| Junior winners identified | 603 (career age ≤ 5 at award year) |
| Matched control pairs | 603 junior–senior pairs (exact: conference + year + author position) |
| Author-year observations | 8,760 (±5-year trajectories for treated + controls) |
| CORE rankings | All 22 conferences are A* (CORE 2023) |
| RQ1 key finding | Juniors show a sharp, temporary citation spike at award year (~3× controls); no lasting publication gap |
| RQ2 key finding | Award papers receive significantly more citations than venue-year matched non-award papers; CD index suggests award papers are more disruptive |
| Citation network | Backward (cited BY award papers) + forward (citing award papers) datasets collected and analysed |

---

## 🗂️ Pipeline Overview

### Phase 1 — Data Collection & Cleaning

| Notebook | Description |
|----------|-------------|
| `01_openalex_demo` | OpenAlex API exploration and rate-limit testing |
| `02_datacollection` | Scrape & raw ingestion of award records |
| `03_datacleaning` | Standardise awards table (names, venues, years) |
| `04_matching_to_openalex` | Multi-step ID resolution: SS → DOI → OpenAlex fuzzy match |

### Phase 2 — RQ1: Junior Author Career Trajectories

| Notebook | Description |
|----------|-------------|
| `05_junior_author_matched` | Junior annotation (position, career age), matched senior identification |
| `06_junior_profiles` | Pull OpenAlex author profiles (publications, citations per year) |
| `07_junior_eda` | Trajectory plots, EDA — citation & publication trends ±5 years |
| `08_control_matching` | 1:1 matched control group construction |
| `09_did_analysis` | Difference-in-differences (DiD) — citations and publications |
| `10_core_rankings` | CORE 2023 join, quality validation, h-index removal |
| `11_lift_analysis` | Citation lift ratio (award year vs. baseline) |
| `13_forest_plot` | Forest plot of DiD estimates by conference |
| `14_within_paper_junior_vs_senior` | Within-paper comparison: junior vs. senior co-authors on same award paper |
| `17_heterogeneity_analysis` | Heterogeneity: subgroup DiD by field, position, career stage |
| `23_survival_analysis` | Survival analysis — time to "hit paper" after award |

### Phase 3 — RQ2: Award Paper Quality

| Notebook | Description |
|----------|-------------|
| `12_rq2_validity` | Award vs. non-award paper citation comparison (same venue & year) |
| `15_rq2_award_vs_nonaward` | Extended award vs. non-award analysis with propensity matching |
| `16_conference_award_quality` | Conference-level breakdown of award paper quality |
| `18_top5_hitpapers` | Top-5% "hit paper" rate comparison: award vs. non-award |
| `19_self_citationshare` | Self-citation share analysis for award papers |

### Phase 4 — Disruption (CD Index)

| Notebook | Description |
|----------|-------------|
| `20_cd_index` | CD index computation for award and matched non-award papers |
| `21_cd_research` | Background research and CD index validation |
| `22_cd_std_analysis` | Standardised CD index analysis and visualisation |

### Phase 5 — Citation Network Analysis

| Notebook | Description |
|----------|-------------|
| `24_cited_papers_collection` | Collect papers *cited by* award papers (backward links via OpenAlex `referenced_works`) |
| `25_cited_papers_eda` | EDA on backward citation network — field, year, venue distributions |
| `26_citing_papers_collection` | Collect papers *citing* award papers (forward links via OpenAlex `cited_by`) |
| `27_citation_network_analysis` | Full citation network analysis: year dist, field dist, connector papers, citation lag heatmap, topic shift heatmap |

---

## 📁 Repository Structure

```
thesis-best-paper-trajectories/
│
├── data/
│   ├── raw/                        # Original scraped award records
│   ├── cleaned/                    # huang_awards_cleaned.csv
│   └── matched/                    # All enriched datasets:
│       ├── huang_matched_openalex.csv          # Award papers + OpenAlex IDs
│       ├── junior_authors_matched.csv          # Junior author annotations
│       ├── control_pairs.csv                   # Matched junior–senior pairs
│       ├── author_year_trajectories.csv        # ±5-year author trajectories
│       ├── award_paper_citations.csv           # Award paper citation counts
│       ├── cited_papers.csv                    # Papers cited BY award papers
│       ├── award_to_cited_edges.csv            # Award → cited paper edges
│       ├── citing_papers.csv                   # Papers that CITE award papers
│       ├── award_to_citing_edges.csv           # Award → citing paper edges
│       └── award_papers_field.csv              # OpenAlex field cache for award papers
│
├── figures/                        # All output figures (p01_*.png … p27_*.png)
│
├── notebooks/                      # 01–27 analysis pipeline (see above)
│
├── docs/                           # Proposal, thesis draft, meeting notes, timeline
│
├── src/                            # Shared utility functions
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup & Reproduction

```bash
git clone https://github.com/AppleShay/thesis-best-paper-trajectories.git
cd thesis-best-paper-trajectories
pip install -r requirements.txt
jupyter notebook notebooks/01_openalex_demo.ipynb
```

> **Note**: Notebooks 24–27 require an OpenAlex API key (set `API_KEY` and `MAILTO` at the top of each notebook). Data files in `data/matched/` are not committed to the repo due to size — contact the author for access.
