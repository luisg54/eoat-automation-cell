"""Revision D: preserve the user's C history and add functional interface changes."""
import json
from build_native import Part,ROOT,connect,call,integer_ref,methods
from build_arm_parts import box,round_feature,holes

def inherited(sw,source,name):
    p=Part.__new__(Part); p.sw=sw; p.name=name; p.features=[]
    p.doc=sw.OpenDoc6(str(ROOT/'parts'/(source+'.SLDPRT')),1,1,'',integer_ref(),integer_ref())
    if p.doc is None: raise RuntimeError('Cannot open preserved user part '+source)
    methods(p.doc,['ClearSelection2','EditRebuild3','ForceRebuild3','GetBodies2','GetPartBox','GetTitle'])
    methods(p.doc.FeatureManager,['FeatureExtrusion2','FeatureCut3'])
    return p

def platform(sw):
    p=inherited(sw,'ARM-002_Yaw_platform_and_shoulder_mount','ARM-202_Yaw_platform')
    p.sketch('Separate_upright_above_platform','Top Plane'); p.rectangle(-100,-100,100,100)
    p.extrude('Remove_integral_upright_from_platform',150,True,77,through=False)
    holes(p,'Four_M3_upright_attachment_holes',[(x,z) for x in (-32,32) for z in (-8,8)],3.4,70,'Top Plane')
    report=p.save()
    if report['approximate_box_mm'][4]>77.01: raise RuntimeError('Platform separation failed')
    return report

def upright(sw):
    p=inherited(sw,'ARM-002_Yaw_platform_and_shoulder_mount','ARM-203_Bolted_shoulder_upright')
    p.sketch('Separate_platform_below_upright','Top Plane'); p.rectangle(-100,-100,100,100)
    p.extrude('Remove_platform_and_spindle_from_upright',200,True,77,flip=True,through=False)
    box(p,'Broad_bolted_foot',(-40,-12,40,12),6,77,'Top Plane')
    holes(p,'Four_M3_platform_attachment_holes',[(x,z) for x in (-32,32) for z in (-8,8)],3.4,70,'Top Plane')
    report=p.save()
    if report['approximate_box_mm'][1]<76.99: raise RuntimeError('Upright separation failed')
    return report

def upper(sw):
    p=inherited(sw,'ARM-101_Upper_link_60mm_MG996_SG90','ARM-201_Upper_link_dual_MG996R')
    box(p,'Larger_elbow_servo_mount_replaces_SG90_opening',(42,-15,100,15),4)
    box(p,'MG996R_elbow_body_clearance',(49.5,-10.35,91.2,10.35),1,-5,cut=True)
    holes(p,'MG996R_elbow_tab_fasteners',[(47,-5),(47,5),(94,-5),(94,5)],3.0)
    return p.save()

if __name__=='__main__':
    sw=connect(); prior=sw.GetUserPreferenceToggle(16)
    try:
        sw.SetUserPreferenceToggle(16,False)
        reports=[platform(sw),upright(sw),upper(sw)]
        (ROOT/'revision-structural-parts.json').write_text(json.dumps(reports,indent=2))
    finally: sw.SetUserPreferenceToggle(16,prior)
