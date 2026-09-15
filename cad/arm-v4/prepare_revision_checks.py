"""Adapt existing verification tooling to D's three revolute joints and parallel jaws."""
from pathlib import Path
root=Path(__file__).resolve().parent
old='ARM-C_Articulated_prototype_DEVELOPMENT'; new='ARM-D_Modular_parallel_gripper_DEVELOPMENT'
for name in ('present_assembly.py','finalize_sketches.py','add_joint_commands.py','check_motion.py','calculate_cad_loads.py'):
    s=(root.parent/'arm-v3'/name).read_text().replace(old,new)
    if name=='add_joint_commands.py':
        s=s.replace(",\n ('J4_Grip_command','forearm','Right Plane','jaw','Top Plane',90)", '')
    if name=='check_motion.py':
        s=s.replace("jaw='forearm'","jaw_right='forearm',jaw_left='forearm'")
        s=s.replace("for target,angle,pivot in [('jaw',grip,rows['jaw']['position_mm']),\n             ('forearm'", "if key in ('jaw_right','jaw_left'):\n            pos=list(pos); pos[1]+=(32-grip)/2*(1 if key=='jaw_right' else -1)\n        for target,angle,pivot in [('forearm'")
        s=s.replace(",('J4_Grip_command',90+grip)", '')
        s=s.replace("    call(doc,'EditRebuild3')\n    residual=", "    if command:\n        for key in ('jaw_right','jaw_left'):\n            dim=doc.Parameter('D1@'+key+'_half_opening')\n            if call(dim,'SetSystemValue3',grip/2000,1,None)!=0: raise RuntimeError('Jaw command failed')\n    call(doc,'EditRebuild3')\n    residual=")
        start=s.index("samples=[");end=s.index("report={'status'",start)
        s=s[:start]+"samples=[('home',0,45,-45,32),('grip_22mm',0,45,-45,22),('grip_2mm',0,45,-45,2),\n         ('low_pickup',0,-30,-60,22),('transfer',0,20,-20,22),('upright',0,80,-90,32),\n         ('elbow_fold',0,45,-100,32),('yaw_left',-60,20,-20,22),('yaw_right',60,20,-20,22),('extended',0,0,-5,32)]\n"+s[end:]
        s=s.replace("pose(0,45,-45,0)","pose(0,45,-45,32)")
    if name=='calculate_cad_loads.py':
        s=s.replace("parents={r['child']:r['parent'] for r in build['mates'] if r['type']=='lock'}", "parents={r['child']:r['parent'] for r in build['mates'] if r['type']=='lock'}\nparents.update(jaw_right='forearm',jaw_left='forearm')")
        s=s.replace("        elif name.startswith('HW-006'):", "        elif name.startswith('HW-202'): mass,source=26.,'Supplier complete gripper 30 g; body allocation 26 g, two jaws 2 g each'\n        elif name.startswith('HW-203'): mass,source=2.,'Allocation within supplier complete gripper mass 30 g'\n        elif name.startswith('HW-006'):")
        s=s.replace('payload_radius=math.hypot(69,1)','payload_radius=90.')
        s=s.replace("('elbow',.17652/3)","('elbow',.9218251/3*.9)")
        start=s.index('# Geometric contact');end=s.index("(ROOT/'cad-load-and-bom-report.json')",start)
        s=s[:start]+"report['grip_estimate']={'parallel_jaw_opening_mm':32,'assumed_friction_coefficient':.3,'required_normal_N_per_jaw_20g_weight_factor2':2*.020*9.80665/(2*.3),'status':'Required holding force only; supplier does not give a usable continuous gripping-force rating. Measure retention and current.'}\n"+s[end:]
    (root/name).write_text(s)
print('Prepared D verification scripts')
