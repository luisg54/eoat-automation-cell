"""Recreate joint references after native part regeneration; keep rigid attachments."""
import json,shutil
from datetime import datetime
from build_assembly import Assembly,ROOT,connect,call,integer_ref,methods,pythoncom,win32com
a=Assembly.__new__(Assembly); a.sw=connect(); a.models={}
path=ROOT/'ARM-B_Articulated_prototype_DEVELOPMENT.SLDASM'
backup=ROOT/'development-debug'/('before-joint-refresh-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir(parents=True); shutil.copy2(path,backup/path.name)
a.doc=a.sw.OpenDoc6(str(path),2,1,'',integer_ref(),integer_ref())
methods(a.doc,['ClearSelection2','AddMate5'])
a.report=json.loads((ROOT/'assembly-build-report.json').read_text())
names={call(c,'Name2'):c for c in call(a.doc,'GetComponents',False)}
a.components={r['key']:names[r['instance']] for r in a.report['components']}
old=[m for m in a.report['mates'] if m['type']!='lock']
call(a.doc,'ClearSelection2',True)
for i,m in enumerate(old):
 f=a.doc.FeatureByName(m['name'])
 if f is None or not f.Select2(bool(i),0): raise RuntimeError('Missing '+m['name'])
if not a.doc.Extension.DeleteSelection2(0): raise RuntimeError('Could not refresh joints')
a.report['mates']=[m for m in a.report['mates'] if m['type']=='lock']
mu=call(a.sw,'GetMathUtility')
for row in a.report['components']:
 r,p=row['rotation'],row['position_mm']
 values=[r[j][i] for i in range(3) for j in range(3)]+[x/1000 for x in p]+[1.,0.,0.,0.]
 a.components[row['key']].Transform2=call(mu,'CreateTransform',win32com.client.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_R8,values))
call(a.doc,'EditRebuild3')
a.mate('J1_yaw_axis',1,a.cylinder('yaw',3.95),a.cylinder('base',11.1))
a.mate('J1_yaw_height',0,a.plane('base','Top Plane'),a.plane('yaw','Top Plane'))
a.joint('J2_shoulder','upper','shoulder_servo',4,3,'yaw',23)
a.joint('J3_elbow','forearm','elbow_servo',4,2.5,'upper',15)
a.joint('J4_grip','jaw','grip_servo',3,2.5,'forearm',0)
a.save()
