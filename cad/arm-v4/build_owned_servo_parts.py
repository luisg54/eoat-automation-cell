"""Fit revision D's servo-touching parts to the owned MG996R/SG90 files.

Stages (run one at a time; each document is hidden, saved and closed):
  fasteners  new centre-screw envelopes for the owned servos
  hub        ARM-207 printed MG996R spline hub (replaces the unowned metal horn)
  coupons    FIT-003 / FIT-004 spline press-fit trials
  edits      ARM-203, ARM-201, ARM-204, ARM-003, ARM-004 in place

Existing parts are edited, never regenerated: superseded features are suppressed and
renamed, so the preserved user edge treatments and history remain in each file.
"""
import sys, json, math
from build_native import Part, ROOT, connect, call
from build_arm_parts import box, round_feature, holes
from build_revision_parts import inherited
import owned_servo_design as D

SUFFIX = '_SUPERSEDED_owned_servo'

def supersede(p, names):
    for name in names:
        f = p.doc.FeatureByName(name)
        if f is None: raise RuntimeError(f'{p.name}: missing feature {name}')
        if not call(f, 'SetSuppression2', 0, 2, None): raise RuntimeError(f'{p.name}: cannot suppress {name}')
        f.Name = name+SUFFIX
        p.features.append(name+SUFFIX)

def hexagon(p, cx, cy, af, angle_deg):
    r = af/math.sqrt(3)
    pts = [(cx+r*math.cos(math.radians(angle_deg+60*i)), cy+r*math.sin(math.radians(angle_deg+60*i))) for i in range(6)]
    for (x, y), (xx, yy) in zip(pts, pts[1:]+pts[:1]):
        p.sk.CreateLine(x/1000, y/1000, 0., xx/1000, yy/1000, 0.)

def blind_cut(p, name, plane, circles, depth, offset=0):
    p.sketch(name+'_profile', plane)
    for x, y, d in circles: p.circle(x, y, d/2)
    return p.extrude(name, depth, True, offset, through=False)

def screw_envelope(sw, name, d, length, head_d, head_h):
    p = Part(sw, name)
    round_feature(p, 'Shank_nominal_thread_envelope', 0, 0, d, length, offset=-length)
    round_feature(p, 'Head_envelope_D%s_H%s' % (str(head_d).replace('.', 'p'), str(head_h).replace('.', 'p')), 0, 0, head_d, head_h)
    return p.save(True)

def fasteners(sw):
    return [screw_envelope(sw, 'HW-S_M3x%d_LOW_HEAD_D5p5_H2_ENVELOPE' % D.MG_CENTRE_SCREW, 3, D.MG_CENTRE_SCREW, 5.5, D.MG_CENTRE_HEAD),
            screw_envelope(sw, 'HW-S_M2x%d_PAN_HEAD_D4_H1p6_ENVELOPE' % D.SG_CENTRE_SCREW, 2, D.SG_CENTRE_SCREW, 4.0, D.SG_CENTRE_HEAD)]

def hub(sw):
    """Servo-side face at Z=0 sits 0.5 mm above the output ring; the floor seats on the spline."""
    p = Part(sw, 'ARM-207_MG996R_printed_spline_hub')
    round_feature(p, 'Hub_disc_OD28_thickness4', 0, 0, D.HUB_OD, D.HUB_THICKNESS)
    blind_cut(p, 'MG996R_spline_press_socket_D5p80_depth3', 'Front Plane', [(0, 0, D.HUB_SOCKET_D)], D.HUB_SOCKET_DEPTH)
    holes(p, 'M3_centre_screw_clearance_through_floor', [(0, 0)], 3.4)
    holes(p, 'Link_M3_clearance_PCD18', D.HUB_POINTS, 3.4)
    p.sketch('Captured_M3_nut_pockets_AF5p7_profile')
    for x, y in D.HUB_POINTS:
        hexagon(p, x, y, D.HUB_NUT_AF, math.degrees(math.atan2(y, x))+30)
    p.extrude('Captured_M3_nut_pockets_depth2p9', D.HUB_NUT_POCKET, True, 0, through=False)
    return p.save()

