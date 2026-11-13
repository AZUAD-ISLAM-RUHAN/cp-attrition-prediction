"""Compares a fresh run with reference_outputs/ (the outputs behind the submitted documents).
Numbers: every numeric leaf of r3_results.json must agree to 3 decimals.
Documents: plain text of the regenerated manuscript and letter must be identical.
    python manuscript_build/verify_against_reference.py      (run from the repository root)"""
import json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; REF = ROOT / "reference_outputs"; OUT = ROOT / "manuscript_build" / "output"
ok = True
def walk(a, b, path=""):
    d = []
    if isinstance(a, dict):
        for k in a:
            if k == "environment": continue
            d += walk(a[k], b.get(k) if isinstance(b, dict) else None, f"{path}/{k}")
    elif isinstance(a, list):
        if not isinstance(b, list) or len(a) != len(b): return [(path, "length/type differs")]
        for i, (x, y) in enumerate(zip(a, b)): d += walk(x, y, f"{path}[{i}]")
    elif isinstance(a, (int, float)) and not isinstance(a, bool):
        if not isinstance(b, (int, float)) or abs(round(a, 3) - round(b, 3)) > 0.0011: d.append((path, a, b))
    return d
for name in ["r3_results.json", "r3_table1_cohort.json"]:
    new = ROOT / "results" / name
    if not new.exists(): print("MISSING", new); ok = False; continue
    diff = walk(json.load(open(REF / name)), json.load(open(new)))
    print(f"{name}: {'IDENTICAL (3 d.p.)' if not diff else f'{len(diff)} differences'}"); ok &= not diff
    for x in diff[:15]: print("   ", x)
def txt(docx, *extra): return subprocess.run(["pandoc", str(docx), "-t", "plain", "--wrap=none", *extra], capture_output=True, text=True).stdout
pairs = [(OUT / "AJSE_1999_Corrected_Manuscript_CLEAN.docx", REF / "Corrected_Manuscript_CLEAN.txt", []),
         (OUT / "AJSE_1999_Corrected_Manuscript_TRACKED_vs_Published.docx", REF / "Corrected_Manuscript_TRACKED.txt", ["--track-changes=all"])]
for docx, ref, extra in pairs:
    if not docx.exists(): print("MISSING", docx); ok = False; continue
    same = txt(docx, *extra).strip() == ref.read_text().strip(); ok &= same
    print(f"{docx.name}: text {'IDENTICAL' if same else 'DIFFERS'}")
lt = OUT / "AJSE_1999_Response_to_Editorial_Inquiry.txt"
same = lt.exists() and lt.read_text() == (REF / "AJSE_1999_Response_to_Editorial_Inquiry.txt").read_text(); ok &= same
print(f"{lt.name}: {'IDENTICAL' if same else 'DIFFERS'}")
# revised manuscript (v3), reviewer report of 8 Nov 2026
R3 = REF / "v3"
if R3.exists():
    for name in ["r4_results.json", "r4_reviewer_claims.json"]:
        new = ROOT / "results" / name
        if not new.exists(): print("MISSING", new); ok = False; continue
        diff = walk(json.load(open(R3 / name)), json.load(open(new)))
        print(f"v3 {name}: {'IDENTICAL (3 d.p.)' if not diff else f'{len(diff)} differences'}"); ok &= not diff
        for x in diff[:10]: print("   ", x)
    O3 = ROOT / "manuscript_build" / "v3" / "output"
    for docx, ref in [(O3 / "AJSE_1999_v3_Revised_CLEAN.docx", R3 / "Revised_CLEAN.txt")]:
        if not ref.exists(): continue             # the revised manuscript is added with release v3.0
        same = docx.exists() and txt(docx).strip() == ref.read_text().strip(); ok &= same
        print(f"v3 {docx.name}: text {'IDENTICAL' if same else 'DIFFERS'}")
    for f in ["Response_to_Reviewer_v3.md", "claims_table_v3.md"]:
        if not (R3 / f).exists(): continue          # the response is kept out of the public repository
        same = (O3 / f).exists() and (O3 / f).read_text() == (R3 / f).read_text(); ok &= same
        print(f"v3 {f}: {'IDENTICAL' if same else 'DIFFERS'}")
print("\nRESULT:", "ALL OUTPUTS REPRODUCED" if ok else "SOME OUTPUTS DIFFER (see above)")
sys.exit(0 if ok else 1)
