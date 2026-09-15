"""Conservative mass budget from native volumes and nominal purchased masses."""
import json,math
from collections import Counter
from build_assembly import ROOT,connect,call,integer_ref,point,rotation_z
sw=connect()
doc=sw.OpenDoc6(str(ROOT/'ARM-C_Articulated_prototype_DEVELOPMENT.SLDASM'),2,1,'',integer_ref(),integer_ref())
if doc is None: raise RuntimeError('Assembly did not open')
build=json.loads((ROOT/'assembly-build-report.json').read_text())
build_by_key={r['key']:r for r in build['components']}
components={call(c,'Name2'):c for c in call(doc,'GetComponents',False)}
parents={r['child']:r['parent'] for r in build['mates'] if r['type']=='lock'}
def group(key):
    while key in parents: key=parents[key]
    return key
cache={}; result=[]
for row in build['components']:
    name=row['file'].split('\\')[-1]
    if name not in cache:
        model=call(components[row['instance']],'GetModelDoc2')
        if call(model,'GetType')!=1: raise RuntimeError('Expected one part')
        mp=call(model.Extension,'CreateMassProperty')
        volume=call(mp,'Volume')*1e9
        center=[v*1000 for v in call(mp,'CenterOfMass')]
        if name.startswith('HW-001'): mass,source=12.,'assumed bearing mass; weigh actual 608ZZ'
        elif name.startswith('HW-003'): mass,source=9.,'TowerPro SG90 reference mass; confirm actual unit'
        elif name.startswith('HW-004'): mass,source=55.,'TowerPro MG996R reference mass'
        elif name.startswith('HW-005'): mass,source=1.,'assumed stock SG90 horn mass'
        elif name.startswith('HW-006'): mass,source=4.,'conservative horn allocation; verify selected horn'
        else:
            density=7.85 if name.startswith('HW-') else (1.2 if 'TPU' in name else 1.27)
            mass,source=volume*density/1000,f'CAD solid volume; assumed density {density} g/cm3'
        cache[name]={'volume_mm3':volume,'center_mm':center,'mass_g':mass,'basis':source}
    data=cache[name]
    center=point(row['rotation'],data['center_mm'],row['position_mm'])
    g=group(row['key'])
    # Jaw is at zero relative angle in the saved nominal pose.
    distal=g in ('forearm','jaw')
    if distal:
        elbow=build_by_key['forearm']['position_mm']
        if g=='jaw':
            grip=build_by_key['jaw']['position_mm']
            elbow_r=math.hypot(45,30)+math.hypot(center[0]-grip[0],center[1]-grip[1])
        else:
            elbow_r=math.hypot(center[0]-elbow[0],center[1]-elbow[1])
        shoulder_r=60+elbow_r
    elif g=='upper':
        elbow_r=0.; shoulder_r=math.hypot(center[0],center[1]-122)
    else: elbow_r=shoulder_r=0.
    result.append({'key':row['key'],'part':name,'motion_group':g,**data,
                   'elbow_lever_bound_mm':elbow_r,'shoulder_lever_bound_mm':shoulder_r})
# Explicit allowances for unmodeled wires and a 20 g object at the nominal contact.
payload_radius=math.hypot(69,1)
allowances=[{'name':'payload','mass_g':20,'elbow_lever_mm':payload_radius,'shoulder_lever_mm':60+payload_radius},
            {'name':'distal cable allowance','mass_g':3,'elbow_lever_mm':65,'shoulder_lever_mm':125},
            {'name':'upper cable allowance','mass_g':3,'elbow_lever_mm':0,'shoulder_lever_mm':60}]
torques={}
for joint,budget in [('elbow',.17652/3),('shoulder',.9218251/3*.9)]:
    moment=sum(r['mass_g']*r[joint+'_lever_bound_mm'] for r in result)
    moment+=sum(r['mass_g']*r[joint+'_lever_mm'] for r in allowances)
    static=moment*9.80665/1e6
    torques[joint]={'static_upper_bound_Nm':static,'design_Nm':static*1.25,
                    'assumed_budget_Nm':budget,'margin_ratio':budget/(static*1.25)}
report={'status':'CAD sizing estimate, not verified servo continuous rating or physical load test',
        'method':'100 percent solid printed mass bound; each joint uses sum of mass times maximum planar lever; 1.25 load multiplier; one third reference stall budget',
        'components':result,'allowances':allowances,'torques':torques,
        'total_modeled_mass_g':sum(r['mass_g'] for r in result),
        'bom_counts':dict(Counter(r['part'] for r in result))}
# Geometric contact of a 22 mm bearing with the two pad faces in the forearm plane.
# Fixed face y=-10, payload center=(69,1), grip axis=(45,30), moving face local y=-21.
lo,hi=0.,math.radians(25)
for _ in range(60):
    q=(lo+hi)/2
    if 24*math.sin(q)+29*math.cos(q)<32: lo=q
    else: hi=q
q=(lo+hi)/2; contact_x=24*math.cos(q)-29*math.sin(q)
mu=.3
normal=2*.020*9.80665/(2*(mu*math.cos(q/2)-math.sin(q/2)))
report['grip_estimate']={'payload_center_forearm_mm':[69,1,3], 'payload_diameter_mm':22,
 'ideal_first_contact_angle_deg':math.degrees(q),'moving_pad_contact_local_x_mm':contact_x,
 'pad_face_local_x_extent_mm':[14,28],'assumed_friction_coefficient':mu,
 'normal_force_each_N_with_wedge_allowance_and_weight_factor_2':normal,
 'grip_torque_estimate_Nm':normal*contact_x/1000,
 'status':'Ideal rigid geometry and assumed friction; actual soft-pad force and retention require testing'}
(ROOT/'cad-load-and-bom-report.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'torques':torques,'total_modeled_mass_g':report['total_modeled_mass_g'],'bom_counts':report['bom_counts']},indent=2))
