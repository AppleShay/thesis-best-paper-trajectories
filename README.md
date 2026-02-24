# Best-Paper Awards & Career Trajectories in Computer Science

**Master Thesis** | Uppsala University | Spring 2026  
**Student**: Shaheryar (AppleShay) | **Supervisors**: [Georgios Panayiotou](https://www.uu.se/kontakt-och-organisation/personal?query=N20-1603) & [Davide Vega](https://davidevega.eu/) **Subject Reviewer:** [Arjun Menon](https://www.uu.se/kontakt-och-organisation/personal?query=N26-77)

"Is the Best, the Best?" — Do early-career best-paper awards predict distinct trajectories
(productivity, citations), or merely reflect pre-existing excellence?
[Proposal](docs/thesis_proposal.pdf)

[![OpenAlex](https://img.shields.io/badge/Data-OpenAlex-blue)](https://openalex.org/)
[![Python](https://img.shields.io/badge/Tools-Python%20%7C%20Pandas%20%7C%20scikit--learn-green)](https://python.org/)

---

## 🔬 Research Questions (for now)
- **RQ1**: Is the career of a junior winner (J=True) better than a matched senior co-author
  (J=False) after the award?
- **RQ2**: Is an award-winning paper actually better than non-award papers at the same venue
  and year?

---

## 📊 Current Status — Week 8

| Milestone | Detail |
|-----------|--------|
| Awards corpus | 1,506 cleaned award records, 22 conferences, 2000–2018 |
| OpenAlex match rate | >95% via multi-step ID resolution (SS → DOI → OpenAlex) |
| Junior winners identified | 603 (career age ≤ 5 at award year) |
| Matched control pairs | 603 junior–senior pairs (exact match: conference + year + position) |
| Author-year observations | 8,760 (±5-year trajectories for treated + controls) |
| CORE rankings | All 22 conferences are A* (CORE 2023) |
| Key finding so far | Juniors show a sharp, temporary citation spike at award year (~3× controls); no lasting publication gap |

---

## 🗂️ Pipeline Overview

| Notebook | Description |
|----------|-------------|
| `01_openalex_demo` | API exploration |
| `02_datacollection` | Scrape & raw ingestion |
| `03_datacleaning` | Standardise awards table |
| `04_matching_to_openalex` | Multi-step ID resolution |
| `05_junior_author_matched` | Junior annotation (position, career age) |
| `06_junior_profiles` | Pull OpenAlex author profiles |
| `07_junior_eda` | Trajectory plots, EDA |
| `08_control_matching` | 1:1 matched control group |
| `09_did_analysis` | Difference-in-differences analysis |
| `10_core_rankings` | CORE 2023 join, h-index removal |

---

## 📁 Structure

```
thesis-best-paper-trajectories/
│
├── data/
│   ├── raw/                          # Original scraped award records
│   ├── cleaned/                      # huang_awards_cleaned.csv
│   ├── matched/                      # Junior authors, matched pairs,
│   │                                 # CORE rankings lookup
│   ├── profiles/                     # OpenAlex author profiles (juniors + controls)
│   └── figures/
│       ├── 01_career_age.png         # Career age distribution
│       ├── 02_per_year.png           # Junior winners per year
│       ├── 03_trajectory.png         # Aggregate citation/pub trajectories
│       ├── 05_position.png           # Author position stacked bar
│       ├── 09_did_cites.png          # DiD plot — citations
│       ├── 09_did_pubs.png           # DiD plot — publications
│       └── _archived/                # Deprecated figures (e.g. h-index)
│
├── notebooks/                        # 01–10 analysis pipeline
├── docs/                             # Proposal, thesis report, references,
│                                     # meeting notes, timeline
├── src/                              # Shared utilities
├── requirements.txt
└── README.md
```



## Setup & Repro

```bash
git clone https://github.com/AppleShay/thesis-best-paper-trajectories.git
cd thesis-best-paper-trajectories
pip install -r requirements.txt
jupyter notebook notebooks/01_openalex_demo.ipynb
```
