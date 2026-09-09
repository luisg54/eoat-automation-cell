"""Revision B native arm components. Development geometry, verify before printing."""
import json
import math
from build_native import Part, ROOT, connect, call

def box(p, name, bounds, depth, offset=0, plane='Front Plane', cut=False):
    p.sketch(name+'_profile', plane)
    p.rectangle(*bounds)
    p.extrude(name, depth, cut, offset)

def round_feature(p, name, x, y, outer, depth, inner=0, offset=0, plane='Front Plane', cut=False):
    p.sketch(name+'_profile', plane)
    p.circle(x,y,outer/2)
    if inner:
        p.circle(x,y,inner/2)
    p.extrude(name,depth,cut,offset)

def holes(p, name, points, diameter, offset=-50, plane='Front Plane'):
    p.sketch(name+'_profile', plane)
    for x,y in points:
        p.circle(x,y,diameter/2)
    p.extrude(name,1,True,offset)

def servo_sg90(sw):
    p=Part(sw,'HW-003_SG90_NOMINAL_VERIFY')
    box(p,'Case_23x12p2x23',(-6,-6.1,17,6.1),23,-19)
    box(p,'Mounting_ears_33x12p2',(-11,-6.1,22,6.1),2,-2)
    round_feature(p,'Output_envelope_not_spline',0,0,5,5,offset=4)
    holes(p,'Mounting_holes_nominal',[(-9,0),(20,0)],2.2)
    return p.save(True)

def servo_mg996(sw):
    p=Part(sw,'HW-004_MG996R_NOMINAL_VERIFY')
    box(p,'Case_40p7x19p7',(-10,-9.85,30.7,9.85),37,-30)
    box(p,'Mounting_flange_nominal',(-16.5,-9.85,37.2,9.85),3,-3)
    round_feature(p,'Output_envelope_not_spline',0,0,6,5.9,offset=7)
    holes(p,'Tab_holes_nominal',[(-13,5),(-13,-5),(34,5),(34,-5)],3.5)
    return p.save(True)

def upper(sw):
    p=Part(sw,'ARM-101_Upper_link_60mm_MG996_SG90')
    box(p,'Main_web',(0,-7,60,7),4)
    round_feature(p,'Shoulder_horn_flange',0,0,32,4)
    box(p,'Elbow_servo_mount',(42,-14,90,14),4)
    box(p,'SG90_body_clearance',(53.6,-6.5,77.4,6.5),1,-5,cut=True)
    holes(p,'Elbow_tab_fasteners',[(51,0),(80,0)],2.6)
    holes(p,'Shoulder_center_screw_access',[(0,0)],8)
    holes(p,'Shoulder_horn_bolt_pattern',[(0,10),(0,-10),(10,0),(-10,0)],3.2)
    holes(p,'Cable_tie_holes',[(27,-3),(27,3)],3.2)
    round_feature(p,'Passive_lower_mount_boss',35,-9,10,4)
    round_feature(p,'Passive_upper_mount_boss',35,9,10,4)
    holes(p,'Passive_cheek_standoffs',[(35,-9),(35,9)],3.2)
    round_feature(p,'Shoulder_dowel_support_hub',0,0,14,4,8,4)
    p.sketch('Shoulder_horn_washer_hub_relief_profile')
    for x,y in [(10,0),(-10,0),(0,10),(0,-10)]: p.circle(x,y,3.3)
    p.extrude('Shoulder_horn_washer_hub_relief',4,True,4,through=False)
    return p.save()

def forearm(sw):
    p=Part(sw,'ARM-102_Forearm_and_fixed_jaw')
    round_feature(p,'Elbow_horn_flange',0,0,26,4)
    box(p,'Forearm_web',(0,-7,40,7),4)
    box(p,'Gripper_mount_rib',(26,0,34,30),4)
    box(p,'Gripper_servo_mount',(26,15,70,41),4)
    box(p,'Grip_SG90_body_clearance',(38.6,23.5,62.4,36.5),1,-5,cut=True)
    box(p,'Moving_finger_sweep_relief',(58,14,71,27),1,-5,cut=True)
    holes(p,'Grip_servo_tab_fasteners',[(36,30),(65,30)],2.6)
    box(p,'Fixed_finger_spine',(30,-16,78,-11),4)
    box(p,'Fixed_finger_root',(27,-16,34,7),7)
    holes(p,'Elbow_center_screw_access',[(0,0)],8)
    round_feature(p,'Elbow_dowel_support_hub',0,0,14,4,8,4)
    holes(p,'Elbow_horn_fasteners',[(0,-8),(0,8),(-8,0),(8,0)],2.2)
    p.sketch('Elbow_horn_washer_recess_profile')
    for x,y in [(0,-8),(0,8),(-8,0),(8,0)]:
        p.circle(x,y,2.75)
    p.extrude('M2x8_washer_and_hub_clearance',5,True,3,through=False)
    # Pad-retention fasteners are normal to the print plane; a pad keeper captures rubber.
    holes(p,'Fixed_pad_keeper_fasteners',[(57,-13.5),(73,-13.5)],2.2)
    return p.save()