def coupons(sw):
    rows = []
    p = Part(sw, 'FIT-003_MG996R_spline_socket_trial')
    box(p, 'Coupon_bar_64x14x4', (-32, -7, 32, 7), D.HUB_THICKNESS)
    sizes = (5.70, 5.80, 5.90, 6.00)
    blind_cut(p, 'Press_sockets_5p70_5p80_5p90_6p00_depth3', 'Front Plane', [(-22.5+15*i, 0, s) for i, s in enumerate(sizes)], D.HUB_SOCKET_DEPTH)
    holes(p, 'M3_centre_screw_clearance', [(-22.5+15*i, 0) for i in range(4)], 3.4)
    holes(p, 'Orientation_mark_at_smallest_socket', [(-30, 5)], 1.5)
    rows.append(p.save())
    p = Part(sw, 'FIT-004_SG90_spline_socket_trial')
    thickness = D.COLLAR_FLOOR_TOP_Y-D.COLLAR_SOCKET_BOTTOM_Y
    box(p, 'Coupon_bar_54x12x3p7', (-27, -6, 27, 6), thickness)
    sizes = (4.65, 4.75, 4.85, 4.95)
    blind_cut(p, 'Press_sockets_4p65_4p75_4p85_4p95_depth2p5', 'Front Plane', [(-18+12*i, 0, s) for i, s in enumerate(sizes)], D.COLLAR_SPLINE_TOP_Y-D.COLLAR_SOCKET_BOTTOM_Y)
    holes(p, 'M2_centre_screw_clearance', [(-18+12*i, 0) for i in range(4)], 2.4)
    holes(p, 'Orientation_mark_at_smallest_socket', [(-25, 4)], 1.5)
    rows.append(p.save())
    return rows

def upright(sw):
    p = inherited(sw, 'ARM-203_Bolted_shoulder_upright', 'ARM-203_Bolted_shoulder_upright')
    supersede(p, ['MG996_body_window', 'MG996_tab_mounts'])
    w = D.MG_WINDOW
    box(p, 'Owned_MG996R_body_window', (w[0], 122+w[1], w[2], 122+w[3]), 1, -5, cut=True)
    holes(p, 'Owned_MG996R_M3_ear_holes', [(x, 122+y) for x, y in D.MG_EAR_HOLES], 3.4)
    return p.save()

def upper(sw):
    p = inherited(sw, 'ARM-201_Upper_link_dual_MG996R', 'ARM-201_Upper_link_dual_MG996R')
    supersede(p, ['MG996R_elbow_body_clearance', 'MG996R_elbow_tab_fasteners', 'Metal_horn_M3_clearance_PCD14'])
    w = D.MG_WINDOW
    box(p, 'Owned_MG996R_elbow_body_window', (60+w[0], w[1], 60+w[2], w[3]), 1, -5, cut=True)
    holes(p, 'Owned_MG996R_elbow_M3_ear_holes', [(60+x, y) for x, y in D.MG_EAR_HOLES], 3.4)
    p.sketch('Printed_hub_washer_seats_PCD18_profile')
    for x, y in D.HUB_POINTS: p.circle(x, y, 3.5)
    p.extrude('Printed_hub_M3_washer_seats_PCD18', 4, False, 4)
    holes(p, 'Printed_hub_M3_clearance_PCD18', D.HUB_POINTS, 3.4)
    return p.save()

def forearm(sw):
    p = inherited(sw, 'ARM-204_Modular_forearm_MG996R', 'ARM-204_Modular_forearm_MG996R')
    supersede(p, ['Metal_horn_M3_pattern'])
    p.sketch('Printed_hub_washer_seats_PCD18_profile')
    for x, y in D.HUB_POINTS: p.circle(x, y, 3.5)
    p.extrude('Printed_hub_M3_washer_seats_PCD18', 4, False, 4)
    holes(p, 'Printed_hub_M3_clearance_PCD18', D.HUB_POINTS, 3.4)
    return p.save()

