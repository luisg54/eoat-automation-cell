REVISION D — DEVELOPMENT, owned-servo update 2026-09-28 (first D build 2026-09-12)

User-authored revision C fillets/chamfers were inspected and preserved before work.
The original cad/arm-v3 directory has not been regenerated or overwritten.

Owned servo geometry (authoritative, measured natively into owned-servo-measurements.json):
parts/MG996R_servo.SLDPRT   shoulder and elbow (two owned MG996Rs)
parts/SERVO_SG90.SLDPRT     yaw (one of four owned SG90s; three are unused spares)
Neither file contains a horn, so the joints drive straight off the splines.
The nominal HW-003/HW-004/HW-005/HW-006 envelopes, ARM-112 cap and their fasteners are
suppressed in every configuration of the D assembly (kept, not deleted).

Structural parts:
ARM-201 Upper link: owned MG996R elbow window/M3 ears; PCD18 hub bolt circle.
ARM-202 Yaw platform: derived from user C ARM-002; upright removed.
ARM-203 Shoulder upright: owned MG996R window and M3 ear holes; four-bolt foot.
ARM-204 Straight modular forearm: PCD18 hub bolt circle.
ARM-205 Removable Pololu 3551 gripper fork.
ARM-206 Two spacers preventing inward clamping of the gripper's plastic ears.
ARM-207 Printed MG996R spline hub (x2): press socket on the 25T spline, M3 centre screw.
ARM-003 Yaw collar: press socket on the SG90 spline; floating crossbolt hole.
ARM-004 Yaw cassette: SG90 ear holes on the measured 27.8 mm pitch.
FIT-003 / FIT-004: spline press-fit coupons. Print these, and FIT-001, first.

Scripts for this update: measure_owned_servos.py, owned_servo_design.py,
build_owned_servo_parts.py, update_owned_servo_assembly.py,
suppress_superseded_components.py; verification: check_motion.py,
check_transfer_path.py, save_pose_configurations.py, verify_saved_assembly.py.
One SolidWorks COM script at a time; restart SolidWorks if its working set nears 2 GB.

The supplier STEP and dimension drawing are preserved in source-reference.
HW-202 and HW-203 are purchased gripper reference geometry, not printed parts.
The gripper is a $29.95 candidate; supplier backorders were shown on 2026-09-12.

Use only fabrication-trial/manifest.json and its files for printing. Uncurated STL/STEP
files under parts are development exports, not a printing release. Do not print the parts
folder or fabrication-trial/superseded-2026-09-28.

development-debug/before-owned-servo-geometry-20260928-180253 holds the pre-update D.
development-debug/USER-C_20260912_original_references.SLDASM is a backup of C and
intentionally still references original C paths. It is not revision D.

Still required: servo spline press fits (FIT-003/FIT-004), bearing/dowel fits, calipering
the owned servos, tool access, cable routing, friction, temperature/current and repeated
cycles. More serviceable CAD does not establish production readiness without those tests.
