"""
r3_export_survey_dates.py - writes data/survey_response_dates.csv: the calendar DATE (no time of day)
of each of the 96 survey submissions, in the same row order as data/survey_responses.csv, so that the
collection window (6 Mar - 2 Apr 2026, after the REC resolution of 24 Feb 2026) can be checked publicly.
Needs the private original sheet in data/PRIVATE/. Times of day are dropped as quasi-identifiers.
    python scripts/revision/r3_export_survey_dates.py
"""
import pandas as pd
x = pd.read_excel("data/PRIVATE/Survey_ORIGINAL_with_timestamps.xlsx")
pub = pd.read_csv("data/survey_responses.csv")
assert len(x) == len(pub) and (x.drop(columns=["Timestamp"]).columns == pub.columns).all()
out = pd.DataFrame({"row": range(1, len(x) + 1), "response_date": pd.to_datetime(x.Timestamp).dt.date.astype(str)})
out.to_csv("data/survey_response_dates.csv", index=False)
print(out.response_date.value_counts().sort_index().to_string()); print("first", out.response_date.min(), "last", out.response_date.max())