def moving_jaw(sw):
    p=Part(sw,'ARM-103_Grip_moving_finger')
    # Origin at grip servo axis; nominal contact point is (20,-7).
    round_feature(p,'Stock_horn_attachment',0,0,22,3,offset=15)
    box(p,'Finger_arm',(0,-19,27,3),3,15)
    box(p,'Descending_contact_finger',(15,-20,27,-15),18)
    holes(p,'Horn_center_access',[(0,0)],6)
    holes(p,'Horn_screws',[(0,-8),(0,8),(-8,0),(8,0)],2.2)
    holes(p,'Contact_pad_keeper',[(18,-17.5),(24,-17.5)],2.2)
    return p.save()

def coupon(sw):
    p=Part(sw,'FIT-001_Dowel_and_bearing_trial')
    box(p,'Coupon_plate',(-60,-17,60,17),8)
    p.sketch('Bearing_seat_trial_22p0_22p1_22p2_22p3')
    for x,d in zip((-45,-15,15,45),(22,22.1,22.2,22.3)):
        p.circle(x,0,d/2)
    p.extrude('Bearing_fit_trial_through',1,True,-1)
    p.sketch('Dowel_trial_6p35_6p45_6p55_6p65')
    for x,d in zip((-30,0,30,56),(6.35,6.45,6.55,6.65)):
        p.circle(x,-11,d/2)
    p.extrude('Dowel_fit_trial_through',1,True,-1)
    return p.save()

def base(sw):
    p=Part(sw,'ARM-001_Base_pedestal')
    box(p,'Bench_footprint_140x120',(-70,-60,70,60),5,plane='Top Plane')
    box(p,'Backbone',(-35,5,-21,68),40,-20)
    holes(p,'Removable_servo_mount_M3',[(12,28),(-12,28)],3.2,-40,'Right Plane')
    box(p,'Bearing_bridge',(-35,-20,18,20),4,39,plane='Top Plane')
    # Clear the bridge for rotating spindle and screwdriver access.
    round_feature(p,'Bridge_horn_clearance',0,0,28,1,offset=38,plane='Top Plane',cut=True)
    round_feature(p,'Drive_collar_chamber',0,0,36,5,28,43,'Top Plane')
    round_feature(p,'Bearing_tower',0,0,36,23,22.2,48,'Top Plane')
    round_feature(p,'Bearing_separation_shoulder',0,0,22.2,8,18,55,'Top Plane')
    holes(p,'Bench_clamp_holes',[(-55,-45),(55,-45),(-55,45),(55,45)],5.5,-1,'Top Plane')
    holes(p,'Yaw_crossbolt_access',[(0,45.5)],5,-40,'Right Plane')
    return p.save()

def yoke(sw):
    p=Part(sw,'ARM-002_Yaw_platform_and_shoulder_mount')
    round_feature(p,'Yaw_platform',0,0,88,5,offset=72,plane='Top Plane')
    round_feature(p,'Printed_hollow_yaw_spindle',0,0,7.9,29,3.5,43,'Top Plane')
    round_feature(p,'Inner_race_load_shoulder',0,0,12,2,3.5,70,'Top Plane')
    p.sketch('D_flat_drive_key_profile','Top Plane')
    p.rectangle(3,-5,6,5)
    p.extrude('D_flat_on_spindle_end',5,True,43,through=False)
    # Shoulder axis at (0,122,0); SG90 body axis parallel to the yaw axis.
    box(p,'Shoulder_mount_plate',(-44,76,43,144),4,0)
    box(p,'MG996_body_window',(-10.5,111.65,31.2,132.35),1,-5,cut=True)
    holes(p,'MG996_tab_mounts',[(-13,117),(-13,127),(34,117),(34,127)],3.8)
    holes(p,'Passive_shoulder_standoffs',[(-36,104),(-36,140)],3.2)
    # A rear rib joins the upright to the platform and limits out-of-plane flexure.
    box(p,'Upright_rib',(-23,77,-16,108),12,-8)
    holes(p,'Yaw_positive_retention_crossbolt',[(0,45.5)],2.2,-10,'Right Plane')
    return p.save()

