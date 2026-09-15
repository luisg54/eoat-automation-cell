"""Read the saved user revision without regenerating or saving its geometry."""
import json, hashlib
from pathlib import Path
from build_native import ROOT, connect, call, integer_ref, pythoncom, win32com
sw=connect()
doc=call(sw,'ActiveDoc')
if doc is None or call(doc,'GetType')!=2: raise RuntimeError('Expected active arm assembly')
source=ROOT.parent/'arm-v3'
if Path(call(doc,'GetPathName')).parent.resolve()!=source.resolve(): raise RuntimeError('Wrong assembly')
seen=set(); rows=[]
for component in call(doc,'GetComponents',False):
    model=call(component,'GetModelDoc2')
    if model is None: raise RuntimeError('Unresolved component')
    path=Path(call(model,'GetPathName'))
    if str(path).lower() in seen: continue
    seen.add(str(path).lower())
    if call(model,'GetSaveFlag'): raise RuntimeError('Unsaved user changes: '+str(path))
    features=[]; errors=[]
    feature=call(model,'FirstFeature')
    while feature:
        name=call(feature,'Name'); kind=call(feature,'GetTypeName2')
        warning=win32com.client.VARIANT(pythoncom.VT_BYREF|pythoncom.VT_BOOL,False)
        error=call(feature,'GetErrorCode2',warning)
        features.append({'name':name,'type':kind})
        if error: errors.append({'name':name,'code':error})
        feature=call(feature,'GetNextFeature')
    mp=call(model.Extension,'CreateMassProperty')
    row={'file':str(path.relative_to(source)), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
         'volume_mm3':call(mp,'Volume')*1e9,'box_mm':[x*1000 for x in call(model,'GetPartBox',True)],
         'features':features,'feature_errors':errors}
    rows.append(row)
    if path.name.startswith('ARM-'):
        print(path.stem, 'edge treatments:', [f['name'] for f in features if 'fillet' in f['type'].lower() or 'chamfer' in f['type'].lower()], 'errors:',errors,flush=True)
(ROOT/'user-revision-inspection.json').write_text(json.dumps({'source':str(source),'parts':rows},indent=2))
print('Inspected',len(rows),'unique saved part files; geometry untouched',flush=True)
