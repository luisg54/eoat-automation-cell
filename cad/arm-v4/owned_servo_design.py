"""Revision D interfaces derived from the measured owned-servo files.

All lengths are mm in the servo interface frame recorded in owned-servo-measurements.json:
origin on the output axis in the ear-underside plane, +Z along the output, +X toward the
far end of the case. Nothing here comes from the earlier nominal HW-003/HW-004 envelopes,
the assumed OD20/PCD14 metal horn or the assumed 13.2 mm SG90 horn height.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
M = json.loads((ROOT/'owned-servo-measurements.json').read_text())
MG, SG = M['MG996R'], M['SG90']

# ---- MG996R, shoulder and elbow -------------------------------------------------------
MG_FILE = 'MG996R_servo'
MG_EAR_HOLES = [(x, y) for x in MG['ears']['hole_x_from_axis_mm'] for y in MG['ears']['hole_y_mm']]
MG_EAR_NEAR = MG['ears']['thickness_output_end_mm']     # ear on the output end (x < 0)
MG_EAR_FAR = MG['ears']['thickness_far_end_mm']         # modeled thinner far ear (x > 0)
MG_CASE_BOTTOM_X = MG['case']['x_from_axis_at_bottom_mm']  # widest section passes the window
MG_CASE_WIDTH = MG['case']['width_mm']
MG_SPLINE_TOP = MG['output_spline']['top_above_ear_underside_mm']      # 15.5
MG_RING_TOP = MG['output_ring']['top_above_ear_underside_mm']          # 12.0, highest case face
MG_TIP_D = MG['output_spline']['tip_diameter_mm']                      # 5.997
MG_THREAD_DEPTH = MG['centre_screw_hole']['depth_from_spline_top_mm']  # 8.19, M3
WINDOW_CLEARANCE = 0.5
MG_WINDOW = (MG_CASE_BOTTOM_X[0]-WINDOW_CLEARANCE, -(MG_CASE_WIDTH/2+WINDOW_CLEARANCE),
             MG_CASE_BOTTOM_X[1]+WINDOW_CLEARANCE, MG_CASE_WIDTH/2+WINDOW_CLEARANCE)
MG_PLATE = 4.0            # existing upright plate and upper-link servo pad thickness
MG_EAR_SCREW = 14         # M3 x 14 through each slotted D4 ear, two washers, nyloc

# Printed spline hub ARM-207 replaces the unowned metal horn. Its underside clears the
# output ring; its floor seats on the spline top so the links keep their existing Z.
HUB_GAP = 0.5
HUB_FLOOR = 1.0
HUB_THICKNESS = MG_SPLINE_TOP+HUB_FLOOR-(MG_RING_TOP+HUB_GAP)            # 4.0
HUB_UNDERSIDE = MG_RING_TOP+HUB_GAP                                        # 12.5 above ears
LINK_REAR_ABOVE_EARS = HUB_UNDERSIDE+HUB_THICKNESS                         # 16.5
HUB_OD = 28.0
HUB_SOCKET_D = 5.80        # nominal press/broach fit on the 5.997 tip diameter; FIT-003 selects
HUB_SOCKET_DEPTH = MG_SPLINE_TOP-HUB_UNDERSIDE                             # 3.0 engagement
HUB_PCD = 18.0
HUB_POINTS = [(HUB_PCD/2, 0), (0, HUB_PCD/2), (-HUB_PCD/2, 0), (0, -HUB_PCD/2)]
HUB_NUT_AF = 5.7           # M3 hex nut AF5.5 plus clearance
HUB_NUT_RECESS = 0.5
HUB_NUT_POCKET = HUB_NUT_RECESS+2.4
HUB_SCREW = 12             # M3 x 12 from the link face; tip meets the recessed nut underside
MG_CENTRE_SCREW = 8        # M3 x 8 low head (DIN 7984, D5.5 x 2.0) into the spline thread
MG_CENTRE_HEAD = 2.0

# ---- SG90, yaw -------------------------------------------------------------------------
SG_FILE = 'SERVO_SG90'
SG_EAR_HOLES = [(x, 0.0) for x in SG['ears']['hole_x_from_axis_mm']]
SG_EAR = SG['ears']['thickness_mm']
SG_COVER_TOP = SG['gear_cover']['top_above_ear_underside_mm']          # 11.4
SG_SPLINE_TOP = SG['output_spline']['top_above_ear_underside_mm']      # 14.4
SG_SPLINE_D = SG['output_spline']['diameter_mm']
SG_SHELF_TOP_WORLD_Y = 25.4   # existing ARM-004 shelf top; the ear underside seats here
SG_SHELF = 4.0
SG_EAR_SCREW = 10             # M2 x 10, no washers: hole centres are 2.4 mm from the case walls
COLLAR_GAP = 0.5
COLLAR_SOCKET_BOTTOM_Y = SG_SHELF_TOP_WORLD_Y+SG_COVER_TOP+COLLAR_GAP   # 37.3
COLLAR_SPLINE_TOP_Y = SG_SHELF_TOP_WORLD_Y+SG_SPLINE_TOP                # 39.8
COLLAR_FLOOR_TOP_Y = 41.0     # existing collar flange underside
COLLAR_SOCKET_D = 4.85        # nominal press fit on the modeled 5.0 spline; FIT-004 selects
COLLAR_BOSS_OD = 12.0
SG_CENTRE_SCREW = 4           # M2 x 4 pan head (D4.0 x 1.6), the servo's own horn screw class
SG_CENTRE_HEAD = 1.6
YAW_SPINDLE_END_Y = 43.0      # existing ARM-202 spindle end, must clear the screw head

# ---- transforms ------------------------------------------------------------------------
def file_rotation(servo):
    f = servo['file_frame_to_interface']
    return [f['interface_X_in_file'], f['interface_Y_in_file'], f['interface_Z_in_file']]

def matmul(a, b):
    return [[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]

def servo_transform(servo, mount_rotation, mount_origin):
    """Component rotation (columns are file axes in world) and translation for a servo
    whose interface frame is placed at mount_origin with mount_rotation."""
    rot = matmul(mount_rotation, file_rotation(servo))
    f0 = servo['file_frame_to_interface']['origin_file_mm']
    pos = [mount_origin[i]-sum(rot[i][j]*f0[j] for j in range(3)) for i in range(3)]
    return rot, pos

def checks():
    assert abs(HUB_THICKNESS-4.0) < 1e-9 and abs(LINK_REAR_ABOVE_EARS-16.5) < 1e-9
    assert abs(HUB_SOCKET_DEPTH-3.0) < 1e-9
    assert abs(COLLAR_SPLINE_TOP_Y-39.8) < 1e-9 and abs(COLLAR_SOCKET_BOTTOM_Y-37.3) < 1e-9
    assert COLLAR_FLOOR_TOP_Y+SG_CENTRE_HEAD <= YAW_SPINDLE_END_Y-0.3
    # Screw engagement and tip positions (ear-underside frame).
    assert MG_SPLINE_TOP+HUB_FLOOR-MG_CENTRE_SCREW > MG_SPLINE_TOP-MG_THREAD_DEPTH
    return True

checks()