def yaw_collar(sw):
    p=Part(sw,'ARM-003_Yaw_D_drive_collar')
    round_feature(p,'Stock_horn_drive_flange',0,0,24,3,8.1,41,'Top Plane')
    round_feature(p,'D_coupling_ring',0,0,14,4,8.1,44,'Top Plane')
    box(p,'D_key_land',(3.1,-2.4,6,2.4),4,44,plane='Top Plane')
    holes(p,'Stock_horn_screws',[(-8,0),(8,0),(0,-8),(0,8)],2.2,39,'Top Plane')
    p.sketch('Two_horn_washer_clearances_profile','Top Plane')
    for z in (-8,8):
        p.circle(0,z,2.75)
    p.extrude('Two_horn_washer_clearances',4,True,44,through=False)
    holes(p,'Yaw_positive_retention_crossbolt',[(0,45.5)],2.2,-10,'Right Plane')
    for start in (-12,6):
        p.sketch('Crossbolt_flat_seat_'+str(start),'Right Plane')
        p.circle(0,45.5,2.75)
        p.extrude('Crossbolt_flat_seat_cut_'+str(start),6,True,start,through=False)
    return p.save()

def cheek(sw):
    p=Part(sw,'ARM-104_Elbow_bearing_cheek')
    round_feature(p,'Bearing_housing',0,0,34,7,22.2)
    box(p,'Mounting_web',(-30,-14,0,14),4)
    # Web creates material inside bore, so recut the seat last.
    holes(p,'Bearing_seat',[(0,0)],22.2)
    round_feature(p,'Inner_outer_race_retaining_lip',0,0,34,1,18,-1)
    holes(p,'Standoff_fasteners',[(-25,-9),(-25,9)],3.2)
    holes(p,'Bearing_keeper_fasteners',[(14,0),(0,-14),(0,14)],2.2)
    return p.save()

def shoulder_cheek(sw):
    p=Part(sw,'ARM-105_Shoulder_bearing_cheek')
    round_feature(p,'Bearing_housing',0,0,34,7,22.2)
    box(p,'Mounting_web',(-42,-22,0,22),4)
    holes(p,'Bearing_seat',[(0,0)],22.2)
    round_feature(p,'Inner_outer_race_retaining_lip',0,0,34,1,18,-1)
    holes(p,'Standoff_fasteners',[(-36,-18),(-36,18)],3.2)
    holes(p,'Bearing_keeper_fasteners',[(14,0),(0,-14),(0,14)],2.2)
    return p.save()

def spacer(sw):
    p=Part(sw,'ARM-106_M3_standoff_24mm')
    round_feature(p,'Standoff_OD8_ID3p2',0,0,8,24,3.2)
    return p.save()

def pin_sleeve(sw):
    p=Part(sw,'ARM-107_Dowel_to_608_adapter')
    round_feature(p,'Adapter_8OD_6p45ID',0,0,7.98,7,6.45)
    return p.save()

def shoulder_spacer(sw):
    p=Part(sw,'ARM-108_M3_standoff_32mm')
    round_feature(p,'Standoff_OD8_ID3p2',0,0,8,32,3.2)
    return p.save()

def keeper(sw):
    p=Part(sw,'ARM-109_Bearing_and_dowel_keeper')
    round_feature(p,'Outer_race_keeper_flange',0,0,34,2)
    round_feature(p,'Housing_contact_rim_preserves_bearing_float',0,0,34,.2,22.4,-.2)
    round_feature(p,'Pin_end_cover',0,0,18,12)
    p.sketch('Dowel_end_float_pocket_profile')
    p.circle(0,0,7)
    p.extrude('Dowel_end_float_pocket_depth9',9,True,0,through=False)
    holes(p,'Keeper_M2_fasteners',[(14,0),(0,-14),(0,14)],2.2)
    return p.save()

def sg_horn(sw):
    p=Part(sw,'HW-005_SG90_stock_horn_ENVELOPE')
    round_feature(p,'Horn_plate_envelope',0,0,20,2,5.1)
    holes(p,'Nominal_horn_attachment_holes',[(-8,0),(8,0),(0,-8),(0,8)],2.2)
    return p.save(True)

