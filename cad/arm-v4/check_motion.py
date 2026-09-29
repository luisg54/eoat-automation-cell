"""Native solid-interference checks at explicit kinematic samples; not a swept proof."""
import json,math
from build_assembly import ROOT,connect,call,integer_ref,pythoncom,win32com,rotation_z,compose,point,I
sw=connect()
path=ROOT/'ARM-D_Modular_parallel_gripper_DEVELOPMENT.SLDASM'
doc=sw.OpenDoc6(str(path),2,1,'',integer_ref(),integer_ref())
if doc is None: raise RuntimeError('Assembly did not open')
build=json.loads((ROOT/'assembly-build-report.json').read_text())
by_name={call(c,'Name2'):c for c in call(doc,'GetComponents',False)}
rows={r['key']:r for r in build['components']}
parents={r['child']:r['parent'] for r in build['mates'] if r['type']=='lock'}
parents.update(yaw='base',upper='yaw',forearm='upper',jaw_right='forearm',jaw_left='forearm')
def ancestors(key):
    result=[key]
    while key in parents:
        key=parents[key]; result.append(key)
    return result
mu=call(sw,'GetMathUtility')
original={key:list(call(call(by_name[r['instance']],'Transform2'),'ArrayData')) for key,r in rows.items()}
def transform_values(r,p):
    return [r[j][i] for i in range(3) for j in range(3)]+[x/1000 for x in p]+[1.,0.,0.,0.]
def set_transform(c,data):
    c.Transform2=call(mu,'CreateTransform',win32com.client.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_R8,data))
def pivot_transform(rot,pos,turn,pivot):
    return compose(turn,rot),point(turn,[pos[i]-pivot[i] for i in range(3)],pivot)
def pose(yaw,shoulder,elbow,grip,command=True):
    global by_name
    # Switching native configurations invalidates previously cached component dispatches.
    by_name={call(c,'Name2'):c for c in call(doc,'GetComponents',False)}
    expected={}
    c,s=math.cos(math.radians(yaw)),math.sin(math.radians(yaw))
    yaw_r=[[c,0,s],[0,1,0],[-s,0,c]]
    for key,row in rows.items():
        chain=ancestors(key)
        rot,pos=row['rotation'],row['position_mm']
        if key in ('jaw_right','jaw_left'):
            pos=list(pos); pos[1]+=(32-grip)/2*(1 if key=='jaw_right' else -1)
        for target,angle,pivot in [('forearm',elbow+45,rows['forearm']['position_mm']),
             ('upper',shoulder-45,rows['upper']['position_mm'])]:
            if target in chain: rot,pos=pivot_transform(rot,pos,rotation_z(angle),pivot)
        if 'yaw' in chain: rot,pos=pivot_transform(rot,pos,yaw_r,(0,0,0))
        expected[key]=transform_values(rot,pos)
    settings=[('J1_Yaw_command',90+yaw),('J2_Shoulder_command',90+shoulder),
              ('J3_Elbow_command',-elbow)]
    for name,value in settings if command else []:
        dim=doc.Parameter('D1@'+name)
        if dim is None: raise RuntimeError('Missing native joint command '+name)
        if call(dim,'SetSystemValue3',math.radians(value),1,None)!=0:
            raise RuntimeError('Native dimension update failed '+name)
    if command:
        if (ROOT/'gripper-equations.json').exists():
            eq=call(doc,'GetEquationMgr')
            index=next(i for i in range(call(eq,'GetCount')) if eq._oleobj_.Invoke(eq._oleobj_.GetIDsOfNames('Equation'),0,2,True,i).split('=')[0].strip()=='"Gripper_opening"')
            if call(eq,'SetEquationAndConfigurationOption',index,'"Gripper_opening" = '+str(grip)+'mm',1,None)<0: raise RuntimeError('Opening equation update failed')
            call(eq,'EvaluateAll')
        else:
            for key in ('jaw_right','jaw_left'):
                dim=doc.Parameter('D1@'+key+'_half_opening')
                if call(dim,'SetSystemValue3',grip/2000,1,None)!=0: raise RuntimeError('Jaw command failed')
    call(doc,'EditRebuild3')
    residual=max(max(abs(a-b) for a,b in zip(expected[key],call(call(by_name[row['instance']],'Transform2'),'ArrayData')))
                 for key,row in rows.items())
    if residual>1e-6:
        issues=[]
        for key,row in rows.items():
            actual=list(call(call(by_name[row['instance']],'Transform2'),'ArrayData'))
            delta=max(abs(a-b) for a,b in zip(expected[key],actual))
            if delta>1e-6: issues.append({'key':key,'residual':delta,'expected':expected[key],'actual':actual})
        (ROOT/'motion-solver-diagnostics.json').write_text(json.dumps({'angles':[yaw,shoulder,elbow,grip],'issues':issues},indent=2))
        for issue in issues[:12]: print('SOLVER',issue,flush=True)
        raise RuntimeError('Mate solver changed the prescribed pose: '+str(residual))
    return residual
