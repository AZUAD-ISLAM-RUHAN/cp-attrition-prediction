"""arXiv source package of the revised paper (v3, no survey), generated from manuscript_build/v3/output/content_v3.json.
IEEEtran journal style (arXiv supplies IEEEtran.cls); ONE self-contained file: the figures are drawn inside main.tex with
pgfplots (manuscript_build/v3/arxiv_figs_v3.py), references are a thebibliography (no BibTeX, no image files).
Placeholders ⟦...⟧ (author-only facts and the pending B1 analysis) are left out, never printed.
Writes manuscript_build/v3/output/arxiv/main.tex and arxiv_metadata.txt.
Run:  python manuscript_build/v3/arxiv_v3.py   (after content_v3.py)"""
import json, re, shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from arxiv_figs_v3 import FIGS, PREAMBLE   # figures drawn inside main.tex (pgfplots): no image files to lose
V3 = Path(__file__).resolve().parent; ROOT = V3.parents[1]
C = json.load(open(V3 / "output" / "content_v3.json")); OUT = V3 / "output" / "arxiv"
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir(parents=True)          # one file: main.tex (figures are pgfplots code inside it)
PH = re.compile(r"\s*⟦[^⟧]*⟧")

def math_token(base, sub):
    b = (r"\Delta " + (rf"\mathrm{{{base[1:]}}}" if len(base) > 2 else base[1:])) if base.startswith("Δ") else (rf"\mathrm{{{base}}}" if len(base) > 1 else base)
    s = ",".join(rf"\mathrm{{{p}}}" if len(p) > 1 else p for p in sub.split(","))
    return f"${b}_{{{s}}}$"
UNI = {"±": r"$\pm$", "×": r"$\times$", "Δ": r"$\Delta$", "†": r"\textsuperscript{\dag}", "‡": r"\textsuperscript{\ddag}", "−": r"$-$",
       "≥": r"$\geq$", "≤": r"$\leq$", "“": "``", "”": "''", "’": "'"}
def tex(s):
    s = PH.sub("", s)
    toks = []
    def keep(m): toks.append(math_token(m.group(1), m.group(2))); return f"\x00{len(toks) - 1}\x00"
    s = re.sub(r"(Δ?[A-Za-z]+)_\{([^}]*)\}", keep, s)
    for a, b in [("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"), ("_", r"\_"),
                 ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}"), ("^", r"\^{}")]:
        s = s.replace(a, b)
    for a, b in UNI.items(): s = s.replace(a, b)
    s = re.sub(r"\|r\|", r"$|r|$", s)
    s = re.sub(r"(?<![\w.$])-(?=\d)", r"$-$", s)               # minus sign, not a hyphen (no line break inside "-0.13")
    s = s.replace(" user i ", " user $i$ ")
    return re.sub(r"\x00(\d+)\x00", lambda m: toks[int(m.group(1))], s)

meta = C["meta"]; L = []
# authors and affiliations come from content_v3.json: all seven authors in the published order (decided 13 Nov 2026)
w = L.append
w(r"\ifdefined\pdfoutput\pdfoutput=1\fi % arXiv: compile with pdfLaTeX (the guard lets XeLaTeX/LuaLaTeX skip it)")
w(r"\documentclass[journal]{IEEEtran}")
w(r"\usepackage[utf8]{inputenc}"); w(r"\usepackage[T1]{fontenc}"); w(r"\usepackage{textcomp}")
w(r"\usepackage{amsmath}"); w(r"\usepackage{graphicx}"); w(r"\usepackage{booktabs}"); w(r"\usepackage{array}")
w(r"\usepackage{url}"); w(r"\usepackage[hidelinks]{hyperref}")
w(PREAMBLE)
w(r"\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}")
w(r"\raggedbottom")
w(r"\begin{document}")
w(r"\title{" + tex(meta["title"]) + "}")
aff = r"\par ".join(tex(a) for a in meta["affil"])
w(r"\author{" + tex(meta["authors"]) + r"\thanks{" + aff + "}}")
w(r"\maketitle")
w(r"\begin{abstract}" + tex(meta["abstract"]) + r"\end{abstract}")
w(r"\begin{IEEEkeywords}" + tex(meta["index"]) + r"\end{IEEEkeywords}")

SKIP_SEC = {"Author Contributions", "Use of AI Tools"}
skip, appendix_started, after_eq = False, False, False
blocks = C["blocks"]; i = 0
EQ = {1: r"\mathrm{SPC}_{i} = S_{i} / C_{i}", 2: r"\mathrm{EDI}_{i} = U_{i} \times \Delta T_{\mathrm{struggle},i}"}
def colspec(widths, total):
    s = sum(widths); n = len(widths)
    return "@{}" + "".join(f"L{{{w_ / s:.3f}\\dimexpr {total}-{2 * (n - 1)}\\tabcolsep\\relax}}" for w_ in widths) + "@{}"