def collar(sw):
    p = inherited(sw, 'ARM-003_Yaw_D_drive_collar', 'ARM-003_Yaw_D_drive_collar')
    supersede(p, ['Captured_horn_key_boss', 'Key_pocket_Hub', 'Key_pocket_Horizontal', 'Key_pocket_Vertical',
                  'Key_pocket_Rounded_tips', 'Unmodified_horn_capture_M2', 'Hub_clearance_in_key_boss_only'])
    p.sketch('SG90_spline_socket_boss_profile', 'Top Plane')
    p.circle(0, 0, D.COLLAR_BOSS_OD/2)
    p.extrude('SG90_spline_socket_boss_OD12', D.COLLAR_FLOOR_TOP_Y-D.COLLAR_SOCKET_BOTTOM_Y, False, D.COLLAR_SOCKET_BOTTOM_Y)
    blind_cut(p, 'SG90_spline_press_socket_D4p85_depth2p5', 'Top Plane', [(0, 0, D.COLLAR_SOCKET_D)],
              D.COLLAR_SPLINE_TOP_Y-D.COLLAR_SOCKET_BOTTOM_Y, D.COLLAR_SOCKET_BOTTOM_Y)
    blind_cut(p, 'SG90_centre_screw_clearance_D2p4', 'Top Plane', [(0, 0, 2.4)],
              D.COLLAR_FLOOR_TOP_Y-D.COLLAR_SPLINE_TOP_Y, D.COLLAR_SPLINE_TOP_Y)
    return p.save()

def collar_float(sw):
    """The collar is axially located by the SG90 spline; float the crossbolt so the platform
    weight stays on the 608 bearings instead of the servo output (printed-stack tolerance)."""
    p = inherited(sw, 'ARM-003_Yaw_D_drive_collar', 'ARM-003_Yaw_D_drive_collar')
    # D2.8 gives the M2 crossbolt +/-0.4 mm axial float; D3.0 is tangent to the D-key land underside.
    holes(p, 'Crossbolt_axial_float_clearance_D2p8', [(0, 45.5)], 2.8, -10, 'Right Plane')
    return p.save()

def cassette(sw):
    p = inherited(sw, 'ARM-004_Removable_yaw_servo_mount', 'ARM-004_Removable_yaw_servo_mount')
    supersede(p, ['Yaw_servo_M2_fasteners'])
    holes(p, 'Owned_SG90_M2_ear_holes', [(x, 0) for x, _ in D.SG_EAR_HOLES], 2.4, D.SG_SHELF_TOP_WORLD_Y-D.SG_SHELF-1, 'Top Plane')
    return p.save()

STAGES = {'fasteners': [fasteners], 'hub': [hub], 'coupons': [coupons],
          'edits': [upright, upper, forearm, collar, cassette],
          'upright': [upright], 'upper': [upper], 'forearm': [forearm], 'collar': [collar], 'cassette': [cassette],
          'collar_float': [collar_float]}

if __name__ == '__main__':
    stage = sys.argv[1]
    sw = connect()
    toggle = sw.GetUserPreferenceToggle(16)
    report_path = ROOT/'owned-servo-parts-build.json'
    reports = json.loads(report_path.read_text()) if report_path.exists() else {}
    try:
        # Sketch dimensions need a model view, so the single part being built stays
        # visible; Part.save() closes it before the next document opens.
        sw.SetUserPreferenceToggle(16, False)
        for builder in STAGES[stage]:
            result = builder(sw)
            for row in (result if isinstance(result, list) else [result]):
                reports[row['name']] = row
            report_path.write_text(json.dumps(reports, indent=2))
    finally:
        sw.SetUserPreferenceToggle(16, toggle)
