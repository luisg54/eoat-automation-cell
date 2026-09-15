"""Check lift/yaw samples and fully closed/reopened gripper states."""
from check_motion import run
samples=[('gripper_fully_closed',0,45,-45,0),('gripper_reopened',0,45,-45,32)]
for i in range(6):
    t=i/5
    samples.append((f'lift_{i}',0,-15+35*t,-80+60*t,22))
for angle in (-60,-40,-20,20,40,60): samples.append((f'yaw_{angle}',angle,20,-20,22))
run(samples,'transfer-path-inspection.json')