while i < len(blocks):
    b = blocks[i]; t = b["t"]
    if t == "h1":
        name = re.sub(r"^[IVX]+\.\s*", "", b["text"])
        skip = name in SKIP_SEC
        if skip: i += 1; continue
        if name.startswith("Appendix A:"):
            w(r"\appendices"); w(r"\section{" + tex(name.split(":", 1)[1].strip()) + "}"); appendix_started = True
        elif name in ("Data and Code Availability", "Acknowledgment"):
            w(r"\section*{" + tex(name) + "}")
        else:
            w(r"\section{" + tex(name) + "}")
    elif skip: pass
    elif t == "h2":
        nxt = blocks[i + 1] if i + 1 < len(blocks) else {}
        if nxt.get("t") == "p" and PH.sub("", nxt["text"]).strip() == "":      # section that only holds a pending placeholder
            i += 2; continue
        w(r"\subsection{" + tex(b["text"]) + "}")
    elif t == "p":
        s = tex(b["text"]).strip()
        if s:
            if b["text"].startswith("and developed in the public repository") or b["text"].startswith("The pseudonymized"):
                pass
            s = s.replace("are available to the editor and reviewers on request for verification", "are available on reasonable request for verification")
            w(("\\noindent " if b.get("noindent") else "") + s)
    elif t == "eq":
        w(r"\begin{equation}" + EQ[b["num"]] + r"\label{eq:" + str(b["num"]) + r"}\end{equation}")
    elif t == "url":
        w(r"\begin{center}\url{" + b["text"] + r"}\end{center}")
    elif t == "fig":
        name = Path(b["path"]).stem
        cap = re.sub(r"^Fig\.\s*\d+\.\s*", "", b["cap"])
        w(r"\begin{figure}[!t]\centering" + "\n" + FIGS[name](tex) + "\n" + r"\caption{" + tex(cap) + r"}\label{fig:" + name.split("_")[0] + r"}\end{figure}")
    elif t == "tab":
        cap = re.sub(r"^TABLE\s+[IVX]+\.\s*", "", b["cap"]); wide = b.get("wide", True)
        env, width = ("table*", r"\textwidth") if wide else ("table", r"\columnwidth")
        rows = []
        for r in b["rows"]:
            cells = [tex(str(c)) for c in r]
            cells[0] = re.sub(r"^\s{2,}", r"\\quad ", cells[0])
            rows.append(" & ".join(cells) + r" \\")
        w(rf"\begin{{{env}}}[!t]\centering\caption{{{tex(cap)}}}\label{{tab:{len([x for x in L if 'begin{table' in x]) + 1}}}")
        w(r"\footnotesize\setlength{\tabcolsep}{4pt}")
        w(r"\begin{tabular}{" + colspec(b["w"], width) + "}")
        w(r"\toprule " + " & ".join(tex(h) for h in b["head"]) + r" \\ \midrule")
        L.extend(rows); w(r"\bottomrule\end{tabular}")
        if b.get("note"): w(r"\par\vspace{3pt}\begin{minipage}{" + width + r"}\raggedright\scriptsize " + tex(b["note"]) + r"\end{minipage}")
        w(rf"\end{{{env}}}")
    i += 1

w(r"\section*{Use of AI Tools}")
w("ChatGPT (OpenAI) was used for language editing, to refine the research topic and the initial proposal, and to help draft parts of the original "
  "data-collection and analysis code, which the authors reviewed and ran. ChatGPT also suggested references for the Related Work section of version 1; three of them did not exist "
  "and were not checked by the authors. Every reference in this version has been checked against Crossref or DataCite. Grammarly was used for language editing. In preparing this version, "
  "Claude Opus 5.5 (Anthropic) was used to write and debug the analysis, figure and manuscript-generation code and its verification tests, "
  "to check every reference against Crossref, and to draft text; OpenAI tools were also used to organize the \\LaTeX{} source and to debug code. "
  "The authors ran every script, checked the reported numbers against the outputs, and take full responsibility for the content.")
w(r"\begin{thebibliography}{" + str(len(C["refs"])) + "}")
for k, r in enumerate(C["refs"], 1):
    m = re.search(r", doi: (\S+)\.$", r)
    if m:
        doi = m.group(1); body = r[:m.start()]
        w(rf"\bibitem{{r{k}}} " + tex(body) + r", doi: \href{https://doi.org/" + doi.replace("%", r"\%").replace("#", r"\#") + r"}{\nolinkurl{" + doi + "}}.")
    else:
        w(rf"\bibitem{{r{k}}} " + tex(r))
w(r"\end{thebibliography}")
w(r"\end{document}")
src = "\n\n".join(L) + "\n"
assert "⟦" not in src and "⟧" not in src, "placeholder leaked"
(OUT / "main.tex").write_text(src)

plain = lambda s: PH.sub("", s).replace("_{obs}", "_obs")
(V3 / "output" / "arxiv_metadata.txt").write_text(
 "arXiv REPLACEMENT METADATA (arXiv:2608.28618)\n=============================================\n\n"
 f"Title:\n{meta['title']}\n\n"
 f"Authors:\n{meta['authors'].replace(', and ', ', ').replace(' and ', ', ')}\n\n"
 f"Abstract (paste as plain text; {len(meta['abstract'])} characters, arXiv limit 1920):\n{plain(meta['abstract'])}\n\n"
 "Comments:\n"
 "v2: substantially revised. The survey component and its results are removed; the analysis is a rating-restricted comparison of "
 "Codeforces activity with effect sizes, two pre-specified models, robustness checks and an analysis of activity before inactivity. Version 1 cited three works that do not exist; "
 "all references in this version were checked against Crossref/DataCite. Data and code: https://doi.org/10.5281/zenodo.24054464. "
 "8 pages, 4 figures, 5 tables.\n\n"
 "Categories: keep those of version 1 (a replacement keeps its primary category).\n"
 "License: keep the licence chosen for v1 (arXiv does not allow a more restrictive licence on replacement).\n")
print(f"main.tex: {len(src):,} characters; figures embedded: {src.count('begin{tikzpicture}')} pgfplots axes; references: {len(C['refs'])}")
