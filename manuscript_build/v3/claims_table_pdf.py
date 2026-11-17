"""Prints output/claims_table_v3.md as a landscape A4 PDF (output/claims_table_v3.pdf), which is easier to read than
the portrait LibreOffice conversion of the six-column table. Needs pandoc and Python Playwright with Chromium."""
import re, subprocess
from pathlib import Path
O = Path(__file__).resolve().parent / "output"
html = subprocess.run(["pandoc", str(O / "claims_table_v3.md"), "-f", "gfm", "-t", "html5", "-s",
                       "--metadata", "title=AJSE Paper ID 1999 - Claims table"], check=True, capture_output=True, text=True).stdout
CSS = """<style>
body{font-family:'DejaVu Serif','Times New Roman',serif;font-size:8.6pt;max-width:none;margin:0;padding:0;color:#000;background:#fff}
header#title-block-header{display:none} h1{font-size:13pt;margin:0 0 4pt} p{margin:0 0 6pt}
table{border-collapse:collapse;width:100%;table-layout:fixed}
th,td{border:0.6pt solid #555;padding:2.5pt 4pt;vertical-align:top;text-align:left;overflow-wrap:break-word}
th{background:#e8e8e8} tr{page-break-inside:avoid} thead{display:table-header-group} code{font-size:8pt}
</style>"""
COLS = "<colgroup>" + "".join(f'<col style="width:{w}%">' for w in (3, 12, 27, 7, 38, 13)) + "</colgroup>"
html = re.sub(r"<colgroup>.*?</colgroup>", "", html, flags=re.S).replace("</head>", CSS + "</head>").replace("<table>", "<table>" + COLS)
FOOT = ('<div style="font-size:7pt;width:100%;text-align:center">AJSE Paper ID 1999 - Claims of the published article '
        '(reviewer report, section 8, item 6) - page <span class="pageNumber"></span> of <span class="totalPages"></span></div>')
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); pg.set_content(html)
    pg.pdf(path=str(O / "claims_table_v3.pdf"), format="A4", landscape=True, print_background=True, display_header_footer=True,
           header_template="<span></span>", footer_template=FOOT, margin={"top": "12mm", "bottom": "14mm", "left": "10mm", "right": "10mm"})
    b.close()
print("wrote", O / "claims_table_v3.pdf")
