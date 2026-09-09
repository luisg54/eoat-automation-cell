"""Preserve the three startup-debug documents before closing them."""
from datetime import datetime
import sys
from build_native import ROOT, connect, call, integer_ref, nothing
sw = connect()
folder = ROOT/'development-debug'/datetime.now().strftime('%Y%m%d-%H%M%S')
folder.mkdir(parents=True, exist_ok=False)
documents = []
doc = call(sw, 'GetFirstDocument')
while doc:
    documents.append(doc)
    doc = call(doc, 'GetNext')
for doc in documents:
    title = call(doc, 'GetTitle')
    if title not in (sys.argv[1:] or ('Part1', 'Part2', 'Part3')):
        continue
    if call(doc, 'GetPathName'):
        print('Skipping document with existing path:', title)
        continue
    suffix = '.SLDASM' if call(doc,'GetType') == 2 else '.SLDPRT'
    path = folder/(title+'_startup-debug'+suffix)
    err, warn = integer_ref(), integer_ref()
    ok = doc.Extension.SaveAs(str(path), 0, 1, nothing(), err, warn)
    if not ok or err.value or not path.is_file():
        raise RuntimeError(f'Save failed; document left open: {title}, {err.value}')
    if call(doc, 'GetSaveFlag'):
        raise RuntimeError('Document remains unsaved; left open: '+title)
    print('Preserved:', path, flush=True)
    sw.CloseDoc(call(doc, 'GetTitle'))
