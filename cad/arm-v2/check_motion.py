"""Native solid-interference checks at explicit kinematic samples; not a swept proof."""
import json,math
from build_assembly import ROOT,connect,call,integer_ref,pythoncom,win32com,rotation_z,compose,point,I
sw=connect()
path=ROOT/'ARM-B_Articulated_prototype_DEVELOPMENT.SLDASM'
doc=sw.OpenDoc6(str(path),2,1,'',integer_ref(),integer_ref())
if doc is None: raise RuntimeError('Assembly did not open')
build=json.loads((ROOT/'assembly-build-report.json').read_text())
by_name={call(c,'Name2'):c for c in call(doc,'GetComponents',False)}
rows={r['key']:r for r in build['components']}
parents={r['child']:r['parent'] for r in build['mates'] if r['type']=='lock'}
parents.update(yaw='base',upper='yaw',forearm='upper',jaw='forearm')
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
        for target,angle,pivot in [('jaw',grip,rows['jaw']['position_mm']),
             ('forearm',elbow+45,rows['forearm']['position_mm']),
             ('upper',shoulder-45,rows['upper']['position_mm'])]:
            if target in chain: rot,pos=pivot_transform(rot,pos,rotation_z(angle),pivot)
        if 'yaw' in chain: rot,pos=pivot_transform(rot,pos,yaw_r,(0,0,0))
        expected[key]=transform_values(rot,pos)
    settings=[('J1_Yaw_command',90+yaw),('J2_Shoulder_command',90+shoulder),
              ('J3_Elbow_command',-elbow),('J4_Grip_command',90+grip)]
    for name,value in settings if command else []:
        dim=doc.Parameter('D1@'+name)
        if dim is None: raise RuntimeError('Missing native joint command '+name)
        if call(dim,'SetSystemValue3',math.radians(value),1,None)!=0:
            raise RuntimeError('Native dimension update failed '+name)
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
samples=[('home',0,45,-45,0),('grip_open',0,45,-45,25),('low_pickup',0,-30,-60,10),
         ('transfer',0,20,-20,5),('upright',0,80,-90,0),('elbow_fold',0,45,-100,0),
         ('yaw_left',-60,20,-20,5),('yaw_right',60,20,-20,5),('extended',0,0,-5,5)]
report={'status':'sampled poses only; continuous swept clearance and physical travel not established','samples':[]}
import sys
if len(sys.argv)>1: samples=[s for s in samples if s[0] in sys.argv[1:]]
def run(selected=samples,filename='motion-inspection.json'):
    report['samples']=[]
    try:
        for name,*angles in selected:
            residual=pose(*angles)
            collisions=interference()
            report['samples'].append({'name':name,'joint_angles_deg':angles,
                'transform_residual':residual,'interferences':collisions})
            (ROOT/filename).write_text(json.dumps(report,indent=2))
            print(name,'collisions',len(collisions),flush=True)
            for item in collisions: print(item,flush=True)
    finally:
        pose(0,45,-45,0)
        if not call(doc,'Save3',1,integer_ref(),integer_ref()): raise RuntimeError('Failed to save restored assembly')

if __name__=='__main__': run()
