"""Rebuild all rigid attachment definitions from a clean, regenerated home pose."""
import json,shutil
from datetime import datetime
from build_native import ROOT,connect,call,integer_ref,pythoncom,win32com
sw=connect(); path=ROOT/'ARM-B_Articulated_prototype_DEVELOPMENT.SLDASM'
backup=ROOT/'development-debug'/('before-rigid-groups-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir(parents=True); shutil.copy2(path,backup/path.name)
doc=sw.OpenDoc6(str(path),2,1,'',integer_ref(),integer_ref())
report=json.loads((ROOT/'assembly-build-report.json').read_text())
rows={r['key']:r for r in report['components']}
components={call(c,'Name2'):c for c in call(doc,'GetComponents',False)}
locks=[m for m in report['mates'] if m['type']=='lock']
call(doc,'ClearSelection2',True)
for i,m in enumerate(locks):
    f=doc.FeatureByName(m['name'])
    if f is None or not f.Select2(bool(i),0): raise RuntimeError('Could not select '+m['name'])
if not doc.Extension.DeleteSelection2(0): raise RuntimeError('Could not clear old rigid attachments')
mu=call(sw,'GetMathUtility')
for row in rows.values():
    r,p=row['rotation'],row['position_mm']
    values=[r[j][i] for i in range(3) for j in range(3)]+[x/1000 for x in p]+[1.,0.,0.,0.]
    components[row['instance']].Transform2=call(mu,'CreateTransform',win32com.client.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_R8,values))
call(doc,'EditRebuild3')
for i,m in enumerate(locks):
    data=call(doc,'CreateMateData',16)
    data.EntitiesToMate=win32com.client.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_DISPATCH,
        [components[rows[m['parent']]['instance']],components[rows[m['child']]['instance']]])
    f=call(doc,'CreateMate',data)
    if f is None: raise RuntimeError('Could not create '+m['name'])
    f.Name=m['name']; m['creation_api']='CreateMateData/CreateMate after clean home rebuild'
    if i%20==0: print('Rigid attachments',i+1,'/',len(locks),flush=True)
call(doc,'EditRebuild3')
if not call(doc,'Save3',1,integer_ref(),integer_ref()): raise RuntimeError('Save failed')
(ROOT/'assembly-build-report.json').write_text(json.dumps(report,indent=2))
print('Saved rigid groups',flush=True)
