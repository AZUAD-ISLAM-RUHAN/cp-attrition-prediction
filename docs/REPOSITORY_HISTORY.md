# Repository history

On 6 November 2026 the `main` branch of this repository was replaced by a single commit (`792cd71`, "Replace repository with updated version"). That commit removed the earlier history from `main`. We regret this. The history has not been rewritten since then, and it will not be.

The earlier history has been restored, unchanged, in the branch **`history-2026-09`**. It holds 26 commits made on 19 September 2026, each with its original hash.

## How to check that the data have not changed since 19 September 2026

The September commits were made through GitHub's web interface. GitHub signs such commits with its own key, and the signature covers the commit date and the full file tree, so an author cannot forge or back-date it. On GitHub, each of these commits shows a green **Verified** badge.

To check from the command line:

```bash
git clone https://github.com/AZUAD-ISLAM-RUHAN/cp-attrition-prediction
cd cp-attrition-prediction
git fetch origin history-2026-09:history-2026-09

# 1. import GitHub's public key for web commits (fingerprint 9684 79A1 AFF9 27E3 7D1A 566B B569 0EEE BB95 2194)
curl -s https://github.com/web-flow.gpg | gpg --import

# 2. check GitHub's signature on the first upload (19 Sep 2026, 01:20 +06:00)
git verify-commit cf36fb7                  # expect: Good signature from "GitHub <noreply@github.com>"

# 3. compare the data files in that upload with the current ones (identical hashes = identical bytes)
git rev-parse cf36fb7:cf_attrition_features.csv      main:data/cf_attrition_features.csv
git rev-parse cf36fb7:survey_responses.csv           main:data/survey_responses.csv
```

| File | Git object hash on 19 Sep 2026 (`cf36fb7`) | Git object hash now (`main`) |
|---|---|---|
| `cf_attrition_features.csv` | `368a284273070bb89b444ccf1e31d820fbf6850a` | `368a284273070bb89b444ccf1e31d820fbf6850a` |
| `survey_responses.csv` | `070b457b642e2765729388b5421c127a769f2685` | `070b457b642e2765729388b5421c127a769f2685` |

SHA-256 of the current files: `cf_attrition_features.csv` 29ab43fe206a92a22ad77ac4ef128d0b31e7f355828c18e68bab24e27ae485c5; `survey_responses.csv` a70b3e6569947734f138173946908392945ccc6a547c63f9a63e68d242f8f48f.

## Versions cited in correspondence with AJSE

| Commit | Date | What it is |
|---|---|---|
| `cf36fb7` … `06aed3d` (branch `history-2026-09`) | 19 Sep 2026 | first public upload and file reorganisation |
| `792cd71` (tag `v2.0-reviewed`) | 6 Nov 2026 | version examined by the reviewer (report of 8 Nov 2026) |

Later versions are added as normal commits and released through Zenodo with a DOI.
