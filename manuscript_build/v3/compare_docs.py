"""Tracked-changes document: compares NEW against OLD with LibreOffice's Compare Document and saves a .docx
in which every difference is a tracked insertion or deletion (as Word's Review > Compare).
Usage: python manuscript_build/v3/compare_docs.py OLD.docx NEW.docx OUT.docx"""
import subprocess, sys, time, os, uno
from pathlib import Path
from com.sun.star.beans import PropertyValue
def pv(n, v): p = PropertyValue(); p.Name, p.Value = n, v; return p
old, new, out = (Path(a).resolve() for a in sys.argv[1:4])
port = 2002 + os.getpid() % 500
proc = subprocess.Popen(["soffice", "--headless", "--invisible", "--nologo", "--norestore",
                         f"--accept=socket,host=localhost,port={port};urp;StarOffice.ComponentContext"])
ctx = None
for _ in range(60):
    try:
        local = uno.getComponentContext()
        ctx = local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local).resolve(
            f"uno:socket,host=localhost,port={port};urp;StarOffice.ComponentContext"); break
    except Exception: time.sleep(1)
smgr = ctx.ServiceManager
desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
doc = desktop.loadComponentFromURL(new.as_uri(), "_blank", 0, (pv("Hidden", True),))
disp = smgr.createInstanceWithContext("com.sun.star.frame.DispatchHelper", ctx)
disp.executeDispatch(doc.getCurrentController().getFrame(), ".uno:CompareDocuments", "", 0, (pv("URL", old.as_uri()), pv("NoAcceptDialog", True)))
doc.storeToURL(out.as_uri(), (pv("FilterName", "MS Word 2007 XML"),))
doc.close(True)
try: desktop.terminate()
except Exception: pass
proc.wait(timeout=60)
print("tracked-changes document:", out)
