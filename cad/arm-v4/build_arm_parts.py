"""Revision C native arm components. Development geometry, verify before printing."""
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

SG_CAP_POINTS=[(7,7),(-7,7),(-7,-7),(7,-7)]
SG_BLADE_WIDTH=4.0  # Undimensioned supplier outline: tune to the actual supplied horn.
SG_EAR_THICKNESS=2.4
SG_HORN_FRONT_FROM_EAR=13.2  # Seated-horn assumption; measure owned servo before release.
SG_EAR_TOP=4+SG_EAR_THICKNESS
SG_LINK_OFFSET=SG_EAR_TOP+SG_HORN_FRONT_FROM_EAR
SG_CAP_RECESS=.55
YAW_EAR_TOP=41-SG_HORN_FRONT_FROM_EAR
ELBOW_BEARING_OFFSET=SG_LINK_OFFSET+13

def sg_horn_seat(p,seat=0,plane='Front Plane',clearance=.10):
    """External key pocket preserves the fully seated stock horn's axial datum."""
    back=seat-1.65; half=SG_BLADE_WIDTH/2; tip=10.15-half
    round_feature(p,'Captured_horn_key_boss',0,0,26,1.65,offset=back,plane=plane)
    profiles=[('Hub',None,[(0,0,3.45+clearance)]),
              ('Horizontal',(-tip,-half-clearance,tip,half+clearance),[]),
              ('Vertical',(-half-clearance,-tip,half+clearance,tip),[]),
              ('Rounded_tips',None,[(tip,0,half+clearance),(-tip,0,half+clearance),
                                     (0,tip,half+clearance),(0,-tip,half+clearance)])]
    for label,bounds,circles in profiles:
        p.sketch('Stock_horn_pocket_'+label,plane)
        if bounds: p.rectangle(*bounds)
        for x,y,r in circles: p.circle(x,y,r)
        p.extrude('Key_pocket_'+label,1.65,True,back,through=False)
    holes(p,'Unmodified_horn_capture_M2',SG_CAP_POINTS,2.3,plane=plane)
    p.sketch('Horn_center_hub_clearance',plane)
    p.circle(0,0,4)
    # Limit this cut to the added boss; a through cut would erase the yaw D key.
    p.extrude('Hub_clearance_in_key_boss_only',1.65,True,back,through=False)

def sg_capture_cap(sw):
    p=Part(sw,'ARM-112_SG90_horn_capture_cap')
    round_feature(p,'Cap_OD26_ID8_thickness2',0,0,26,2,8)
    holes(p,'Four_M2_capture_holes',SG_CAP_POINTS,2.3)
    p.sketch('Low_profile_head_seats')
    for x,y in SG_CAP_POINTS: p.circle(x,y,2.1)
    p.extrude('Head_recess_depth0p55',SG_CAP_RECESS,True,0,through=False)
    return p.save()

def sg_fit_coupon(sw,clearance):
    code=str(int(round(clearance*100))).zfill(2)
    p=Part(sw,'FIT-002_SG90_horn_pocket_clearance_0p'+code)
    round_feature(p,'Trial_load_plate',0,0,26,4,8)
    sg_horn_seat(p,clearance=clearance)
    return p.save()

def servo_sg90(sw):
    p=Part(sw,'HW-003_SG90_NOMINAL_VERIFY')
    box(p,'Case_conservative_plan_23x12p2',(-6,-6.1,17,6.1),22.6,-18.3)
    box(p,'Mounting_ears_33x12p2',(-11,-6.1,22,6.1),SG_EAR_THICKNESS,-SG_EAR_THICKNESS)
    round_feature(p,'Raised_gear_cover_envelope',0,0,12.2,4.5,offset=4.3)
    round_feature(p,'Secondary_gear_cover_envelope',6,0,5.6,4.5,offset=4.3)
    round_feature(p,'Output_envelope_not_spline',0,0,5,3.6,offset=8.8)
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
    holes(p,'Cable_tie_holes',[(27,-3),(27,3)],3.2)
    round_feature(p,'Passive_lower_mount_boss',35,-9,10,4)
    round_feature(p,'Passive_upper_mount_boss',35,9,10,4)
    holes(p,'Passive_cheek_standoffs',[(35,-9),(35,9)],3.2)
    round_feature(p,'Shoulder_dowel_support_hub',0,0,14,4,8,4)
    # Raise the washers above the 7 mm sleeve, so their inner edges cannot pinch it.
    p.sketch('Raised_M3_washer_seats_PCD14_profile')
    for x,y in [(7,0),(-7,0),(0,7),(0,-7)]: p.circle(x,y,3.5)
    p.extrude('Raised_M3_washer_seats_height8',4,False,4)
    holes(p,'Metal_horn_M3_clearance_PCD14',[(7,0),(-7,0),(0,7),(0,-7)],3.2)
    holes(p,'Restore_shoulder_sleeve_bore',[(0,0)],8)
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
    sg_horn_seat(p)
    # Pad-retention fasteners are normal to the print plane; a pad keeper captures rubber.
    holes(p,'Fixed_pad_keeper_fasteners',[(57,-13.5),(73,-13.5)],2.2)
    return p.save()

