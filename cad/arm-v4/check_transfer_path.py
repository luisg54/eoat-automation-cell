"""Check the pin-safe lift, the joint-space transfer and fully closed/reopened gripper states.

The 608ZZ leaves a 6.35 mm pin (standout up to 6 mm), so the first 10 mm are a Cartesian
vertical lift solved by planar inverse kinematics at the 90 mm grip point, not a joint
interpolation. The remaining move to the transfer pose is joint-interpolated.
"""
import json, math
from check_motion import run, ROOT
L1, L2 = 60.0, 90.0   # upper-link centres; forearm grip-point radius used by the load model
PICK = (-15, -75)   # 03_Pickup_trial: forearm vertical, jaws coaxial with the pin

def fk(s, e):
    s, e = math.radians(s), math.radians(e)
    return L1*math.cos(s)+L2*math.cos(s+e), L1*math.sin(s)+L2*math.sin(s+e)

def ik(x, y):
    c = (x*x+y*y-L1*L1-L2*L2)/(2*L1*L2)
    e = -math.acos(max(-1., min(1., c)))
    s = math.atan2(y, x)-math.atan2(L2*math.sin(e), L1+L2*math.cos(e))
    return math.degrees(s), math.degrees(e)

x0, y0 = fk(*PICK)
path = []
samples = [('gripper_fully_closed', 0, 45, -45, 0), ('gripper_reopened', 0, 45, -45, 32)]
for lift in (0, 2, 4, 6, 8, 10):
    s, e = ik(x0, y0+lift)
    gx, gy = fk(s, e)
    path.append({'lift_mm': lift, 'shoulder_deg': s, 'elbow_deg': e, 'forearm_angle_deg': s+e,
                 'grip_point_mm': [gx, gy], 'horizontal_drift_mm': gx-x0})
    samples.append((f'pin_lift_{lift}mm', 0, s, e, 22))
clear = ik(x0, y0+10)
for i in range(1, 6):
    t = i/5
    samples.append((f'lift_{i}', 0, clear[0]+(20-clear[0])*t, clear[1]+(-20-clear[1])*t, 22))
for angle in (-60, -40, -20, 20, 40, 60): samples.append((f'yaw_{angle}', angle, 20, -20, 22))
run(samples, 'transfer-path-inspection.json')
report = json.loads((ROOT/'transfer-path-inspection.json').read_text())
report['pin_lift_path'] = {'method': 'planar two-link IK at the 90 mm grip point; vertical lift from 03_Pickup_trial',
                           'forearm_rotation_over_10mm_deg': path[-1]['forearm_angle_deg']-path[0]['forearm_angle_deg'],
                           'samples': path}
(ROOT/'transfer-path-inspection.json').write_text(json.dumps(report, indent=2))
print('Pin lift forearm rotation over 10 mm:', round(report['pin_lift_path']['forearm_rotation_over_10mm_deg'], 3), 'deg', flush=True)
