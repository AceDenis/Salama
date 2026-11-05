"""Fill the table of contents of a .docx using LibreOffice (page numbers included). Usage: python3 update_toc.py in.docx out.docx"""
import subprocess, sys, time, os, uno
from com.sun.star.beans import PropertyValue
src, dst = map(os.path.abspath, sys.argv[1:3])
p = subprocess.Popen(["soffice", "--headless", "--norestore", "--accept=socket,host=localhost,port=2002;urp;"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
ctx = None
for _ in range(40):
    try:
        local = uno.getComponentContext(); res = local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local)
        ctx = res.resolve("uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext"); break
    except Exception: time.sleep(0.5)
desk = ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
pv = lambda n, v: PropertyValue(Name=n, Value=v)
doc = desk.loadComponentFromURL("file://" + src, "_blank", 0, (pv("Hidden", True),))
idx = doc.getDocumentIndexes()
for i in range(idx.getCount()): idx.getByIndex(i).update()
doc.refresh()
doc.storeToURL("file://" + dst, (pv("FilterName", "MS Word 2007 XML"),))
doc.close(True)
try: desk.terminate()
except Exception: pass
p.wait(timeout=20)
print("toc updated ->", dst)
