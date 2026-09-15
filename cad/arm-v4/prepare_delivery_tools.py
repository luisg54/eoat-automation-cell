"""Adapt export and arm-limit helpers; never regenerates native part geometry."""
from pathlib import Path
root=Path(__file__).resolve().parent
for name in ('check_print_meshes.py','export_fabrication_trials.py','add_limited_motion_configuration.py'):
    s=(root.parent/'arm-v3'/name).read_text().replace('ARM-C_Articulated_prototype_DEVELOPMENT','ARM-D_Modular_parallel_gripper_DEVELOPMENT')
    if name=='export_fabrication_trials.py':
        s=s.replace("  shutil.copy2(source.with_suffix('.step'),folder/(source.stem+'.step'))", "  err,warn=integer_ref(),integer_ref()\n  if not doc.Extension.SaveAs(str(folder/(source.stem+'.step')),0,1,nothing(),err,warn) or err.value: raise RuntimeError('STEP export failed')")
        s=s.replace("  sw.CloseDoc(str(source));", "  sw.CloseDoc(str(source));")
    if name=='add_limited_motion_configuration.py':
        s=s.replace("('J2_Shoulder_command',60,170)","('J2_Shoulder_command',75,170)")
        s=s.replace(",('J4_Grip_command',90,115)","")
        s=s.replace(",'J4_Grip_command':('forearm','Front Plane')","")
    (root/name).write_text(s)
print('Prepared export and native arm-limit helpers')
