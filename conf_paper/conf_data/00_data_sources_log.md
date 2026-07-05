
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

### Output files (conf_data/)
- 02_award_authors_long.csv — raw author-paper pairs
- 02_author_profiles_raw.csv — OpenAlex author summary stats (pre-fallback)
- 02_author_profiles.csv — with corrected first_pub_year
- 02_award_authors_with_career_stage.csv — final analysis-ready table (Junior/Senior labeled)