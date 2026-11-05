# Conformance with the AJSE camera-ready template

Reference: `AJSE_Template_2020-OTH.doc` (AJSE's version of the IEEE Transactions template). The rules below come from the template's own styles and instructions. Each one is checked automatically by test group T7 in `manuscript_build/verify_manuscript_consistency.py`, which runs inside `reproduce_all.sh`.

| Element | Template rule | Earlier corrected build (before this check) | Corrected version (now) |
|---|---|---|---|
| Page | US Letter 8.5 × 11 in | A4 (as published) | US Letter |
| Margins | 0.65 in left/right, 0.70 in top/bottom | 0.75 in all round (as published) | as template |
| Columns | two, 0.2 in apart (3.5 in each) | 0.24 in apart (as published) | as template |
| Title | 24 pt, centred | 20 pt (as published) | 24 pt |
| Authors | 11 pt, centred | 10.5 pt (published: 11 pt) | 11 pt |
| Abstract | one paragraph, 150–250 words, self-contained, no abbreviations, footnotes or references; 9 pt bold | 292 words (published: 198) | 249 words, no abbreviations ("area under the receiver operating characteristic curve", "versus") |
| Index Terms | 9 pt bold, alphabetical order | alphabetical | alphabetical (unchanged) |
| Body text | Times New Roman 10 pt, justified, first-line indent 0.14 in, line spacing 1.05 | 9.5 pt (published: 10 pt) | as template |
| Level-1 headings | Roman numeral, 10 pt small caps, centred | not small caps (published: small caps) | small caps |
| Level-2 headings | 10 pt italic, lettered "A.", "B.", ... | not lettered (as published) | lettered |
| Unnumbered headings | References, Appendix, Acknowledgment: small caps, centred | "VII. References" (as published) | "References" (unnumbered) |
| Equations | numbered "(1)" flush right; cited as "(1)", not "Eq. (1)" | "Eq. (1)", "Eq. (2)" in Table VI | "(1)", "(2)" |
| Figure captions | 8 pt, below the figure, "Fig. 1." | as template | as template |
| Table titles | "TABLE I" on its own line, then the title in small caps, 8 pt, centred, above the table | one line, not small caps (published: "TABLE I" on its own line) | as template |
| Table text | 8 pt | 6–7 pt (published: 7–8 pt) | 8 pt |
| References | 8 pt, bracketed number as a hanging column | 7.5 pt (published: 8 pt) | 8 pt |
| Biographies | photo 1.0 × 1.25 in, text 8 pt | photo 0.71 × 0.89 in, 7.5 pt (published: photo 1.0 × 1.25 in) | as template |
| Figure size | one column (3.5 in) or page width (7.16 in) | 3.3 in / 4.6 in (published: 3.18 in / 5.31–6.56 in) | 3.45 in / 7.0 in, drawn at printed size |
| Figure resolution | colour figures at least 300 dpi | 213–419 dpi at printed size (published: 211–562 dpi; Fig. 1 at 211) | 400 dpi |
| Figure fonts | Times New Roman, Helvetica, Arial, Cambria or Symbol; labels about 8–10 pt | DejaVu Sans, 5.2–7.5 pt | Arial (its metric twin Liberation Sans where Arial is not installed), 7.5–9 pt |
| Axis labels | words, not symbols; units in parentheses | e.g. "% flagged (ATR < 0.5)", raw feature names | e.g. "Users with activity decay (%)", feature names in words |
| Multipart figures | parts labelled (a), (b), ... centred below each part in 8 pt Times New Roman | not labelled | labelled, and named in the caption |
| Language | American spelling; "Acknowledgment"; "whereas" for contrast; "approximately", not "essentially" | mixed (modelling, analysed, practised, Acknowledgement), as published | American spelling in the text; titles of cited works kept as published |

"Earlier corrected build" is the version prepared on 6 November 2026 before this check. It had kept the published page set-up (A4, 0.75 in margins, 20 pt title) but drifted from the published article in several type sizes; the published values are given in brackets. Measured from `manuscript_build/inputs/AJSE_Camera_Ready_PUBLISHED.docx`.

Not changed:

- **Biographies and affiliations stay in the published arrangement.** The template places affiliations in an unnumbered first-page footnote; here they follow the index terms in 8 pt, as in the published version.
- **The correction notice box on page 1 is kept.** It identifies the version as the response to the inquiry and can be removed if the Desk prefers.
- **The serial comma is not imposed.** The template prefers "A, B, and C". Applying it to every list in the published text would add many tracked edits that are not corrections.
