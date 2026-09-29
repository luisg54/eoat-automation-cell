# Arm D — printing, assembly and commissioning

Open `cad/arm-v4/ARM-D_Modular_parallel_gripper_DEVELOPMENT.SLDASM`. This is the serviceable development revision, updated 2026-09-28 to the owned servo files `MG996R_servo.SLDPRT` (×2) and `SERVO_SG90.SLDPRT`. Owned motors: **two MG996Rs**, driving the shoulder and elbow, and **four SG90s**. One SG90 drives yaw; the other three are unused spares, useful for FIT-004 trials. The gripper's FS90-FB comes with the Pololu kit. It is **not a print release and is not physically qualified**. User revision C and `cad/arm-v3` are preserved.

## What changed in the owned-servo update

- **MG996R mounts (ARM-203 shoulder, ARM-201 elbow).**
  - Body windows are 41.7 × 21.0 mm. That is the file's widest case section (40.7 × 20.0 mm) plus 0.5 mm per side.
  - Ear holes are Ø3.4 on the measured 48.30 × 10.00 mm pattern, for M3 × 14 screws with two washers and a nyloc each. These replace the nominal holes and the M2.5 hardware.
- **ARM-207 printed spline hub (×2) replaces the metal horn.** The files contain no horn, so each hub fits the 25-tooth spline directly:
  - Ø5.80 mm press socket on the Ø5.997 mm spline, 3.0 mm engagement.
  - The underside sits 0.5 mm above the output ring. The 1.0 mm floor seats on the spline top and is clamped by an M3 × 8 low-head centre screw.
  - Four M3 × 12 screws on an 18 mm circle go into captured nuts.
  - The link rear faces stay 16.5 mm above the ear underside, so dowels, sleeves, cheeks, standoffs and M3 × 50 stacks are unchanged.
- **ARM-201 and ARM-204.** The link bolt circle moves from PCD14 to PCD18, with new raised washer seats. The metal-horn holes are suppressed.
- **SG90 yaw.**
  - ARM-004 ear holes move to the measured 27.8 mm pitch (−8.4 / +19.4 mm from the output axis).
  - ARM-003 loses its horn pocket and gains a Ø12 boss with a Ø4.85 × 2.5 mm press socket, 0.5 mm above the gear cover. Its 1.2 mm floor seats on the spline top, retained by the servo's own M2 horn screw.
  - The ARM-003 crossbolt hole opens to Ø2.8, giving ±0.4 mm axial float. The arm's weight then stays on the 608 bearings instead of the SG90 output.
  - ARM-112 and its low-profile screws are no longer needed.
- **Pickup trial pose** is now shoulder −15° / elbow −75° (was −15° / −80°). The forearm is vertical, so the jaws close coaxially with the 608ZZ pin.

## Owned-servo geometry used (native measurement, not calipers)

- **MG996R** (native part; case and spline bodies; no horn, no cable, no material):
  - Ear underside is the mounting datum. Ear thickness in the file: 2.40 mm at the output end, 1.754 mm at the far end.
  - Ø4.0 open-slot holes at −14.15 / +34.15 × ±5.00 mm from the output axis.
  - Case 40.0–40.7 × 20.0 mm, 27.99 mm below the ear underside.
  - Output ring (Ø10.8) top is 12.0 mm above the ears. The 25-tooth spline (tip Ø5.997, root ≈Ø5.42) reaches 15.5 mm, 3.5 mm exposed.
  - M3 centre thread, 8.19 mm deep.
- **SG90** (STEP import; case, spline and three cable stubs; no horn, no material):
  - Ears 2.4 mm thick with Ø2.5 open-slot holes at −8.4 / +19.4 mm.
  - Case 12.0 × 23.0 mm.
  - Gear cover (Ø12 plus a Ø5 lobe) top is 11.4 mm above the ear underside (9.0 above the ear top).
  - Plain Ø5.0 spline with 40 shallow grooves and no tooth form, 3.0 mm exposed, top 14.4 mm above the ear underside.
  - Ø1.0 plain centre hole.
  - Three Ø1.2 cable stubs exit the output end 12.7 mm below the ears.

## Native controls and verified state

Six named configurations cover home, 22 mm grip, pickup and three transfer poses. `07_Free_motion_CHECK_COLLISIONS` releases the three arm angles with provisional limits; it does not certify every combined pose.

