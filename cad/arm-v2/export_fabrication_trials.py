"""Export only individual solids with explicit mm units and fine mesh settings."""
import json,shutil
from collections import Counter
from build_native import ROOT,connect,call,integer_ref,nothing
from check_print_meshes import inspect
sw=connect(); build=json.loads((ROOT/'assembly-build-report.json').read_text())
counts=Counter(r['file'].split('\\')[-1] for r in build['components'] if r['file'].startswith('parts'))
counts['FIT-001_Dowel_and_bearing_trial.SLDPRT']=1
out=ROOT/'fabrication-trial'; out.mkdir(exist_ok=True)
prior_i={i:sw.GetUserPreferenceIntegerValue(i) for i in (78,211)}
prior_t={i:sw.GetUserPreferenceToggle(i) for i in (69,70,191)}
rows=[]
try:
 sw.SetUserPreferenceIntegerValue(78,2); sw.SetUserPreferenceIntegerValue(211,0)
 sw.SetUserPreferenceToggle(69,True); sw.SetUserPreferenceToggle(70,False); sw.SetUserPreferenceToggle(191,False)
 for filename,quantity in sorted(counts.items()):
  source=ROOT/'parts'/filename
  folder=out/('fit-coupon' if filename.startswith('FIT-') else 'candidate-parts')
  folder.mkdir(exist_ok=True)
  doc=sw.OpenDoc6(str(source),1,1,'',integer_ref(),integer_ref())
  if doc is None: raise RuntimeError('Open failed '+filename)
  sw.ActivateDoc3(str(source),True,0,integer_ref())
  if call(call(sw,'ActiveDoc'),'GetPathName').lower()!=str(source).lower(): raise RuntimeError('Wrong active export document')
  props=doc.Extension.CustomPropertyManager('')
  for key,value in [('Print material recommendation','TPU' if 'TPU' in filename else 'PETG'),
                    ('Assembly print quantity',str(quantity)),('Prototype status','Fit trial; physical validation outstanding')]:
   call(props,'Add3',key,30,value,1)
  if not call(doc,'Save3',1,integer_ref(),integer_ref()): raise RuntimeError('Could not save part properties')
  path=folder/(source.stem+'.stl')
  err,warn=integer_ref(),integer_ref()
  if not doc.Extension.SaveAs(str(path),0,1,nothing(),err,warn) or err.value: raise RuntimeError('Export failed '+filename)
  mesh=inspect(path)
  if mesh['boundary_edges'] or mesh['nonmanifold_edges'] or mesh['signed_volume_in_file_units_cubed']<=0: raise RuntimeError('Invalid mesh '+filename)
  mp=call(doc.Extension,'CreateMassProperty'); volume=call(mp,'Volume')*1e9
  if abs(mesh['signed_volume_in_file_units_cubed']/volume-1)>.02: raise RuntimeError('Mesh/native volume mismatch')
  shutil.copy2(source.with_suffix('.step'),folder/(source.stem+'.step'))
  rows.append({'part':source.stem,'quantity':quantity,'material':'TPU' if 'TPU' in filename else 'PETG',
    'status':'Print and measure coupon first' if filename.startswith('FIT-') else 'Candidate geometry; horn and purchased-hardware fits must be resolved before fabrication',
    'units':'mm','native_volume_mm3':volume,**mesh})
  sw.CloseDoc(str(source)); print('Exported and checked',source.stem,flush=True)
 (out/'manifest.json').write_text(json.dumps(rows,indent=2))
finally:
 for i,v in prior_i.items(): sw.SetUserPreferenceIntegerValue(i,v)
 for i,v in prior_t.items(): sw.SetUserPreferenceToggle(i,v)
