"""Assembles the e-mail package requested by the Editor (6 Nov 2026) into manuscript_build/output/SEND_TO_AJSE/:
  1 response letter (DOCX + PDF)   2 corrected manuscript, clean (DOCX + PDF)   3 tracked vs published (DOCX + PDF)
  4 ethics approval letter (if docs/REC_Approval_Letter.pdf exists)   5 supplementary verification (DOCX + PDF)
  6 public data and code archive (ZIP, without data/PRIVATE, node_modules or generated output)
Run from the repository root after reproduce_all.sh.   python manuscript_build/make_send_package.py"""
import re, shutil, subprocess, zipfile
from pathlib import Path
import docx
from docx.shared import Pt, Cm
ROOT = Path(__file__).resolve().parents[1]; OUT = ROOT / "manuscript_build" / "output"; SEND = OUT / "SEND_TO_AJSE"
SEND.mkdir(parents=True, exist_ok=True)
def pdf(p):
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(p.parent), str(p)], capture_output=True)

# 1 letter -> DOCX/PDF (line structure of the text file kept; section rules become bold headings)
lines = (OUT / "AJSE_1999_Response_to_Editorial_Inquiry.txt").read_text().split("\n")
d = docx.Document(); st = d.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(11)
for s in d.sections: s.left_margin = s.right_margin = Cm(2.2); s.top_margin = s.bottom_margin = Cm(2)
paras, buf = [], []
for i, l in enumerate(lines):
    nxt = lines[i + 1] if i + 1 < len(lines) else ""
    if set(l.strip()) <= {"=", "-"} and l.strip(): continue
    if not l.strip(): paras.append(("p", " ".join(buf))) if buf else None; buf = []; continue
    if set(nxt.strip()) <= {"=", "-"} and nxt.strip() or (i > 0 and set(lines[i - 1].strip()) == {"="} and l.isupper() is False and l.startswith("ITEM")) or l.startswith("ITEM ") or l.startswith("RESPECTFUL CLOSING"):
        if buf: paras.append(("p", " ".join(buf))); buf = []
        paras.append(("h", l.strip())); continue
    if l.startswith("  - ") or re.match(r"^\s+\([a-f]\)", l) or l.startswith(("To:", "Cc:", "From:", "Re:", "Subject:", "Date:")):
        if buf: paras.append(("p", " ".join(buf))); buf = []
        buf = [l.strip()]; continue
    buf.append(l.strip())
if buf: paras.append(("p", " ".join(buf)))
for kind, text in paras:
    if not text: continue
    p = d.add_paragraph(); r = p.add_run(text)
    if kind == "h": r.bold = True; p.paragraph_format.space_before = Pt(10)
    elif text.startswith("INQUIRY (verbatim)"): r.italic = True
    if text.startswith("- "): p.paragraph_format.left_indent = Cm(0.6)
    p.paragraph_format.space_after = Pt(4)
L = SEND / "1_AJSE_1999_Response_Letter.docx"; d.save(L); pdf(L)

# 2-3 manuscripts
for src, dst in [("AJSE_1999_Corrected_Manuscript_CLEAN", "2_AJSE_1999_Corrected_Manuscript_CLEAN"),
                 ("AJSE_1999_Corrected_Manuscript_TRACKED_vs_Published", "3_AJSE_1999_Corrected_Manuscript_TRACKED_vs_Published")]:
    shutil.copy(OUT / f"{src}.docx", SEND / f"{dst}.docx"); pdf(SEND / f"{dst}.docx")
# 4 ethics approval
rec = ROOT / "docs" / "REC_Approval_Letter_REC-MU-2026-007.pdf"
if rec.exists(): shutil.copy(rec, SEND / "4_Ethics_Approval_REC-MU-2026-007.pdf")
# 5 supplementary verification
md = ["# Supplementary Verification File: AJSE Paper ID 1999", "",
      "This file accompanies the response letter. Every item below can be regenerated from the public archive with `bash reproduce_all.sh`.", ""]
for title, f in [("A. Published values vs. re-execution of the deposited scripts", ROOT / "reference_outputs" / "Published_vs_Reproduced.md"),
                 ("B. Manuscript consistency tests", OUT / "Consistency_Report.md"),
                 ("C. Reference verification", ROOT / "docs" / "reference_verification.md"),
                 ("D. Draft correction notice", ROOT / "docs" / "Draft_Correction_Notice.txt")]:
    if f.exists():
        txt = f.read_text(); txt = re.sub(r"^# .*\n", "", txt, count=1)
        md += [f"## {title}", "", txt if f.suffix == ".md" else "```\n" + txt + "\n```", ""]
ic = OUT / "independent_check.log"
if ic.exists(): md += ["## E. Independent recomputation from the raw files", "", "```", ic.read_text(), "```", ""]
(OUT / "supplement.md").write_text("\n".join(md))
S5 = SEND / "5_Supplementary_Verification.docx"
subprocess.run(["pandoc", str(OUT / "supplement.md"), "-o", str(S5)], check=True); pdf(S5)
# 6 public archive
Z = SEND / "6_AJSE_1999_Public_Data_and_Code.zip"
skip = ("data/PRIVATE", "docs/REC_Approval_Letter", "node_modules", "manuscript_build/output", "manuscript_build/v3/output", "manuscript_build/inputs/AJSE_1999_v2_", "_generated_moved_aside", "__pycache__", ".ipynb_checkpoints")
with zipfile.ZipFile(Z, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(ROOT.rglob("*")):
        rel = p.relative_to(ROOT).as_posix()
        if p.is_file() and not any(rel.startswith(s) or f"/{s}" in rel for s in skip):
            z.write(p, f"cp-attrition-prediction/{rel}")
names = zipfile.ZipFile(Z).namelist()
assert not any("PRIVATE" in n and not n.endswith("README_ADD_RAW_FILES_HERE.txt") for n in names), "private file leaked"
assert not any(n.endswith(".xlsx") for n in names), "timestamped sheet leaked"
for f in sorted(SEND.iterdir()): print(f"{f.stat().st_size/1e6:7.2f} MB  {f.name}")
print(f"TOTAL {sum(f.stat().st_size for f in SEND.iterdir())/1e6:.1f} MB (Gmail limit 25 MB); public zip files: {len(names)}")
