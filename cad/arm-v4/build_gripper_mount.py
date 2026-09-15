"""A removable fork supports the purchased parallel gripper at both pin axes."""
import json
from build_native import ROOT,Part,connect
from build_arm_parts import box,round_feature,holes
from build_fasteners import screw,washer,nut
G_POS=(30.85,-2.980423487682,34.512087117409)
G_ROT=[[0,1,0],[-1,0,0],[0,0,1]]
PIN_POINTS=[(37.620525892443,21.0),(46.820525892444,13.0)]
MOUNT_POINTS=[(27,-11.5),(27,11.5),(58,-11.5),(58,11.5)]

def forearm(sw):
    p=Part(sw,'ARM-204_Modular_forearm_MG996R')
    round_feature(p,'Metal_horn_flange',0,0,32,4)
    box(p,'Straight_forearm_web',(0,-7,28,7),4)
    box(p,'Replaceable_tool_mounting_deck',(23,-15,62,15),4)
    round_feature(p,'Dowel_support_hub',0,0,14,4,8,4)
    p.sketch('Raised_washer_seats_PCD14')
    for x,y in [(7,0),(-7,0),(0,7),(0,-7)]: p.circle(x,y,3.5)
    p.extrude('Washer_seats_clear_dowel_sleeve',4,False,4)
    holes(p,'Metal_horn_M3_pattern',[(7,0),(-7,0),(0,7),(0,-7)],3.2)
    holes(p,'Elbow_sleeve_bore',[(0,0)],8)
    holes(p,'Modular_tool_four_M3_pattern',MOUNT_POINTS,3.4)
    return p.save()

def adapter(sw):
    p=Part(sw,'ARM-205_Parallel_gripper_fork_adapter')
    box(p,'Removable_adapter_base',(23,-15,62,15),4,4)
    for side,start in [('Left',10.2),('Right',-14.2)]:
        for i,(x,z) in enumerate(PIN_POINTS):
            box(p,f'{side}_pin{i}_support',(x-5,-z,x+5,-8),4,start,'Top Plane')
            round_feature(p,f'{side}_pin{i}_rounded_lug',x,-z,10,4,offset=start,plane='Top Plane')
    holes(p,'Both_M4_gripper_pin_axes',[(x,-z) for x,z in PIN_POINTS],4.3,-20,'Top Plane')
    holes(p,'Four_M3_removable_deck_bolts',MOUNT_POINTS,3.4)
    return p.save()

def spacer(sw):
    p=Part(sw,'ARM-206_Gripper_lug_crush_spacer_13mm')
    round_feature(p,'Spacer_between_POM_mounting_ears',0,0,8,13,4.3)
    return p.save()

if __name__=='__main__':
    sw=connect(); old=sw.GetUserPreferenceToggle(16)
    try:
        sw.SetUserPreferenceToggle(16,False)
        reports=[forearm(sw),adapter(sw),spacer(sw),screw(sw,3,20),screw(sw,4,35),washer(sw,4),nut(sw,4,True)]
        (ROOT/'gripper-mount-build.json').write_text(json.dumps(reports,indent=2))
    finally: sw.SetUserPreferenceToggle(16,old)
