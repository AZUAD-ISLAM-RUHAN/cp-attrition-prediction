# Ethics approval, consent and data handling

## Approval
- **Body:** Research Ethics Committee (REC), Metropolitan University, Bateshwar, Sylhet-3104, Bangladesh. Convener: Professor Dr. Mohammad Jamal Uddin.
- **Reference:** REC/MU/2026/007.
- **Approved project:** undergraduate thesis research project "Predicting Student Attrition in Competitive Programming: A Study Integrating Survey Insights and Global Behavioral Logs". The applicant was Azuad Islam Ruhan (ID 231-115-276) "and others", Department of CSE.
- **Decision:** approved by the REC resolution of its meeting on **24 February 2026**. The formal approval letter was issued on **17 March 2026**. The approval is valid for one year.
- **Principles named in the approval:** informed consent; voluntary participation; confidentiality and privacy protection; data security and responsible data management; respect for human dignity and rights; academic integrity.

## Timeline (from the response-sheet timestamps)
| Event | Date |
|---|---|
| REC meeting resolution approving the study | 24 Feb 2026 |
| First survey response | 6 Mar 2026 |
| Responses received 6–12 Mar 2026 | 84 of 96 |
| REC approval letter issued | 17 Mar 2026 |
| Last survey response | 2 Apr 2026 |

Data collection started after the REC resolution of 24 February 2026, which is the approval decision. The letter of 17 March 2026 formally communicates that decision. The published article and an earlier version of this README said "approved … on 17 March 2026", giving only the letter date. That wording could be read as data collection having started before approval. It has been corrected here and in the manuscript.

**Published-article wording corrected:** "on 17 March 2026" (letter date only); "multi-institutional" (institution was not recorded); "account handles are stored solely to deduplicate records" (handles are pseudonymised in all released files).

## Survey: recruitment, consent and anonymity
- **Instrument:** a Google Form, "Survey on Predicting the Competitive Programming Journey", with branching on Q6 (see `survey_instrument.md`).
- **Recruitment:** an online link shared with computer science students at universities in Bangladesh. The form did not record institution, so neither a number of institutions nor per-institution counts are reported.
- **Consent:** as stated by the authors in the published article: the landing page gave the purpose of the study, said that responses would be used for academic research, and said that submission constituted consent. Respondents could close the form at any point without submitting, and no incentive was offered. A screenshot of the form can be provided on request.
- **Identifiers:** the questionnaire asked for no name, student ID, e-mail address or institution (the response sheet contains no such column). The public file drops the submission timestamps; `data/survey_response_dates.csv` gives only the calendar date of each response (no time of day), so the collection window can be checked publicly. The timestamped original is kept by the corresponding author and available to the Editorial Desk on request.
- **Participants:** university students; age was not asked.

## Codeforces data
- **Source:** public endpoints of the Codeforces API (`user.ratedList`, `user.info`, `user.status`, `user.rating`). Only publicly visible, platform-generated activity data was used, with no private messages or profile text beyond rating fields.
- **Rate limiting:** requests were spaced (≥1 s, adaptive back-off) in line with the API's published call limits.
- **Pseudonymisation:** handles are replaced by a salted SHA-256 prefix in every released file. The salt and mapping are not distributed. No attempt was made to link Codeforces accounts to survey respondents, and the two datasets share no identifiers.
- **Raw dumps:** `users_info.jsonl`, `users_dynamic.jsonl` and `handle_pool.txt`, as produced by `01_collect_and_build_features.ipynb`. They are provided privately to the editorial desk for verification. They are not redistributed publicly because they contain handles. `scripts/revision/r0_rebuild_from_raw_jsonl.py` rebuilds every stage count from them.

## Sampling frame and observation time (Codeforces)
- **Frame:** all rated accounts returned by `user.ratedList?activeOnly=false` on the collection date. From this list, a pool of 26,000 handles was drawn, stratified by current rating band (Newbie … GMplus), proportional to band size with a minimum of 50 per band (`random.seed(42)`).
- **Gate:** current rating >0 and <2400, at least 5 rated contests, at least 1 accepted submission, and a non-empty submission history.
- **T_obs:** the moment the feature file was built (`datetime.now()` in cell 5 of the collection notebook). The published article describes it as "the date on which the API crawl completed", which is not what the code does. Account age and months since the last submission are measured to T_obs. It falls in June 2026, before 24 June 2026, when the first figures were produced from the file; the exact time was not recorded, which is why `r0_rebuild_from_raw_jsonl.py` takes T_obs as an explicit argument.
