"""Recreate differently oriented rigid attachments through the current mate API."""
import json,shutil
from datetime import datetime
from build_assembly import ROOT,connect,call,integer_ref,nothing,pythoncom,win32com
sw=connect(); path=ROOT/'ARM-B_Articulated_prototype_DEVELOPMENT.SLDASM'
backup=ROOT/'development-debug'/('before-lock-repair-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir(parents=True); shutil.copy2(path,backup/path.name)
doc=sw.OpenDoc6(str(path),2,1,'',integer_ref(),integer_ref())
report=json.loads((ROOT/'assembly-build-report.json').read_text())
rows={r['key']:r for r in report['components']}
by_name={call(c,'Name2'):c for c in call(doc,'GetComponents',False)}
mu=call(sw,'GetMathUtility'); repaired=[]
for mate in report['mates']:
    if mate['type']!='lock': continue
    parent,child=rows[mate['parent']],rows[mate['child']]
    if max(abs(parent['rotation'][i][j]-child['rotation'][i][j]) for i in range(3) for j in range(3))<1e-8: continue
    feature=doc.FeatureByName(mate['name'])
    if feature is None: raise RuntimeError('Missing native mate '+mate['name'])
    call(doc,'ClearSelection2',True)
    if not feature.Select2(False,0) or not doc.Extension.DeleteSelection2(0):
        raise RuntimeError('Could not replace '+mate['name'])
    c=by_name[child['instance']]
    r,p=child['rotation'],child['position_mm']
    values=[r[j][i] for i in range(3) for j in range(3)]+[x/1000 for x in p]+[1.,0.,0.,0.]
    c.Transform2=call(mu,'CreateTransform',win32com.client.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_R8,values))
    data=call(doc,'CreateMateData',16)
    data.EntitiesToMate=win32com.client.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_DISPATCH,[by_name[parent['instance']],c])
    new=call(doc,'CreateMate',data)
    if new is None: raise RuntimeError('Lock creation failed '+mate['name'])
    new.Name=mate['name']
    mate['creation_api']='CreateMateData/CreateMate'
    repaired.append(mate['name'])
    print('Repaired',mate['name'],flush=True)
    (ROOT/'lock-repair-progress.json').write_text(json.dumps(repaired,indent=2))
call(doc,'EditRebuild3')
if not call(doc,'Save3',1,integer_ref(),integer_ref()): raise RuntimeError('Save failed')
(ROOT/'assembly-build-report.json').write_text(json.dumps(report,indent=2))
print('Saved',len(repaired),'recreated lock mates',flush=True)
