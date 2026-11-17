#!/usr/bin/env bash
# Builds the revised manuscript (v3) and the response package from results/ (run from the repository root).
#   bash manuscript_build/v3/build_v3.sh            documents only (uses existing results/r4_results.json)
#   bash manuscript_build/v3/build_v3.sh --analyses also re-runs the analyses (about 10 minutes on 2 cores)
set -euo pipefail
cd "$(dirname "$0")/../.."
O=manuscript_build/v3/output; mkdir -p "$O" figures/v3
if [ "${1:-}" = "--analyses" ]; then
  python3 scripts/revision/r4_check_reviewer_claims.py
  python3 scripts/revision/r4_revision_analyses.py
fi
python3 scripts/revision/r4_figures.py
python3 manuscript_build/v3/content_v3.py
CONTENT=$O/content_v3.json node manuscript_build/render_pub.js clean "$O/AJSE_1999_v3_Revised_CLEAN.docx"
BASE=manuscript_build/inputs/AJSE_1999_v2_2026-11-06_CLEAN.docx    # the 6 Nov manuscript: private, not in the public repository
if [ -f "$BASE" ]; then python3 manuscript_build/v3/compare_docs.py "$BASE" "$O/AJSE_1999_v3_Revised_CLEAN.docx" "$O/AJSE_1999_v3_TRACKED_vs_2026-11-06.docx"
else echo "tracked-changes version skipped: $BASE not present (it is supplied privately)"; fi
python3 manuscript_build/v3/arxiv_v3.py          # arXiv LaTeX source (no survey, no placeholders): output/arxiv/
python3 manuscript_build/v3/claims_table_v3.py
[ -f manuscript_build/v3/response_v3.py ] && python3 manuscript_build/v3/response_v3.py   # the response is private: not in the public repository
for f in Response_to_Reviewer_v3 Author_Statement_A1_A2_A9_A10 claims_table_v3; do
  [ -f "$O/$f.md" ] && pandoc "$O/$f.md" -o "$O/$f.docx"
done; true
if command -v soffice >/dev/null 2>&1; then
  (cd "$O" && for f in AJSE_1999_v3_Revised_CLEAN AJSE_1999_v3_TRACKED_vs_2026-11-06 Response_to_Reviewer_v3 Author_Statement_A1_A2_A9_A10 claims_table_v3; do
     [ -f "$f.docx" ] && soffice --headless --convert-to pdf "$f.docx" >/dev/null 2>&1; done; true)
fi
python3 manuscript_build/v3/claims_table_pdf.py || echo "landscape claims table skipped (needs Python Playwright)"
python3 manuscript_build/v3/verify_v3.py