def moving_jaw(sw):
    p=Part(sw,'ARM-103_Grip_moving_finger')
    # Origin at grip servo axis; nominal contact point is (20,-7).
    round_feature(p,'Stock_horn_attachment',0,0,26,3,offset=SG_LINK_OFFSET)
    box(p,'Finger_arm',(0,-19,27,3),3,SG_LINK_OFFSET)
    box(p,'Descending_contact_finger',(15,-20,27,-15),SG_LINK_OFFSET+3)
    holes(p,'Horn_center_access',[(0,0)],6)
    sg_horn_seat(p,seat=SG_LINK_OFFSET)
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
    round_feature(p,'Stock_horn_drive_flange',0,0,26,3,8.1,41,'Top Plane')
    round_feature(p,'D_coupling_ring',0,0,14,4,8.1,44,'Top Plane')
    box(p,'D_key_land',(3.1,-2.4,6,2.4),4,44,plane='Top Plane')
    sg_horn_seat(p,seat=41,plane='Top Plane')
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
    p=Part(sw,'ARM-106_M3_standoff_28p6mm')
    round_feature(p,'Standoff_OD8_ID3p2',0,0,8,ELBOW_BEARING_OFFSET-4,3.2)
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
    p=Part(sw,'HW-005_SG90_COMPACT_CROSS_REFERENCE')
    half=SG_BLADE_WIDTH/2; tip=10.15-half
    round_feature(p,'Compact_horn_center_OD6p9',0,0,6.9,1.5)
    box(p,'Horizontal_blades_assumed_width4',(-tip,-half,tip,half),1.5)
    box(p,'Vertical_blades_assumed_width4',(-half,-tip,half,tip),1.5)
    p.sketch('Rounded_blade_tips')
    for x,y in [(tip,0),(-tip,0),(0,tip),(0,-tip)]: p.circle(x,y,half)
    p.extrude('Rounded_tips_span20p3',1.5)
    round_feature(p,'Hub_projection2p5_total_height4',0,0,6.9,2.5,offset=-2.5)
    holes(p,'Purchased_spline_internals_omitted',[(0,0)],5.1)
    holes(p,'Unmodified_stock_pilot_holes',[(r,0) for r in (-8.3,-6.3,-4.3,4.3,6.3,8.3)]+
          [(0,r) for r in (-8.3,-6.3,-4.3,4.3,6.3,8.3)],1)
    return p.save(True)

def mg_horn(sw):
    p=Part(sw,'HW-006_MG996_25T_D20_PCD14_HORN')
    # Supplier disc: OD20, plate2, hub OD9 x2.5, M3 on PCD14.
    # Spline/center-screw internals are omitted; bore6.1 is a collision envelope,
    # not a manufactured spline dimension. Retain the purchased 25T interface.
    round_feature(p,'Metal_disc_OD20_thickness2',0,0,20,2,6.1)
    round_feature(p,'Purchased_25T_hub_envelope_OD9',0,0,9,2.5,6.1,-2.5)
    holes(p,'Four_M3_tapped_hole_envelopes_PCD14',[(-7,0),(7,0),(0,-7),(0,7)],3)
    return p.save(True)

def cassette(sw):
    p=Part(sw,'ARM-004_Removable_yaw_servo_mount')
    box(p,'Servo_shelf',(-21,-18,25,18),4,YAW_EAR_TOP-SG_EAR_TOP,plane='Top Plane')
    box(p,'Rear_clamping_block',(-21,23,-14,33),36,-18)
    box(p,'Servo_body_window',(-6.4,-6.5,17.4,6.5),1,YAW_EAR_TOP-SG_EAR_TOP-1,plane='Top Plane',cut=True)
    holes(p,'Yaw_servo_M2_fasteners',[(-9,0),(20,0)],2.6,YAW_EAR_TOP-SG_EAR_TOP-1,'Top Plane')
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
BUILDERS['shoulder_interface']=[upper,mg_horn]
BUILDERS['sg90_interfaces']=[forearm,moving_jaw,yaw_collar,sg_horn,sg_capture_cap]
BUILDERS['sg90_fit_trials']=[lambda sw,c=c:sg_fit_coupon(sw,c) for c in (.05,.10,.15)]
BUILDERS['axial_stack']=[servo_sg90,sg_horn,cassette,moving_jaw,spacer,sg_capture_cap]
BUILDERS['cassette_only']=[cassette]
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
