"""Save native configurations and independently verify their stored transforms."""
import json
from check_motion import doc,sw,ROOT,call,integer_ref,pose
cm=call(doc,'ConfigurationManager')
positions=[('01_Home',(0,45,-45,32)),('02_Grip_22mm',(0,45,-45,22)),
 ('03_Pickup_trial',(0,-15,-80,22)),('04_Transfer',(0,20,-20,22)),
 ('05_Transfer_left',(-60,20,-20,22)),('06_Transfer_right',(60,20,-20,22))]
report=[]
for name,values in positions:
    if doc.GetConfigurationByName(name) is None:
        if call(cm,'AddConfiguration2',name,'Sampled CAD pose; calibrate real servos','',0,'','',True) is None: raise RuntimeError('Cannot create '+name)
    call(doc,'ShowConfiguration2',name)
    pose(*values)
for name,values in positions:
    call(doc,'ShowConfiguration2',name); call(doc,'ForceRebuild3',False)
    residual=pose(*values,command=False)
    report.append({'name':name,'pose_values':values,'units':['deg','deg','deg','mm'],'transform_residual':residual})
    print('Verified saved pose',name,flush=True)
call(doc,'ShowConfiguration2','01_Home'); pose(0,45,-45,32)
if not call(doc,'Save3',1,integer_ref(),integer_ref()): raise RuntimeError('Save failed')
(ROOT/'pose-configurations.json').write_text(json.dumps(report,indent=2))
