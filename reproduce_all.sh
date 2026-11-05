#!/usr/bin/env bash
# =====================================================================================
# reproduce_all.sh  -  rebuilds EVERY component of AJSE Paper 1999 from the raw data:
#   statistics and models -> Table I -> figures -> corrected manuscript (clean + tracked
#   changes vs the published article) -> response letter -> independent check -> comparison
#   with the reference outputs that were submitted.
#
# Usage (from this folder):
#   bash reproduce_all.sh            full run (about 45 min on 2 CPU cores)
#   bash reproduce_all.sh --fast     quick smoke test (fewer permutations; numbers will differ slightly)
#   bash reproduce_all.sh --docs     documents only, re-using existing results/ (about 1 min)
#
# Needs: Python 3.13 (pip install -r requirements.txt), Node.js >= 18 (npm install),
#        pandoc (for the checks), LibreOffice (optional, for PDF export).
# =====================================================================================
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p manuscript_build/output results figures/revised   # generated folders (git-ignored or empty in a fresh clone)
MODE="${1:-}"
step() { printf '\n========== %s ==========\n' "$1"; }

step "0. Environment"
python3 --version; node --version || { echo "Node.js is required for the manuscript build"; exit 1; }
python3 -c "import sklearn, xgboost, lightgbm, scipy, pandas, matplotlib, openpyxl" 2>/dev/null \
  || { echo "Installing Python packages..."; pip install -r requirements.txt; }
[ -d node_modules/docx ] || npm install --no-audit --no-fund

if [ "$MODE" != "--docs" ]; then
  step "1. Statistics and models  (scripts/revision/r3_inquiry_reanalysis.py)"
  if [ "$MODE" = "--fast" ]; then python3 scripts/revision/r3_inquiry_reanalysis.py --fast; else python3 scripts/revision/r3_inquiry_reanalysis.py; fi
fi
step "2. Table I cohort counts  (scripts/revision/r3_table1_cohort.py)"
python3 scripts/revision/r3_table1_cohort.py
step "3. Figures  (scripts/revision/r3_figures.py)"
python3 scripts/revision/r3_figures.py

step "4. Corrected manuscript: content from the published text + results"
python3 manuscript_build/content_pub.py
python3 manuscript_build/diff_prep.py
node manuscript_build/render_pub.js clean   manuscript_build/output/AJSE_1999_Corrected_Manuscript_CLEAN.docx
node manuscript_build/render_pub.js tracked manuscript_build/output/AJSE_1999_Corrected_Manuscript_TRACKED_vs_Published.docx

step "5. Response letter"
python3 manuscript_build/response_pub.py

step "6. PDF export (optional, needs LibreOffice)"
if command -v soffice >/dev/null 2>&1; then
  (cd manuscript_build/output && soffice --headless --convert-to pdf AJSE_1999_Corrected_Manuscript_CLEAN.docx >/dev/null 2>&1 \
     && soffice --headless --convert-to pdf AJSE_1999_Corrected_Manuscript_TRACKED_vs_Published.docx >/dev/null 2>&1 && ls *.pdf) || echo "PDF export skipped"
else echo "LibreOffice not found: PDF export skipped"; fi

step "7. Independent check (numbers recomputed from raw files, searched in the documents)"
python3 manuscript_build/independent_check_pub.py | tee manuscript_build/output/independent_check.log | tail -12

step "7b. Manuscript consistency tests (figures, tables, equations, references, headline numbers)"
python3 manuscript_build/verify_manuscript_consistency.py | tail -3

step "8. Comparison with the submitted reference outputs"
python3 manuscript_build/verify_against_reference.py || true
step "9. E-mail package for the Editorial Desk"
python3 manuscript_build/make_send_package.py || echo "send package step needs LibreOffice and pandoc"
echo; echo "Outputs: results/, figures/revised/, manuscript_build/output/ (SEND_TO_AJSE/ = files to attach)"
