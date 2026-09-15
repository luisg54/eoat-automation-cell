"""Preserve the interrupted assembly and close document windows to release RAM."""
from build_native import ROOT,connect,call,integer_ref,nothing
sw=connect(); docs=[]; d=call(sw,'GetFirstDocument')
while d:
    docs.append((d,call(d,'GetType'),call(d,'GetPathName'),call(d,'GetTitle')))
    d=call(d,'GetNext')
for d,kind,path,title in docs:
    if kind==2 and not path:
        out=ROOT/'development-debug/D_partial_insertion.SLDASM'
        if not d.Extension.SaveAs(str(out),0,1,nothing(),integer_ref(),integer_ref()): raise RuntimeError('Partial save failed')
        print('Preserved',title,'components',len(call(d,'GetComponents',False)),flush=True)
        sw.CloseDoc(str(out))
for d,kind,path,title in docs:
    if kind==1 and path and str(ROOT).lower() in path.lower():
        sw.CloseDoc(path)
print('Released D component document windows',len(docs),flush=True)
