"""Test native dimension-driven rotation rather than direct component transforms."""
import json,math
from build_assembly import Assembly,ROOT,connect,call,integer_ref
a=Assembly.__new__(Assembly); a.sw=connect(); a.models={}
path=ROOT/'ARM-B_Articulated_prototype_DEVELOPMENT.SLDASM'
a.doc=a.sw.OpenDoc6(str(path),2,1,'',integer_ref(),integer_ref())
a.report=json.loads((ROOT/'assembly-build-report.json').read_text())
by_name={call(c,'Name2'):c for c in call(a.doc,'GetComponents',False)}
a.components={r['key']:by_name[r['instance']] for r in a.report['components']}
name='J2_Shoulder_command'
if a.doc.FeatureByName(name) is None:
    call(a.doc,'ClearSelection2',True)
    if not a.plane('yaw','Right Plane').Select2(False,1) or not a.plane('upper','Top Plane').Select2(True,1):
        raise RuntimeError('Could not select angle planes')
    err=integer_ref(); angle=math.radians(135)
    mate=call(a.doc,'AddMate5',6,0,False,0.,0.,0.,0.,0.,angle,angle,angle,False,False,0,err)
    if mate is None or err.value!=1: raise RuntimeError('Angle mate failed '+str(err.value))
    mate.Name=name
    a.report['mates'].append({'name':name,'type':'angle_command','error':1,'home_angle_deg':135})
dim=a.doc.Parameter('D1@'+name)
if dim is None: raise RuntimeError('Angle dimension not found')
try:
    for q in (45,30,-40):
        result=call(dim,'SetSystemValue3',math.radians(q+90),1,None)
        print('Dimension command',q,'return',result,'rebuild',call(a.doc,'EditRebuild3'),flush=True)
        for key in ('upper','elbow_servo','forearm','shoulder_horn','elbow_sleeve_0'):
            values=call(call(a.components[key],'Transform2'),'ArrayData')
            print(key,'angle',math.degrees(math.atan2(values[1],values[0])),
                  'position',[round(v*1000,3) for v in values[9:12]],flush=True)
finally:
    call(dim,'SetSystemValue3',math.radians(135),1,None)
    call(a.doc,'EditRebuild3')
    a.save()
