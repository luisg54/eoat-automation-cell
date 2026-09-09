"""Save and re-open named native assembly positions using verified joint angles."""
import json
from check_motion import doc,sw,ROOT,call,integer_ref,pose
cm=call(doc,'ConfigurationManager')
home='01_Home'
positions=[('01_Home',(0,45,-45,0)),('02_Grip_open',(0,45,-45,25)),
 ('03_Pickup_trial',(0,-30,-60,10)),('04_Transfer',(0,20,-20,10)),
 ('05_Transfer_left',(-60,20,-20,10)),('06_Transfer_right',(60,20,-20,10))]
for name,angles in positions:
 if doc.GetConfigurationByName(name) is None:
  c=call(cm,'AddConfiguration2',name,'Nominal CAD pose; physical calibration required','',0,'','Joint-angle review position',True)
  if c is None: raise RuntimeError('Could not create '+name)
 call(doc,'ShowConfiguration2',name)
 if call(call(cm,'ActiveConfiguration'),'Name')!=name: raise RuntimeError('Could not show '+name)
 pose(*angles)
 print('Configured',name,flush=True)
# Revisit, checking independently saved native dimension values rather than resetting them.
report=[]
for name,angles in positions:
 call(doc,'ShowConfiguration2',name); call(doc,'EditRebuild3')
 expected=[90+angles[0],90+angles[1],-angles[2],90+angles[3]]
 import math
 actual=[math.degrees(call(doc.Parameter('D1@'+n),'SystemValue')) for n in
  ['J1_Yaw_command','J2_Shoulder_command','J3_Elbow_command','J4_Grip_command']]
 if max(abs(a-b) for a,b in zip(actual,expected))>1e-6: raise RuntimeError('Configuration values did not persist '+name)
 report.append({'name':name,'joint_angles_deg':angles,'native_mate_dimensions_deg':actual})
call(doc,'ShowConfiguration2',home); pose(0,45,-45,0)
call(doc,'ShowConfiguration2','01_Home'); call(doc,'EditRebuild3')
doc.ShowNamedView2('*Isometric',7); call(doc,'ViewZoomtofit2')
if not call(doc,'Save3',1,integer_ref(),integer_ref()): raise RuntimeError('Save failed')
(ROOT/'pose-configurations.json').write_text(json.dumps(report,indent=2))
print('Saved and verified six native configurations',flush=True)