def interference():
    mgr=call(doc,'InterferenceDetectionManager')
    try:
        mgr.TreatCoincidenceAsInterference=False
        mgr.IncludeMultibodyPartInterferences=True
        items=call(mgr,'GetInterferences') or []
        result=[{'volume_mm3':float(call(i,'Volume'))*1e9,
                 'components':[call(c,'Name2') for c in call(i,'Components') or []]} for i in items]
        count=call(mgr,'GetInterferenceCount')
        if count!=len(result): raise RuntimeError('Interference count mismatch')
        return result
    finally: call(mgr,'Done')
# Designed engagements with the owned-servo files: plain press-fit sockets over the modeled
# splines and centre screws in the modeled M3 thread / 1.0 mm SG90 pilot. Anything else is unexpected.
EXPECTED={frozenset(p):note for p,note in [
    (('shoulder_spline_hub','shoulder_servo_owned'),'ARM-207 5.80 mm press socket on 5.997 mm MG996R spline'),
    (('elbow_spline_hub','elbow_servo_owned'),'ARM-207 5.80 mm press socket on 5.997 mm MG996R spline'),
    (('shoulder_spline_screw','shoulder_servo_owned'),'M3 centre screw in modeled MG996R spline thread'),
    (('elbow_spline_screw','elbow_servo_owned'),'M3 centre screw in modeled MG996R spline thread'),
    (('collar','yaw_servo_owned'),'ARM-003 4.85 mm press socket on 5.0 mm SG90 spline'),
    (('yaw_spline_screw','yaw_servo_owned'),'M2 horn screw in the 1.0 mm plain SG90 file hole')] if all(k in rows for k in p)}
EXPECTED_MAX_MM3=15.
instance_key={r['instance']:k for k,r in rows.items()}
def classify(collisions,grip):
    expected,known,unexpected=[],[],[]
    for item in collisions:
        keys=frozenset(instance_key.get(n,n) for n in item['components'])
        if keys in EXPECTED and item['volume_mm3']<=EXPECTED_MAX_MM3:
            expected.append(dict(item,note=EXPECTED[keys]))
        elif grip<2 and keys<={'gripper_body','jaw_right','jaw_left'}:
            known.append(dict(item,note='supplier gripper model at full closure, outside the 2-32 mm working range'))
        else: unexpected.append(item)
    return expected,known,unexpected
samples=[('home',0,45,-45,32),('grip_22mm',0,45,-45,22),('grip_2mm',0,45,-45,2),
         ('low_pickup',0,-15,-75,22),('previous_tilted_pickup',0,-15,-80,22),('transfer',0,20,-20,22),('upright',0,80,-90,32),
         ('elbow_fold',0,45,-100,32),('yaw_left',-60,20,-20,22),('yaw_right',60,20,-20,22),('extended',0,0,-5,32)]
report={'status':'sampled poses only; continuous swept clearance and physical travel not established. Designed press-fit/thread engagements with the owned-servo files are listed separately and are not collisions','samples':[]}
import sys
if len(sys.argv)>1: samples=[s for s in samples if s[0] in sys.argv[1:]]
def run(selected=samples,filename='motion-inspection.json'):
    report['samples']=[]
    try:
        for name,*angles in selected:
            residual=pose(*angles)
            collisions=interference()
            expected,known,unexpected=classify(collisions,angles[3])
            report['samples'].append({'name':name,'joint_angles_deg':angles,
                'transform_residual':residual,'interferences':unexpected,
                'expected_designed_engagements':expected,'known_supplier_overlaps':known})
            (ROOT/filename).write_text(json.dumps(report,indent=2))
            print(name,'unexpected',len(unexpected),'expected',len(expected),'known',len(known),flush=True)
            for item in unexpected: print('  UNEXPECTED',item,flush=True)
    finally:
        pose(0,45,-45,32)
        if not call(doc,'Save3',1,integer_ref(),integer_ref()): raise RuntimeError('Failed to save restored assembly')

if __name__=='__main__': run()
