"""Word-level diff of every corrected block against the published paragraph it replaces."""
import json, re, difflib
from pathlib import Path
MB = str(Path(__file__).resolve().parent)
C = json.load(open(f"{MB}/output/content_pub.json"))
PUB = C["pub"]
TOK = re.compile(r"⟦[^⟧]*⟧\S*|\S+\s*")
def toks(s): return TOK.findall(s)
def segs(old, new):
    a, b = toks(old), toks(new)
    sm = difflib.SequenceMatcher(a=[x.strip() for x in a], b=[x.strip() for x in b], autojunk=False)
    out = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal": out.append(["=", "".join(b[j1:j2])])
        if op in ("delete", "replace"): out.append(["-", "".join(a[i1:i2])])
        if op in ("insert", "replace"): out.append(["+", "".join(b[j1:j2])])
    # make sure spaces separate a deletion from following text
    for s in out:
        if not s[1].endswith(" "): s[1] += " "
    if out: out[-1][1] = out[-1][1].rstrip()
    return out
stats = {"kept": 0, "changed": 0, "new": 0, "deleted": 0}
for b in C["blocks"]:
    o = b.get("o")
    newtext = b.get("text") if b["t"] not in ("fig", "tab") else b.get("cap")
    if b["t"] == "del":
        b["segs"] = [["-", PUB[o]]] if PUB[o].strip() else []; stats["deleted"] += 1; continue
    if o is None:
        b["segs"] = [["+", newtext]]; stats["new"] += 1; continue
    old = PUB[o]
    if old == newtext: b["segs"] = [["=", newtext]]; stats["kept"] += 1
    else: b["segs"] = segs(old, newtext); stats["changed"] += 1
C["abstract_segs"] = segs(C["pub_abstract"], C["meta"]["abstract"])
C["ref_segs"] = [segs(C["pub_refs"][k], r) if k < len(C["pub_refs"]) else [["+", r]] for k, r in enumerate(C["refs"])]
json.dump(C, open(f"{MB}/output/content_pub.json", "w"), ensure_ascii=False, indent=1)
print(stats)
