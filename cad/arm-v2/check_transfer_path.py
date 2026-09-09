"""Sample proposed pickup-to-transfer motion; discrete samples are not a swept proof."""
from check_motion import run
samples=[]
for i in range(6):
 t=i/5
 samples.append((f'lift_{i}',0,-30+50*t,-60+40*t,10))
for angle in (-60,-40,-20,20,40,60):
 samples.append((f'yaw_{angle}',angle,20,-20,10))
run(samples,'transfer-path-inspection.json')
