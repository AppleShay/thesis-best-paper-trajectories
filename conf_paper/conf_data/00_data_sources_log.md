
## Notebook 02 — Author profiles & career stage
- Author-paper pairs built from 903 matched award papers (excluded 22 unmatched from notebook 01).
- Total author-paper pairs: 3150; unique authors: 2710.
- Author entries skipped due to missing OpenAlex author id: 52.
- OpenAlex /authors profiles fetched: 2701 (0 failed batches).
- Precise first-pub-year fallback lookups (/works endpoint): 13 authors.
- Authors still missing first_pub_year after fallback: 0.
- Career stage counts: {'Senior': 2313, 'Junior': 828, None: 9}.
- Definition: career_age_at_award = award_year - first_pub_year (absolute first pub, any field).
- Junior: career_age <= 5. Senior: career_age >= 6.
- LIMITATION: first_pub_year not restricted to CS-relevant works; may inflate career age for authors with prior publications in unrelated fields.

- NOTE: The 9 authors with career_stage=None correspond exactly to the 9 unique author IDs 
  that returned no result from the OpenAlex /authors batch fetch (2710 unique - 2701 fetched = 9). 
  Likely deprecated/merged OpenAlex IDs. These 9 authors' paper rows are retained in the dataset 
  but excluded from Junior/Senior group comparisons.

### Output files (conf_data/)
- 02_award_authors_long.csv — raw author-paper pairs
- 02_author_profiles_raw.csv — OpenAlex author summary stats (pre-fallback)
- 02_author_profiles.csv — with corrected first_pub_year
- 02_award_authors_with_career_stage.csv — final analysis-ready table (Junior/Senior labeled)
## Notebook 03 — Junior (all) vs Senior (all): citations & publications
- Input: 02_award_authors_with_career_stage.csv (3150 rows).
- Dropped 9 rows with unresolved career_stage (per notebook 02 log).
- Deduplicated to unique-author level for this analysis: 2701 authors (Junior=760, Senior=1941).
- DROPPED h-index and i10-index from comparison: both are cumulative snapshot-at-query-time metrics, confounded by award year spanning 2000-2018 (8 to 26 years of accumulation time).
- Added time-normalized metrics: citations_per_year and works_per_year (= cited_by_count / years_since_first_pub, works_count / years_since_first_pub) as primary comparison metrics; raw cumulative counts kept for descriptive context only.
- All group means reported with bootstrap 95% CIs (5000 resamples), not bare averages.
- Group differences tested via Mann-Whitney U (two-sided) given expected right-skewed distributions.
- LIMITATION: still author-level only (not per-award-paper); an author with multiple award papers is counted once here based on their own overall career metrics.

### Output files
- conf_data/03_junior_vs_senior_summary.csv — means, 95% CIs, medians, n per group/metric
- conf_data/03_mannwhitney_results.csv — significance tests per metric
- conf_figures/03_junior_vs_senior_rates_bar.png — bar chart with error bars
- conf_figures/03_junior_vs_senior_boxplots.png — distribution boxplots
## Notebook 04a — Event-study trajectory plot (thesis-style)
- Reads 04_trajectory_long.csv, generated from notebook 04's in-memory all_works (no re-fetch).
- Trajectory rows: 23721, window -5 to +5 years relative to award.
- Chart: median + bootstrapped 95% CI (1000 resamples) per relative year, Junior vs Senior, matching thesis notebook 11 style (11_lift_trajectories.png).

### Output files
- conf_figures/04_lift_trajectories.png — citation & publication trajectories around award year