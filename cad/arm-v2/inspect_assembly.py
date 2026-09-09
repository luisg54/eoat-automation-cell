"""Read-only assembly inspection plus an on-disk QA report."""
import json
from build_native import ROOT, connect, call, integer_ref
sw=connect()
path=ROOT/'ARM-B_Articulated_prototype_DEVELOPMENT.SLDASM'
doc=sw.OpenDoc6(str(path),2,1,'',integer_ref(),integer_ref())
if doc is None:
    raise RuntimeError('Assembly could not be opened')
result={'file':str(path),'components':[],'interferences':[]}
for c in call(doc,'GetComponents',False) or []:
    t=call(c,'Transform2')
    row={'name':call(c,'Name2'),'path':call(c,'GetPathName'),
         'fixed':call(c,'IsFixed'),'transform':list(call(t,'ArrayData')),
         'constraint_status':call(c,'GetConstrainedStatus')}
    result['components'].append(row)
    print(row['name'],[round(v*1000,3) for v in row['transform'][9:12]],'fixed',row['fixed'],flush=True)
mgr=call(doc,'InterferenceDetectionManager')
mgr.TreatCoincidenceAsInterference=False
mgr.IncludeMultibodyPartInterferences=True
for interference in call(mgr,'GetInterferences') or []:
    row={'volume_mm3':float(call(interference,'Volume'))*1e9,
         'component_count':call(interference,'GetComponentCount'),
         'components':[call(c,'Name2') for c in call(interference,'Components') or []]}
    result['interferences'].append(row)
    print('Interference',row,flush=True)
call(mgr,'Done')
(ROOT/'assembly-inspection.json').write_text(json.dumps(result,indent=2))
print('Report saved',flush=True)
