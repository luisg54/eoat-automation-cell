"""Inspect native joint references, suppression, and parent transforms."""
import json,math
from build_native import ROOT,connect,call,integer_ref
sw=connect(); doc=sw.OpenDoc6(str(ROOT/'ARM-B_Articulated_prototype_DEVELOPMENT.SLDASM'),2,1,'',integer_ref(),integer_ref())
report=json.loads((ROOT/'assembly-build-report.json').read_text())
names={r['key']:r['instance'] for r in report['components']}
cs={call(c,'Name2'):c for c in call(doc,'GetComponents',False)}
for key in ['base','yaw','shoulder_servo','upper','forearm','jaw']:
 c=cs[names[key]]
 print(key,'fixed',call(c,'IsFixed'),'transform',call(call(c,'Transform2'),'ArrayData'),flush=True)
for name in ['J1_yaw_axis','J1_yaw_height','J2_shoulder_axis','J2_shoulder_axial','J3_elbow_axis','J4_grip_axis']:
 f=doc.FeatureByName(name); m=call(f,'GetSpecificFeature2')
 print(name,'suppressed',call(f,'IsSuppressed2',1,None),flush=True)
 for i in range(2):
  e=call(m,'MateEntity',i)
  ref=call(e,'Reference')
  print('entity',call(call(e,'ReferenceComponent'),'Name2'),'params',call(e,'EntityParams'),flush=True)
  try: print('surface',call(call(ref,'GetSurface'),'CylinderParams'),flush=True)
  except Exception: pass

