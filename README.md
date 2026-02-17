# Best-Paper Awards & Career Trajectories in Computer Science

**Master Thesis** | Uppsala University | Spring 2026  
**Student**: Shaheryar (AppleShay) | **Supervisors**: Georgios Panayiotou, Arjun Menon

"Is the Best, the Best?" — Do early-career best-paper awards predict distinct trajectories (productivity, citations, disruption), or reflect pre-existing excellence? [Proposal](https://github.com/AppleShay/thesis-best-paper-trajectories/docs/thesis_proposal.pdf)

[![OpenAlex](https://img.shields.io/badge/Data-OpenAlex-blue)](https://openalex.org/) [![Python](https://img.shields.io/badge/Tools-Python%20%7C%20Pandas%20%7C%20NetworkX-green)](https://python.org/)

## Week 7 Pilot Results (CHI, ICSE, ICML, NeurIPS, OSDI, PLDI, SIGMOD, SOSP; 2000-2018)
- **Scraped**: 1,507 awards (1996-2023, 32 confs) via Selenium (52 sections, 28 tables) → **1,506 clean**.
- **Pilot**: 411 awards → **246 matched** (59.9%, 99.8% fuzzy score).
- **Juniors** (0-5 yrs career): **196 total** | 0.80/award | 48% 1st-auth, 34% 2nd, 17% 3rd | Even age spread | Top inst: CMU (10).

| Metric | Value |
|--------|-------|
| Awards Scraped | 1,507 → 1,506 |
| Pilot Matched | 246/411 (59.9%) |
| Juniors ID'd | 196 (0.80/award) |
| 1st-Auth % | 48% |

**Next**: Controls matching, pre/post trajectories (CD index, networks).

## 📁 Structure
- `data/raw/`: 1,507 award scrapes.
- `data/cleaned/`: 1,506 + pilot/juniors CSVs.
- `data/matched/`: 246/411 + unmatched.
- `notebooks/`: 01-demo → 05-juniors pipeline.
- `presentation/`: Week 7 slides (Thu meeting).

## Setup & Repro
```bash
git clone https://github.com/AppleShay/thesis-best-paper-trajectories.git
cd thesis-best-paper-trajectories
pip install -r requirements.txt  # Pandas, openalex, fuzzywuzzy, selenium
jupyter notebook notebooks/01_openalex_demo.ipynb
```