def mg_horn(sw):
    p=Part(sw,'HW-006_MG996_stock_horn_ENVELOPE')
    round_feature(p,'Horn_plate_envelope',0,0,26,3,6.1)
    round_feature(p,'Spline_hub_envelope',0,0,9,4,6.1,-4)
    holes(p,'Nominal_horn_attachment_holes',[(-10,0),(10,0),(0,-10),(0,10)],3.2)
    return p.save(True)

def cassette(sw):
    p=Part(sw,'ARM-004_Removable_yaw_servo_mount')
    box(p,'Servo_shelf',(-21,-18,25,18),4,26,plane='Top Plane')
    box(p,'Rear_clamping_block',(-21,23,-14,33),36,-18)
    box(p,'Servo_body_window',(-6.4,-6.5,17.4,6.5),1,25,plane='Top Plane',cut=True)
    holes(p,'Yaw_servo_M2_fasteners',[(-9,0),(20,0)],2.6,25,'Top Plane')
    box(p,'Left_nut_access',(-14,8,-4,16),1,20,plane='Top Plane',cut=True)
    box(p,'Right_nut_access',(-14,-16,-4,-8),1,20,plane='Top Plane',cut=True)
    p.sketch('Rear_clamping_M3_profile','Right Plane')
    p.circle(12,28,1.6)
    p.circle(-12,28,1.6)
    p.extrude('Rear_clamping_M3_holes',11,True,-25,through=False)
    return p.save()

def fixed_pad(sw):
    p=Part(sw,'ARM-110_Fixed_jaw_TPU_sock')
    box(p,'Soft_contact_and_wrap',(54,-17,76,-10),6,-1)
    p.sketch('Fixed_bar_slip_pocket_profile')
    p.rectangle(53,-16.1,77,-10.9)
    p.extrude('Slip_pocket',4.2,True,-.1,through=False)
    holes(p,'Pad_capture_M2',[(57,-13.5),(73,-13.5)],2.2)
    return p.save()

def moving_pad(sw):
    p=Part(sw,'ARM-111_Moving_jaw_TPU_sock')
    box(p,'Soft_contact_and_wrap',(14,-21,28,-14),7,-1)
    p.sketch('Finger_slip_pocket_profile')
    p.rectangle(14.9,-20.1,27.1,-14.9)
    p.extrude('Open_top_slip_pocket',7,True,0,through=False)
    p.sketch('Servo_ear_sweep_relief_profile')
    p.rectangle(13,-16,29,-13)
    p.extrude('Servo_ear_sweep_relief',3.2,True,3.8,through=False)
    holes(p,'Pad_capture_M2',[(18,-17.5),(24,-17.5)],2.2)
    return p.save()

BUILDERS={'servos': [servo_sg90,servo_mg996], 'links':[upper,forearm,moving_jaw],
          'coupon':[coupon], 'base':[base], 'yoke':[yoke,yaw_collar],
          'support':[cheek,shoulder_cheek,spacer,pin_sleeve],
          'core':[base,yoke,yaw_collar,upper,forearm,moving_jaw],
          'revision_b':[base,yoke,yaw_collar,upper,forearm,moving_jaw,cheek,shoulder_cheek,spacer,pin_sleeve,shoulder_spacer,keeper,sg_horn,mg_horn],
          'detail_update':[moving_jaw,keeper], 'cassette':[base,cassette],
          'fastener_clearances':[forearm,yaw_collar,cheek,shoulder_cheek],
          'pads':[moving_jaw,fixed_pad,moving_pad]}
BUILDERS['assembly_fixes']=[forearm,yaw_collar,moving_jaw,fixed_pad,moving_pad]
BUILDERS['keeper_seat']=[keeper]
BUILDERS['final_seats']=[upper,keeper]
BUILDERS['finger_wall']=[moving_jaw,moving_pad]
BUILDERS['pad_relief_and_coupon']=[moving_pad,coupon]
if __name__=='__main__':
    import sys
    group=sys.argv[1] if len(sys.argv)>1 else 'links'
    sw=connect()
    previous=sw.GetUserPreferenceToggle(16)
    try:
        sw.SetUserPreferenceToggle(16,False)
        report=[]
        for builder in BUILDERS[group]:
            report.append(builder(sw))
            (ROOT/('build-'+group+'.json')).write_text(json.dumps(report,indent=2))
    finally:
        sw.SetUserPreferenceToggle(16,previous)
