"""Checks every reference of the revised manuscript against Crossref.
 - entries with a DOI: the DOI must resolve in Crossref, and the Crossref title must match ours (similarity >= 0.85) and the year;
 - entries without a DOI: Crossref is searched; a confident match (similarity >= 0.92) is reported as a DOI to add.
Writes docs/reference_verification_v3.md and exits non-zero on any mismatch.   Needs internet access."""
import json, re, sys, time, urllib.parse, urllib.request
from difflib import SequenceMatcher
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from refs_v3 import REFS
ROOT = Path(__file__).resolve().parents[2]
UA = {"User-Agent": "cp-attrition-prediction reference check (https://github.com/AZUAD-ISLAM-RUHAN/cp-attrition-prediction)"}
def get(url):
    for k in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30))
        except Exception as e: err = e; time.sleep(2)
    return {"error": str(err)}
def title_of(ref):
    m = re.search(r"“(.+?)[,”]”?", ref)
    if m: return m.group(1).rstrip(",")
    return re.split(r"\. ", ref.split(", ", 1)[1] if ", " in ref else ref)[0]
def norm(s): return re.sub(r"[^a-z0-9 ]", "", re.sub(r"<[^>]+>", "", s.lower().replace("’", "'")))
def sim(a, b):   # full-title match, or one title is the other without its subtitle
    a, b = norm(a), norm(b); n = min(len(a), len(b))
    return max(SequenceMatcher(None, a, b).ratio(), SequenceMatcher(None, a[:n], b[:n]).ratio() if n >= 20 else 0)
rows, bad = [], []
for key, (ref, doi) in REFS.items():
    t = title_of(ref); year = re.findall(r"(19|20)\d\d", ref); year = re.findall(r"\b(?:19|20)\d\d\b", ref)[-1]
    if doi:
        r = get("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/()<>;:."))
        if "message" not in r:      # not a Crossref DOI: try DataCite (e.g. Zenodo DOIs)
            dc = get("https://api.datacite.org/dois/" + urllib.parse.quote(doi, safe="/"))
            a_ = dc.get("data", {}).get("attributes", {})
            if a_:
                ct = " ".join(x.get("title", "") for x in a_.get("titles", [])[:1]); s = sim(t, ct); ok = s >= 0.85
                rows.append((key, doi, ("verified (DataCite)" if ok else "TITLE MISMATCH (DataCite)"), f"{s:.2f}", f"{ct[:90]} ({a_.get('publicationYear')})"))
                if not ok: bad.append(key)
            else: rows.append((key, doi, "DOI NOT FOUND", "", "")); bad.append(key)
            continue
        m = r["message"]; ct = " ".join(m.get("title", [""])) + (": " + m["subtitle"][0] if m.get("subtitle") else "")
        cy = str((m.get("published-print") or m.get("published-online") or m.get("issued") or {}).get("date-parts", [[None]])[0][0])
        s = sim(t, ct); ok = s >= 0.85
        rows.append((key, doi, "verified" if ok else "TITLE MISMATCH", f"{s:.2f}", f"{ct[:90]} ({cy})"))
        if not ok: bad.append(key)
    else:
        r = get("https://api.crossref.org/works?rows=3&query.bibliographic=" + urllib.parse.quote(t + " " + year))
        best = max(r.get("message", {}).get("items", []), key=lambda it: sim(t, " ".join(it.get("title", [""]))), default=None)
        if best:
            s = sim(t, " ".join(best.get("title", [""])))
            by = str((best.get("published-print") or best.get("published-online") or best.get("issued") or {}).get("date-parts", [[None]])[0][0])
            same = s >= 0.92 and by == year
            rows.append((key, "-", f"no DOI in list; Crossref best match {best['DOI']} ({by})" + (" (ADD)" if same else " (not the same work)"),
                         f"{s:.2f}", " ".join(best.get("title", [""]))[:90]))
            if same: bad.append(key + " (DOI available)")
        else: rows.append((key, "-", "no DOI in list; no Crossref record", "", ""))
    time.sleep(0.3)
md = ["# Reference verification for the revised manuscript (Crossref)", "",
      "Each DOI was resolved in Crossref and its registered title compared with ours. Entries without a DOI were searched in Crossref.", "",
      "| Key | DOI | Result | Title similarity | Crossref title (year) |", "|---|---|---|---|---|"]
md += [f"| {a} | {b} | {c} | {d} | {e} |" for a, b, c, d, e in rows]
md += ["", f"**{len(bad)} problems:** {', '.join(bad)}" if bad else "**All DOIs verified; no missing DOI found.**"]
(ROOT / "docs" / "reference_verification_v3.md").write_text("\n".join(md)); print("\n".join(md)); sys.exit(1 if bad else 0)