- Physical yaw: −60 to +60°. D1@J1_Yaw_command = 90° + yaw.
- Shoulder: −15 to +80°. D1@J2_Shoulder_command = 90° + shoulder.
- Elbow: −100 to −5°. D1@J3_Elbow_command = −elbow.
- Edit the **Gripper_opening** global variable, provisionally **2–32 mm**. It drives both jaws symmetrically.

**Verified 2026-09-28 on the reopened assembly:**

- **References:** 191 active components, all resolving inside `arm-v4` across 38 unique parts. 75 superseded components and their mates suppressed in every configuration.
- **Solver and features:** zero mate errors, zero part feature errors. The six saved poses match the kinematic model within 1.1e-15 of the stored transforms.
- **Revision C:** 38 files unchanged by hash.
- **Interference:** native solid interference was checked in all six saved configurations, plus 11 review poses and 19 transfer/lift samples. There are **0 unexpected overlaps**.
  - Each state shows the same 93 designed engagements, reported separately: the hub and collar press fits on the modeled splines, and the centre screws in the M3 thread and the SG90's Ø1.0 hole.
  - Full 0 mm closure shows 2 small supplier-model overlaps, outside the 2–32 mm working range.
- **Limits:** these are discrete samples, not a swept proof. Cables, external fixtures and a real payload are not covered.

## Material and printing

