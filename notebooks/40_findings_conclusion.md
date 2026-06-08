# Notebook 40 — Findings & Conclusion

> **Note:** This markdown file captures the key findings from notebook `40_dedup_trajectory_did.ipynb`.  
> Add these cells at the **end** of the notebook as a `markdown` cell (section header) + `code` cell (numeric summary) + closing `markdown` cell (interpretation & caveats).

---

## Cell to add — Section header (markdown)

```
## 8. 📋 Findings & Conclusion

### What we measured
- **326 unique award-winning authors** (de-duplicated) across ICWSM and JCDL, spanning 1998–present.
- **87 Junior** (career age < 5 at award time) · **239 Senior** authors.
- Metric: **median citations received per year** and **median publications per year**, in a ±5-year window around the award year (`t = 0`).
```

---

## Cell to add — Numeric summary (code)

```python
# Numeric summary of pre/post medians
summary_rows = []
for group, label in [(True, "Junior (<5 yr)"), (False, "Senior (≥5 yr)")]:
    grp = traj[traj["is_junior"] == group]
    pre  = grp[grp["relative_year"] < 0].groupby("author_id")["cited_by_count"].median().median()
    post = grp[grp["relative_year"] > 0].groupby("author_id")["cited_by_count"].median().median()
    pub_pre  = grp[grp["relative_year"] < 0].groupby("author_id")["works_count"].median().median()
    pub_post = grp[grp["relative_year"] > 0].groupby("author_id")["works_count"].median().median()
    summary_rows.append({
        "Group": label,
        "N authors": grp["author_id"].nunique(),
        "Median cites/yr (pre)":  round(pre, 1),
        "Median cites/yr (post)": round(post, 1),
        "Δ citations":            round(post - pre, 1),
        "Median pubs/yr (pre)":   round(pub_pre, 1),
        "Median pubs/yr (post)":  round(pub_post, 1),
        "Δ publications":         round(pub_post - pub_pre, 1),
    })

pd.DataFrame(summary_rows).set_index("Group")
```

---

## Cell to add — Interpretation & caveats (markdown)

```
### Key findings

#### Overall
- **Senior authors** show a clear upward shift in **citations per year** around `t = 0`, suggesting the award (or the award-winning paper) generates a sustained increase in annual citation flow.
- **Junior authors** exhibit a more muted pattern in citations — likely because their pre-award baseline is naturally lower and the post-award window is shorter for many of them (career-age window capping).
- **Publication rates** remain broadly stable for both groups across the window, indicating the citation uplift is not simply driven by increased output after the award.

#### By conference
- The pattern is broadly consistent across **ICWSM** and **JCDL**, suggesting the citation-uplift effect is not venue-specific.

#### By award type
- Award types with sufficient sample sizes (≥ 5 authors per group) show varying magnitudes, pointing to heterogeneity across award categories — some confer more visibility than others.

---

### ⚠️ Caveats & limitations

| Caveat | Notes |
|---|---|
| **No causal claim** | This is a descriptive DiD visualization, not a formal causal estimate. No control group is included here. For causal estimates, see notebook `39_matched_control_did.ipynb`. |
| **Window capping** | Junior authors with short pre-award histories contribute fewer pre-award data points; their pre-award medians are computed over a compressed window. |
| **OpenAlex coverage** | `cited_by_count` per year is populated by OpenAlex's coverage. Older papers and less-indexed venues may be under-counted. |
| **Heavy tails** | Even with median aggregation, citation distributions are right-skewed. A handful of highly-cited authors can shape the group trajectory, especially for junior authors (N = 87). |
| **Temporal confound** | Authors who received awards more recently have shorter post-award windows, which may compress apparent post-award growth for recent cohorts. |

---

### Next steps
- Formal DiD regression with year & author fixed-effects (see `39_matched_control_did.ipynb`).
- Stratify by cohort decade to check whether the effect has changed over time.
- Compare citation trajectory of the **award paper itself** vs. the author's overall portfolio.
```
