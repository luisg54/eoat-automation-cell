"""Add editable native angle dimensions for deterministic arm positioning."""
import json,math
from build_assembly import Assembly,ROOT,connect,call,integer_ref
a=Assembly.__new__(Assembly); a.sw=connect(); a.models={}
a.doc=a.sw.OpenDoc6(str(ROOT/'ARM-C_Articulated_prototype_DEVELOPMENT.SLDASM'),2,1,'',integer_ref(),integer_ref())
a.report=json.loads((ROOT/'assembly-build-report.json').read_text())
names={call(c,'Name2'):c for c in call(a.doc,'GetComponents',False)}
a.components={r['key']:names[r['instance']] for r in a.report['components']}
for name,parent,plane1,child,plane2,angle in [
 ('J1_Yaw_command','base','Front Plane','yaw','Right Plane',90),
 ('J2_Shoulder_command','yaw','Right Plane','upper','Top Plane',135),
 ('J3_Elbow_command','upper','Right Plane','forearm','Right Plane',45),
 ('J4_Grip_command','forearm','Right Plane','jaw','Top Plane',90)]:
 if a.doc.FeatureByName(name) is not None: continue
 call(a.doc,'ClearSelection2',True)
 if not a.plane(parent,plane1).Select2(False,1) or not a.plane(child,plane2).Select2(True,1): raise RuntimeError(name+' selection failed')
 err=integer_ref(); rad=math.radians(angle)
 m=call(a.doc,'AddMate5',6,0,False,0.,0.,0.,0.,0.,rad,rad,rad,False,False,0,err)
 if m is None or err.value!=1: raise RuntimeError(name+' creation failed '+str(err.value))
 m.Name=name
 a.report['mates'].append({'name':name,'type':'angle_command','error':1,'home_angle_deg':angle})
 print('Created',name,flush=True)
a.save()