Use **PETG for the first structural set**. Follow the actual filament and printer profile, not universal temperature settings. [Prusa PETG guidance](https://help.prusa3d.com/article/petg_2059)

Starting process proposal: 0.4 mm nozzle, 0.20 mm layers, 5–6 walls, 5 top/bottom layers, 35–50% infill on broad structures, locally solid bearing seats and bolt regions. These are trial settings, not a validated strength specification.

- **ARM-207 hubs and ARM-003 collar:** print **solid**, socket face down on the bed so the socket is in the most accurate XY plane. Use 0.12–0.16 mm layers if the printer allows. FDM will not reproduce spline teeth; the socket is a press/broach fit whose bore is selected with the coupons.
- **Base ARM-001:** foot flat on the bed. Support the elevated bridge as needed; keep support scars out of bearing seats.
- **Platform ARM-202:** broad upper face on the bed, spindle up.
- **Upright ARM-203:** foot on the bed, supports for the servo-window roof as needed.
- **Upper ARM-201 and forearm ARM-204:** rear face on the bed (still flat; the hub is a separate part), hubs up.
- **Fork ARM-205:** base flat. Clean the two 4.3 mm holes.
- **Cheeks, keepers, cassette:** broad mounting faces on the bed. Print sleeves and standoffs with bores vertical.

Use only `cad/arm-v4/fabrication-trial/manifest.json` and its 18 listed files (refreshed 2026-09-28 for the changed parts). Never print HW reference parts or anything under `superseded-2026-09-28`.

## Fit trials first

1. **FIT-003 (MG996R).** Sockets Ø5.70 / 5.80 / 5.90 / 6.00, 3.0 mm deep, from the orientation mark. Press each onto a centred owned MG996R, fit the M3 centre screw, then check:
   - the coupon floor seats on the spline top, leaving about 0.5 mm above the output ring;
   - there is no cracking;
   - it doesn't slip under a gentle hand torque well above the 0.24 N·m shoulder design torque.
2. **FIT-004 (SG90).** Sockets Ø4.65 / 4.75 / 4.85 / 4.95, 2.5 mm deep, tested the same way on a spare SG90.
3. **Apply the result.** Set the selected bores in ARM-207 (modeled Ø5.80) and ARM-003 (modeled Ø4.85), then re-run the CAD verification.
4. **FIT-001:** bearing seat and dowel fits, as before.

## Assembly, tool to base

1. **Purchased gripper:** assemble the kit using the [supplier's guide](https://www.pololu.com/docs/0J76). Verify both paddles slide freely.
2. **Fork and crush spacers:** fit the two ARM-206 spacers between the plastic ears. Fit two M4 × 35 screws, two washers each and M4 nylocs. Tighten only enough to remove play, then confirm jaw travel.
3. **Forearm tool deck:** fasten ARM-205 to ARM-204 with four M3 × 14, two washers each and nylocs, before fitting the forearm to the elbow.
4. **Elbow servo:**
   - Drop the elbow MG996R through the ARM-201 window. Fasten each ear with M3 × 14, a washer on the ear, a washer and nyloc under the link.
   - Centre the servo electrically.
   - Seat four M3 hex nuts in an ARM-207 hub, press the hub onto the spline until its floor bottoms on the spline top, and fit the M3 × 8 low-head centre screw.
   - Fit ARM-204 onto the hub with four M3 × 12 and washers into the captured nuts.
5. **Elbow passive support (unchanged):**
   - Slide the link-side ARM-107 sleeve into the forearm bore over the centre-screw head (the head sits inside the sleeve with 1.0 mm to the dowel end).
   - Install the dowel and the second sleeve.
   - Fit the 608 in ARM-104 with its ARM-109 keeper and three M2 × 14 stacks.
   - Mount the cheek on two 32 mm ARM-108 standoffs with M3 × 50 stacks.
6. **Shoulder:** repeat the MG996R, hub, centre-screw and M3 × 12 sequence at ARM-203 and ARM-201. Then fit the shoulder dowel, sleeves, 608, ARM-105 cheek, ARM-109 keeper, standoffs and M3 × 50 stacks.
7. **Upright to platform:** nylocs in ARM-202's underside recesses, then four M3 × 14 with washers.
8. **Yaw:**
   - Fit two 608s in ARM-001.
   - Fasten the SG90 in ARM-004 with two M2 × 10, no washers, and M2 nuts under the shelf, flats toward the case.
   - Press ARM-003 onto the spline until its floor seats, then fit the SG90's own horn screw through the collar floor.
   - Mount the cassette with two M3 × 30 stacks.
   - Lower the platform spindle through the bearings into the collar D-key and fit the M2 × 20 crossbolt stack.
   - Check by hand that the spindle shoulder rests on the upper 608 inner race: the Ø2.8 collar hole should let the bolt float. Also check about 0.4 mm between the horn-screw head and the spindle end.
9. **Bench and cables:**
   - Clamp the 140 × 120 mm base.
   - The SG90 cable leaves the output end below the shelf; the MG996R cable is not in its file.
   - The shoulder, elbow and gripper cables must cross the ±60° yaw joint with a service loop.
   - Route strain-relieved loops outside every sweep and check screwdriver access. CAD does not model flexible wires.

## Pickup, lift and transfer

At `03_Pickup_trial` the jaws hang vertically. The jaw tips are the gripper's lowest point, about 16.5 mm above the bench plane, beside the base (assembly z ≈ 75 mm). The pickup fixture must present the 608ZZ on its pin at that height.

For the first 10 mm off the pin, command a **Cartesian vertical lift** (planar inverse kinematics at the 90 mm grip point), not a joint-space move. The CAD samples show the forearm rotating only 1.14° over that lift with no horizontal drift. The joint angles are in `transfer-path-inspection.json`. After the bearing clears the pin, joint-space motion to the transfer pose was sampled clear.

## Loads, power and proof before repeated use

The solid-PETG/native-volume estimate is **639.3 g** for modeled hardware and prints, excluding supply and controller. The servo files carry no material, so reference masses are used: MG996R 55 g, SG90 9 g.

With a 20 g payload at 90 mm, cable allowances and a 1.25 load multiplier, the design torques are:

- **elbow: 0.077 N·m**, margin **3.58**;
- **shoulder: 0.243 N·m**, margin **1.14**.

Both are against an assumed 0.277 N·m operating budget (one-third reference stall, further reduced 10%). These are sizing assumptions, not measured servo ratings. The shoulder governs; do not add distal mass, payload or duty from these numbers alone.

Power servos from the separate regulated supply and rated distribution, sharing signal ground with the Mega. Keep motor current off the Mega regulator and breadboard rails. Use an accessible DC disconnect and support the arm when power is removed.

Calibrate one servo at a time with the arm supported, then try slow unloaded motion. The gripper's pulse range is unusually wide; find its usable endpoints gradually. Feedback indicates position, not grip force. Test retention over a catch surface at 5, 10 and 20 g. Record current, voltage, case temperature, drift, slips and hub or fastener movement.

For the next gate, run 50 pick/place cycles with at least 49 successes. Record placement spread and failures, inspect the hubs, sockets and printed joints, and repeat after a sustained-duty trial. No fit, cycle, thermal, grip-force or repeatability performance has been measured yet.
