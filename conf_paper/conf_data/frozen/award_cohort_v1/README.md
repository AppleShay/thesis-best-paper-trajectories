# Frozen award cohort: award_cohort_v1

Award-source records from 2000–2018, including unmatched and missing-author-ID records. No deduplication, no author reference-award selection, no new API calls.

Use award_cohort_papers.csv as the paper roster and award_cohort_authorships.csv as the linked authorship roster. Join using cohort_record_id, not conference/year. Exclude is_placeholder rows only when counting known author slots. See manifest.json, data_dictionary.json and issue tables. Do not edit a frozen snapshot in place.
