"""Verify references, saved native configuration transforms, and active mate errors."""
import json,math
from check_motion import doc,sw,ROOT,call,pose,integer_ref,pythoncom,win32com
report={'status':'Native reopen QA; physical hardware fit and tests outstanding','configurations':[]}
build=json.loads((ROOT/'assembly-build-report.json').read_text())
positions=json.loads((ROOT/'pose-configurations.json').read_text())
limits=json.loads((ROOT/'native-motion-limits.json').read_text())
for item in limits['limits']:
 if not any(m['name']==item['name'] for m in build['mates']):
  build['mates'].append({'name':item['name'],'type':'angle_limit','configuration':limits['configuration']})
for position in positions:
 name=position['name']; call(doc,'ShowConfiguration2',name); call(doc,'ForceRebuild3',False)
 if call(call(call(doc,'ConfigurationManager'),'ActiveConfiguration'),'Name')!=name: raise RuntimeError('Configuration failed '+name)
 residual=pose(*position['joint_angles_deg'],command=False)
 errors=[]
 for m in build['mates']:
  f=doc.FeatureByName(m['name'])
  if f is None: raise RuntimeError('Missing mate '+m['name'])
  if call(f,'IsSuppressed2',1,None)[0]: continue
  warning=win32com.client.VARIANT(pythoncom.VT_BYREF|pythoncom.VT_BOOL,False)
  value=call(f,'GetErrorCode2',warning)
  if value: errors.append({'mate':m['name'],'error':value,'warning':warning.value})
 if errors: raise RuntimeError('Mate issues in '+name+': '+str(errors))
 report['configurations'].append({'name':name,'transform_residual':residual,'mate_errors':errors})
 print('Verified saved configuration',name,flush=True)
call(doc,'ShowConfiguration2',limits['configuration']); call(doc,'ForceRebuild3',False)
for item in limits['limits']:
 f=doc.FeatureByName(item['name'])
 if call(f,'IsSuppressed2',1,None)[0]: raise RuntimeError('Inactive free-motion limit')
 warning=win32com.client.VARIANT(pythoncom.VT_BYREF|pythoncom.VT_BOOL,False)
 if call(f,'GetErrorCode2',warning): raise RuntimeError('Invalid free-motion limit')
 command_name=item['name'].replace('_travel_limit','_command')
 if not call(doc.FeatureByName(command_name),'IsSuppressed2',1,None)[0]: raise RuntimeError('Fixed command active in free motion')
report['free_motion_limits_verified']=True
call(doc,'ShowConfiguration2','01_Home'); call(doc,'ForceRebuild3',False)
components={call(c,'Name2'):c for c in call(doc,'GetComponents',False)}
if len(components)!=len(build['components']): raise RuntimeError('Component count mismatch')
for row in build['components']:
 c=components[row['instance']]; model=call(c,'GetModelDoc2')
 if model is None or len(call(model,'GetBodies2',0,False) or [])!=1: raise RuntimeError('Missing component solid '+row['key'])
 if call(model,'GetPathName').lower()!=str(ROOT/row['file']).lower(): raise RuntimeError('Wrong reference '+row['key'])
report['referenced_components_verified']=len(components)
sw.ActivateDoc3(str(ROOT/'ARM-C_Articulated_prototype_DEVELOPMENT.SLDASM'),True,0,integer_ref())
doc.ShowNamedView2('*Isometric',7); call(doc,'ViewZoomtofit2'); call(doc,'GraphicsRedraw2')
if not call(doc,'Save3',1,integer_ref(),integer_ref()): raise RuntimeError('Save failed')
build['status']='Native articulation/configurations verified at discrete samples; fabrication hold for actual horn interfaces'
(ROOT/'assembly-build-report.json').write_text(json.dumps(build,indent=2))
(ROOT/'saved-assembly-verification.json').write_text(json.dumps(report,indent=2))
print('Verified references and mate state; saved home',flush=True)
