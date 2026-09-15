"""Import the supplier STEP, preserving and closing only saved revision-C documents."""
import json
from pathlib import Path
from build_native import ROOT,connect,call,integer_ref,nothing
sw=connect()
docs=[]; d=call(sw,'GetFirstDocument')
while d:
    path=call(d,'GetPathName')
    if path and Path(path).resolve().is_relative_to((ROOT.parent/'arm-v3').resolve()):
        if call(d,'GetSaveFlag'): raise RuntimeError('Unsaved user changes: '+path)
        docs.append((call(d,'GetType'),path))
    d=call(d,'GetNext')
for kind,path in sorted(docs,reverse=True): sw.CloseDoc(path)
print('Closed',len(docs),'saved C documents; user files unchanged',flush=True)
path=ROOT/'source-reference/pololu-3551.step'
data=sw.GetImportFileData(str(path))
data.MapConfigurationData=False
err=integer_ref()
doc=sw.LoadFile4(str(path),'r',data,err)
if doc is None: raise RuntimeError('STEP import failed '+str(err.value))
kind=call(doc,'GetType')
out=ROOT/'hardware-reference'/('HW-201_Pololu3551_SUPPLIER'+('.SLDASM' if kind==2 else '.SLDPRT'))
err,warn=integer_ref(),integer_ref()
if not doc.Extension.SaveAs(str(out),0,1,nothing(),err,warn): raise RuntimeError('Native save failed')
rows=[]
if kind==2:
    for c in call(doc,'GetComponents',False) or []:
        m=call(c,'GetModelDoc2')
        rows.append({'name':call(c,'Name2'),'path':call(c,'GetPathName'),
                     'box_mm':[x*1000 for x in call(c,'GetBox',False,False)],
                     'transform':list(call(c.Transform2,'ArrayData'))})
else:
    for b in call(doc,'GetBodies2',0,False) or []:
        rows.append({'name':call(b,'Name'),'box_mm':[x*1000 for x in call(b,'GetBodyBox')]})
report={'type':kind,'file':str(out),'components_or_bodies':rows}
(ROOT/'supplier-import.json').write_text(json.dumps(report,indent=2))
doc.ShowNamedView2('*Isometric',7); call(doc,'ViewZoomtofit2')
print(json.dumps(report),flush=True)
