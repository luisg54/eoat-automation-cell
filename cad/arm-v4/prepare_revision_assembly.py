"""Apply a small, auditable assembly delta to the previously validated C builder."""
from pathlib import Path
root=Path(__file__).resolve().parent
s=(root.parent/'arm-v3/build_assembly.py').read_text()
def replace(old,new):
    global s
    if old not in s: raise RuntimeError('Missing edit anchor '+old[:80])
    s=s.replace(old,new)
replace("TEMPLATE=r", "from build_gripper_mount import G_POS,G_ROT,PIN_POINTS,MOUNT_POINTS\nSG_LINK_OFFSET=20.5\nELBOW_BEARING_OFFSET=36\n\nTEMPLATE=r")
replace('ARM-C_Articulated_prototype_DEVELOPMENT','ARM-D_Modular_parallel_gripper_DEVELOPMENT')
replace('ARM-002_Yaw_platform_and_shoulder_mount','ARM-202_Yaw_platform')
replace('ARM-101_Upper_link_60mm_MG996_SG90','ARM-201_Upper_link_dual_MG996R')
replace('ARM-102_Forearm_and_fixed_jaw','ARM-204_Modular_forearm_MG996R')
replace('(60,0,SG_EAR_TOP)','(60,0,7)')
replace("a.add('elbow_servo','HW-003_SG90_NOMINAL_VERIFY'","a.add('elbow_servo','HW-004_MG996R_NOMINAL_VERIFY'")
start=s.index('    grip_servo='); end=s.index('    attachments=[]',start)
s=s[:start]+s[end:]
start=s.index("    attached('fixed_pad'"); end=s.index("    attached('yaw_horn'",start)
s=s[:start]+"    attached('upright','ARM-203_Bolted_shoulder_upright','yaw',(0,0,0))\n"+s[end:]
start=s.index("    attached('elbow_horn'"); end=s.index("    attached('yaw_horn_cap'",start)
s=s[:start]+"    attached('elbow_horn','HW-006_MG996_25T_D20_PCD14_HORN','forearm',point(forearm_rotation,(0,0,-2),forearm_origin),forearm_rotation,True)\n"+s[end:]
start=s.index("    attached('elbow_horn_cap'");end=s.index("    attached('shoulder_cheek'",start)
s=s[:start]+s[end:]
replace('ARM-106_M3_standoff_28p6mm','ARM-108_M3_standoff_32mm')
anchor='    # Real screw/nut envelopes'
start=s.index(anchor)
gripper='''    attached('gripper_adapter','ARM-205_Parallel_gripper_fork_adapter','forearm',forearm_origin,forearm_rotation)
    supplier=json.loads((ROOT/'supplier-mounting-inspection.json').read_text())
    jaw_index=0
    for row in supplier:
        data=row['transform']
        sr=[[data[j*3+i] for j in range(3)] for i in range(3)]
        sp=[x*1000 for x in data[9:12]]
        rot=compose(forearm_rotation,compose(G_ROT,sr))
        pos=point(forearm_rotation,point(G_ROT,sp,G_POS),forearm_origin)
        if 'body' in row['key']:
            attached('gripper_body',row['key'],'forearm',pos,rot,True)
        else:
            key='jaw_right' if jaw_index==0 else 'jaw_left'; jaw_index+=1
            a.add(key,row['key'],pos,rot,True)
    for i,(x,z) in enumerate(PIN_POINTS):
        attached('gripper_crush_spacer_'+str(i),'ARM-206_Gripper_lug_crush_spacer_13mm','forearm',point(forearm_rotation,(x,-6.5,z),forearm_origin),compose(forearm_rotation,TOP))
'''
s=s[:start]+gripper+s[start:]
replace('{2.5:3.5,3:4}[d]','{2.5:3.5,3:4,4:5}[d]')
replace('{2:1.6,2.5:2.,3:2.4}[d]','{2:1.6,2.5:2.,3:2.4,4:3.2}[d]')
replace("[('yaw_servo','base',(0,YAW_EAR_TOP,0),TOP),\n            ('elbow_servo','upper',elbow_servo,shoulder),\n            ('grip_servo','forearm',grip_servo,forearm_rotation)]", "[('yaw_servo','base',(0,YAW_EAR_TOP,0),TOP)]")
start=s.index('    for i,xy in enumerate([(-13,-5)');end=s.index('    for i,y in enumerate((-18,18))',start)
s=s[:start]+'''    for role,parent,origin,rot in [('shoulder','yaw',(0,122,7),I),('elbow','upper',elbow_servo,shoulder)]:
        for i,xy in enumerate([(-13,-5),(-13,5),(34,-5),(34,5)]):
            stack(role+'_servo_mount_'+str(i),parent,origin,rot,xy,0,-7,2.5,14,True)
    for i,xy in enumerate([(x,z) for x in (-32,32) for z in (-8,8)]):
        stack('upright_foot_'+str(i),'yaw',(0,0,0),TOP,xy,83,72,3,20,True)
    for i,xy in enumerate(MOUNT_POINTS):
        stack('tool_adapter_'+str(i),'forearm',forearm_origin,forearm_rotation,xy,8,0,3,16,True)
    for i,(x,z) in enumerate(PIN_POINTS):
        stack('gripper_pin_'+str(i),'forearm',point(forearm_rotation,(x,0,z),forearm_origin),compose(forearm_rotation,TOP),(0,0),14.2,-14.2,4,35,True)
'''+s[end:]
replace('(-25,y),4,-ELBOW_BEARING_OFFSET,3,45,True)','(-25,y),4,-ELBOW_BEARING_OFFSET,3,50,True)')
start=s.index('    for i,xy in enumerate([(7,0)');end=s.index('    # Rear-facing low heads',start)
block=s[start:end]
block=block.replace("label='shoulder_horn_'", "label=role+'_horn_'").replace(",'upper',point(shoulder,(*xy,8.5),upper_origin),shoulder,True)",",parent,point(rot,(*xy,8.5),origin),rot,True)").replace(",'upper',point(shoulder,(*xy,8),upper_origin),shoulder,True)",",parent,point(rot,(*xy,8),origin),rot,True)").replace("'parent':'upper'","'parent':parent")
s=s[:start]+"    for role,parent,origin,rot in [('shoulder','upper',upper_origin,shoulder),('elbow','forearm',forearm_origin,forearm_rotation)]:\n"+'\n'.join('    '+line for line in block.splitlines())+'\n'+s[end:]
replace("[('yaw','yaw',(0,0,0),TOP,41,44),\n            ('elbow','forearm',forearm_origin,forearm_rotation,0,4),\n            ('grip','jaw',jaw_origin,forearm_rotation,SG_LINK_OFFSET,SG_LINK_OFFSET+3)]","[('yaw','yaw',(0,0,0),TOP,41,44)]")
start=s.index('    for i,x in enumerate((57,73))'); end=s.index("    a.report['rigid_attachments']",start)
s=s[:start]+s[end:]
replace("('elbow_servo','upper'),('grip_servo','forearm')","('elbow_servo','upper')")
replace("a.joint('J3_elbow','forearm','elbow_servo',4,2.5,'upper',SG_LINK_OFFSET)","a.joint('J3_elbow','forearm','elbow_servo',4,3,'upper',SG_LINK_OFFSET)")
replace("    a.joint('J4_grip','jaw','grip_servo',3,2.5,'forearm',0)",'''    for key in ('jaw_right','jaw_left'):
        row=next(r for r in a.report['components'] if r['key']==key)
        rel=[row['position_mm'][i]-forearm_origin[i] for i in range(3)]
        a.mate(key+'_height',5,a.plane('forearm','Front Plane'),a.plane(key,'Front Plane'),abs(rel[2]))
        a.mate(key+'_reach',5,a.plane('forearm','Right Plane'),a.plane(key,'Top Plane'),abs(rel[0]))
        a.mate(key+'_half_opening',5,a.plane('forearm','Top Plane'),a.plane(key,'Right Plane'),abs(rel[1]))''')
(root/'build_assembly.py').write_text(s)
print('Prepared D assembly builder')
