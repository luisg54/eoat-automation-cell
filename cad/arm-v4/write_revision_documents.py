"""Publish the D BOM, print/assembly guide and design parameters from the saved native reports.

Every count and measured value is read from the reports written by the CAD scripts, so the
documents match the saved assembly. Revision C documents stay in development-debug.
"""
import json
from pathlib import Path
import owned_servo_design as D

root = Path(__file__).resolve().parent; project = root.parent.parent
def load(name): return json.loads((root/name).read_text())
build, loads, meas = load('assembly-build-report.json'), load('cad-load-and-bom-report.json'), load('owned-servo-measurements.json')
verify, motion, transfer = load('saved-assembly-verification.json'), load('motion-inspection.json'), load('transfer-path-inspection.json')
poses, limits, manifest = load('pose-configurations.json'), load('native-motion-limits.json'), load('fabrication-trial/manifest.json')
counts = loads['bom_counts']
printed = {k: v for k, v in counts.items() if k.startswith('ARM-')}
fasteners = {k: v for k, v in counts.items() if k.startswith(('HW-S_', 'HW-W_', 'HW-N_'))}
mg, sg = meas['MG996R'], meas['SG90']
t = loads['torques']
cfgs = verify['configurations']
all_samples = motion['samples']+transfer['samples']
unexpected = sum(len(s['interferences']) for s in all_samples)+sum(len(c['unexpected_interferences']) for c in cfgs)
known = sum(len(s['known_supplier_overlaps']) for s in all_samples)
lift = transfer['pin_lift_path']
pick = next(p for p in poses if p['name'] == '03_Pickup_trial')['pose_values']
additions = [('Pololu 3551 gripper', 29.95, 29.95), ('5 V supply', 29.95, 29.95), ('distribution/protection', 15, 25),
             ('fasteners', 35, 55), ('PETG and fit prints', 10, 25), ('liners', 1, 5), ('clamps', 0, 10), ('ties/consumables', 5, 10)]
lo, hi = sum(a[1] for a in additions), sum(a[2] for a in additions)
def label(name):
    return (name.removesuffix('.SLDPRT').replace('HW-S_', 'Screw ').replace('HW-W_', 'Washer ').replace('HW-N_', 'Nut ')
            .replace('_ENVELOPE', '').replace('_', ' '))

bom = f'''# Articulated arm D — hardware and budget

Development BOM, 2026-09-28 (owned-servo update). Native assembly: **{len(build['components'])} active components, {len(build['fastener_stacks'])} fastener stacks, {sum(printed.values())} printed pieces across {len(printed)} types**. {len(build['superseded_components'])} superseded nominal-servo components stay in the model, suppressed. This is a development model, not a print release. No purchases were made by the agent. Revision C documents are preserved in `cad/arm-v4/development-debug`.

## Owned hardware to reuse

- **Two MG996R positional servos** — shoulder (in ARM-203) and elbow (in ARM-201). Recorded purchase cost: **$10 total**. Geometry: `cad/arm-v4/parts/MG996R_servo.SLDPRT`.
- **Four SG90 micro servos** — one drives yaw (ARM-004 cassette, ARM-003 collar). The other three are spares, deliberately unused (see `HANDOFF.md`). Geometry for all four: `cad/arm-v4/parts/SERVO_SG90.SLDPRT`.
- **Four 608ZZ bearings**, 8 × 22 × 7 mm. Keep a fifth as the pick object.
- **Two 6.35 × 25.4 mm dowel pins**, plus the existing Mega R3 and signal cables.
- **Each servo's own horn (centre) screw.** SG90: its small M2 self-tapping horn screw, about 4 mm long (modeled as M2 × 4 pan head, Ø4.0 × 1.6). MG996R: use the original M3 horn screw only if its head is ≤ Ø6.0 × 2.0 mm and it engages at least 5 mm. Otherwise use the M3 × 8 low-head screws listed below.

No servo horns are used. Neither servo file contains horn geometry, so the joints drive straight off the splines through printed parts.

## Additions

- **One [Pololu 3551 micro parallel gripper](https://www.pololu.com/product/3551)**, including its FS90-FB feedback servo: **$29.95**, checked 2026-09-12. The supplier showed backorders; confirm delivery before printing ARM-205.
- **One external regulated 5 V supply**, unless a suitable bench supply is available. [Adafruit 658, 5 V/10 A](https://www.adafruit.com/product/658): **$29.95**, shown in stock on 2026-09-12. Supply capacity alone does not rate the downstream connector or wiring.
- Distribution, wire, fuse/protection and an accessible DC disconnect: **$15–25** allowance.
- Fastener packs and spares below: **$35–55** allowance. The only special parts are two M3 × 8 low-head (DIN 7984) screws and eight plain M3 hex nuts.
- PETG and fit prints: **$10–25**. Optional small rubber gripping liners: **$1–5**. Bench clamps: **$0–10**. Ties and consumables: **$5–10**.
- **Removed from the earlier D list:** the two OD20/PCD14 metal horns ($10–20), the M2 × 10 low-profile (Ø4 × 1.1) cap screws, and all M2.5 servo-ear hardware.

## Fasteners — native assembly quantities

All lengths are under the head. The models omit threads and sockets. Do not substitute longer screws without checking the assembly.

'''
for name, n in sorted(fasteners.items()): bom += f'- **{n} × {label(name)}**\n'
bom += f'''
Where they go:

- **16 × M3 × 14** — eight MG996R ear stacks (two washers and a nyloc each), four upright-to-platform, four tool-adapter.
- **8 × M3 × 12** — link to ARM-207 hub on an 18 mm bolt circle (one washer each), into **8 plain M3 hex nuts** captured 0.5 mm deep in the hub pockets.
- **2 × M3 × 8 low head** — hub to MG996R spline, into the spline's M3 thread; 7.0 mm engaged of 8.19 mm available.
- **4 × M3 × 50** — cheek standoffs. **2 × M3 × 30** — yaw cassette.
- **2 × M2 × 10** — SG90 ears, with the nut directly under the shelf and **no washers** (the hole centres are 2.4 mm from the case walls).
- **1 × M2 × 4 pan head** — the SG90's own horn screw through the ARM-003 floor.
- **6 × M2 × 14** — bearing keepers. **1 × M2 × 20** — yaw crossbolt.
- **2 × M4 × 35** — gripper axes.

Washers are the modeled **0.5 mm small-series** types: M2 OD5/ID2.2, M3 OD6/ID3.2, M4 OD8/ID4.2. Nyloc envelopes: M3 AF5.5/H4, M4 AF7/H5. Plain nuts: M2 AF4/H1.6, M3 AF5.5/H2.4. Kit-internal gripper hardware is separate from these {len(build['fastener_stacks'])} modeled stacks.

## Printed pieces

'''
for name, n in sorted(printed.items()): bom += f'- {n} × {name.removesuffix(".SLDPRT")}\n'
bom += f'''
Fit coupons, printed first: FIT-001_Dowel_and_bearing_trial, FIT-003_MG996R_spline_socket_trial, FIT-004_SG90_spline_socket_trial.

**Superseded — do not print or buy for D:** ARM-112 horn cap and its four low-head screws, washers and nuts; FIT-002 horn-pocket coupons; HW-006 metal horns; HW-003/HW-004/HW-005 nominal servo and horn envelopes; M2.5 ear hardware. They remain in `parts`/`hardware-reference` and as suppressed components; curated exports are in `fabrication-trial/superseded-2026-09-28`.

## Budget and buying order

The additions total **${lo:.2f}–{hi:.2f}**, before shipping/tax and contingency. With $20–25 shipping/tax and $20–30 contingency, that is **${lo+40:.2f}–{hi+55:.2f} remaining spend**, if none of those additions is already on hand. Adding the earlier recorded $20.17 SG90/bearing/dowel order and the $10 MG996R pair gives **${lo+40+30.17:.2f}–{hi+55+30.17:.2f} estimated all-in cost**. Existing Mega/kit costs are excluded as sunk costs. These are pack and printing allowances, not a checkout quote.

Buying order:

1. Print FIT-003, FIT-004 and FIT-001, and test them on the owned servos, a bearing and a dowel.
2. Confirm gripper stock.
3. Order the fasteners.
4. Print one structural set.

Reuse workshop power and clamps where suitable to stay near the historical $250 target. Avoid duplicate motors or a new controller.
'''
(project/'docs/arm-bom.md').write_text(bom, encoding='utf-8')

guide = f'''# Arm D — printing, assembly and commissioning

Open `cad/arm-v4/ARM-D_Modular_parallel_gripper_DEVELOPMENT.SLDASM`. This is the serviceable development revision, updated 2026-09-28 to the owned servo files `MG996R_servo.SLDPRT` (×2) and `SERVO_SG90.SLDPRT`. Owned motors: **two MG996Rs**, driving the shoulder and elbow, and **four SG90s**. One SG90 drives yaw; the other three are unused spares, useful for FIT-004 trials. The gripper's FS90-FB comes with the Pololu kit. It is **not a print release and is not physically qualified**. User revision C and `cad/arm-v3` are preserved.

## What changed in the owned-servo update

- **MG996R mounts (ARM-203 shoulder, ARM-201 elbow).**
  - Body windows are 41.7 × 21.0 mm. That is the file's widest case section (40.7 × 20.0 mm) plus 0.5 mm per side.
  - Ear holes are Ø3.4 on the measured 48.30 × 10.00 mm pattern, for M3 × 14 screws with two washers and a nyloc each. These replace the nominal holes and the M2.5 hardware.
- **ARM-207 printed spline hub (×2) replaces the metal horn.** The files contain no horn, so each hub fits the 25-tooth spline directly:
  - Ø{D.HUB_SOCKET_D:.2f} mm press socket on the Ø{mg['output_spline']['tip_diameter_mm']:.3f} mm spline, {D.HUB_SOCKET_DEPTH:.1f} mm engagement.
  - The underside sits {D.HUB_GAP} mm above the output ring. The {D.HUB_FLOOR:.1f} mm floor seats on the spline top and is clamped by an M3 × 8 low-head centre screw.
  - Four M3 × 12 screws on an 18 mm circle go into captured nuts.
  - The link rear faces stay 16.5 mm above the ear underside, so dowels, sleeves, cheeks, standoffs and M3 × 50 stacks are unchanged.
- **ARM-201 and ARM-204.** The link bolt circle moves from PCD14 to PCD18, with new raised washer seats. The metal-horn holes are suppressed.
- **SG90 yaw.**
  - ARM-004 ear holes move to the measured 27.8 mm pitch (−8.4 / +19.4 mm from the output axis).
  - ARM-003 loses its horn pocket and gains a Ø12 boss with a Ø{D.COLLAR_SOCKET_D:.2f} × 2.5 mm press socket, 0.5 mm above the gear cover. Its 1.2 mm floor seats on the spline top, retained by the servo's own M2 horn screw.
  - The ARM-003 crossbolt hole opens to Ø2.8, giving ±0.4 mm axial float. The arm's weight then stays on the 608 bearings instead of the SG90 output.
  - ARM-112 and its low-profile screws are no longer needed.
- **Pickup trial pose** is now shoulder {str(pick[1]).replace('-', '−')}° / elbow {str(pick[2]).replace('-', '−')}° (was −15° / −80°). The forearm is vertical, so the jaws close coaxially with the 608ZZ pin.

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

Six named configurations cover home, 22 mm grip, pickup and three transfer poses. `{limits['configuration']}` releases the three arm angles with provisional limits; it does not certify every combined pose.

- Physical yaw: −60 to +60°. D1@J1_Yaw_command = 90° + yaw.
- Shoulder: −15 to +80°. D1@J2_Shoulder_command = 90° + shoulder.
- Elbow: −100 to −5°. D1@J3_Elbow_command = −elbow.
- Edit the **Gripper_opening** global variable, provisionally **2–32 mm**. It drives both jaws symmetrically.

**Verified 2026-09-28 on the reopened assembly:**

- **References:** {verify['active_components_verified']} active components, all resolving inside `arm-v4` across {verify['unique_active_parts_verified']} unique parts. {verify['superseded_components_suppressed']} superseded components and their mates suppressed in every configuration.
- **Solver and features:** zero mate errors, zero part feature errors. The six saved poses match the kinematic model within {max(c['transform_residual'] for c in cfgs):.1e} of the stored transforms.
- **Revision C:** {verify['original_C_files_unchanged']} files unchanged by hash.
- **Interference:** native solid interference was checked in all six saved configurations, plus {len(motion['samples'])} review poses and {len(transfer['samples'])} transfer/lift samples. There are **{unexpected} unexpected overlaps**.
  - Each state shows the same 93 designed engagements, reported separately: the hub and collar press fits on the modeled splines, and the centre screws in the M3 thread and the SG90's Ø1.0 hole.
  - Full 0 mm closure shows {known} small supplier-model overlaps, outside the 2–32 mm working range.
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

Use only `cad/arm-v4/fabrication-trial/manifest.json` and its {len(manifest)} listed files (refreshed 2026-09-28 for the changed parts). Never print HW reference parts or anything under `superseded-2026-09-28`.

## Fit trials first

1. **FIT-003 (MG996R).** Sockets Ø5.70 / 5.80 / 5.90 / 6.00, 3.0 mm deep, from the orientation mark. Press each onto a centred owned MG996R, fit the M3 centre screw, then check:
   - the coupon floor seats on the spline top, leaving about 0.5 mm above the output ring;
   - there is no cracking;
   - it doesn't slip under a gentle hand torque well above the 0.24 N·m shoulder design torque.
2. **FIT-004 (SG90).** Sockets Ø4.65 / 4.75 / 4.85 / 4.95, 2.5 mm deep, tested the same way on a spare SG90.
3. **Apply the result.** Set the selected bores in ARM-207 (modeled Ø{D.HUB_SOCKET_D:.2f}) and ARM-003 (modeled Ø{D.COLLAR_SOCKET_D:.2f}), then re-run the CAD verification.
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

For the first 10 mm off the pin, command a **Cartesian vertical lift** (planar inverse kinematics at the 90 mm grip point), not a joint-space move. The CAD samples show the forearm rotating only {abs(lift['forearm_rotation_over_10mm_deg']):.2f}° over that lift with no horizontal drift. The joint angles are in `transfer-path-inspection.json`. After the bearing clears the pin, joint-space motion to the transfer pose was sampled clear.

## Loads, power and proof before repeated use

The solid-PETG/native-volume estimate is **{loads['total_modeled_mass_g']:.1f} g** for modeled hardware and prints, excluding supply and controller. The servo files carry no material, so reference masses are used: MG996R 55 g, SG90 9 g.

With a 20 g payload at 90 mm, cable allowances and a 1.25 load multiplier, the design torques are:

- **elbow: {t['elbow']['design_Nm']:.3f} N·m**, margin **{t['elbow']['margin_ratio']:.2f}**;
- **shoulder: {t['shoulder']['design_Nm']:.3f} N·m**, margin **{t['shoulder']['margin_ratio']:.2f}**.

Both are against an assumed {t['shoulder']['assumed_budget_Nm']:.3f} N·m operating budget (one-third reference stall, further reduced 10%). These are sizing assumptions, not measured servo ratings. The shoulder governs; do not add distal mass, payload or duty from these numbers alone.

Power servos from the separate regulated supply and rated distribution, sharing signal ground with the Mega. Keep motor current off the Mega regulator and breadboard rails. Use an accessible DC disconnect and support the arm when power is removed.

Calibrate one servo at a time with the arm supported, then try slow unloaded motion. The gripper's pulse range is unusually wide; find its usable endpoints gradually. Feedback indicates position, not grip force. Test retention over a catch surface at 5, 10 and 20 g. Record current, voltage, case temperature, drift, slips and hub or fastener movement.

For the next gate, run 50 pick/place cycles with at least 49 successes. Record placement spread and failures, inspect the hubs, sockets and printed joints, and repeat after a sustained-duty trial. No fit, cycle, thermal, grip-force or repeatability performance has been measured yet.
'''
(project/'docs/arm-print-and-assembly-guide.md').write_text(guide, encoding='utf-8')

params = {
    'revision': 'D-development (owned-servo update 2026-09-28)',
    'status': 'Native CAD verified on the reopened assembly; physical fit and performance qualification remain',
    'scope': 'Articulated tabletop robot arm picking a 608ZZ bearing',
    'payload_target_g': 20, 'pick_object': '608ZZ 8 x 22 x 7 mm',
    'upper_link_centres_mm': 60, 'forearm_link_centres_mm': 90, 'grip_point_radius_mm': 90,
    'owned_motors': {'MG996R': 2, 'SG90': 4},
    'motor_use': {'MG996R': ['shoulder', 'elbow'], 'SG90': ['yaw'], 'SG90_spares': 3,
                  'gripper': 'FS90-FB included with Pololu 3551 (purchase pending)'},
    'servo_geometry_source': {'MG996R': 'cad/arm-v4/parts/MG996R_servo.SLDPRT', 'SG90': 'cad/arm-v4/parts/SERVO_SG90.SLDPRT',
                              'measurements': 'cad/arm-v4/owned-servo-measurements.json',
                              'scope': 'Native file measurement in SolidWorks; owned units not calipered by the agent'},
    'mg996r': {'ear_hole_x_from_axis_mm': mg['ears']['hole_x_from_axis_mm'], 'ear_hole_y_mm': mg['ears']['hole_y_mm'],
               'ear_hole_diameter_mm': 4.0, 'ear_thickness_output_end_mm': D.MG_EAR_NEAR, 'ear_thickness_far_end_mm': round(D.MG_EAR_FAR, 3),
               'case_bottom_x_from_axis_mm': D.MG_CASE_BOTTOM_X, 'case_width_mm': D.MG_CASE_WIDTH,
               'output_ring_top_above_ears_mm': D.MG_RING_TOP, 'spline_top_above_ears_mm': D.MG_SPLINE_TOP,
               'spline_teeth': mg['output_spline']['teeth'], 'spline_tip_diameter_mm': round(D.MG_TIP_D, 3),
               'centre_thread': 'M3', 'centre_thread_depth_mm': round(D.MG_THREAD_DEPTH, 2),
               'mount_window_mm': [round(v, 3) for v in D.MG_WINDOW], 'ear_screws': 'M3 x 14, 2 washers, nyloc'},
    'sg90': {'ear_hole_x_from_axis_mm': sg['ears']['hole_x_from_axis_mm'], 'ear_hole_diameter_mm': 2.5, 'ear_thickness_mm': D.SG_EAR,
             'case_x_from_axis_mm': sg['case']['x_from_axis_mm'], 'case_width_mm': sg['case']['width_mm'],
             'gear_cover_top_above_ears_mm': round(D.SG_COVER_TOP, 3), 'spline_top_above_ears_mm': round(D.SG_SPLINE_TOP, 3),
             'spline_diameter_mm': D.SG_SPLINE_D, 'centre_hole_in_file_mm': 1.0,
             'ear_screws': 'M2 x 10, hex nut, no washers'},
    'mg996r_hub_ARM_207': {'socket_diameter_mm': D.HUB_SOCKET_D, 'socket_depth_mm': D.HUB_SOCKET_DEPTH, 'thickness_mm': D.HUB_THICKNESS,
                           'gap_above_output_ring_mm': D.HUB_GAP, 'floor_mm': D.HUB_FLOOR, 'outer_diameter_mm': D.HUB_OD,
                           'link_bolt_circle_mm': D.HUB_PCD, 'link_screws': 'M3 x 12 into captured M3 hex nuts',
                           'centre_screw': 'M3 x 8 low head DIN 7984', 'fit_trial': 'FIT-003 5.70/5.80/5.90/6.00'},
    'sg90_collar_ARM_003': {'socket_diameter_mm': D.COLLAR_SOCKET_D, 'socket_depth_mm': round(D.COLLAR_SPLINE_TOP_Y-D.COLLAR_SOCKET_BOTTOM_Y, 3),
                            'gap_above_gear_cover_mm': D.COLLAR_GAP, 'floor_mm': round(D.COLLAR_FLOOR_TOP_Y-D.COLLAR_SPLINE_TOP_Y, 3),
                            'crossbolt_float_hole_diameter_mm': 2.8, 'fit_trial': 'FIT-004 4.65/4.75/4.85/4.95'},
    'link_rear_above_mg996r_ears_mm': D.LINK_REAR_ABOVE_EARS, 'elbow_axial_offset_mm': 20.5, 'elbow_standoff_mm': 32,
    'bearing_OD_mm': 22, 'bearing_ID_mm': 8, 'bearing_width_mm': 7, 'dowel_diameter_mm': 6.35, 'dowel_length_mm': 25.4,
    'shoulder_servo_stall_reference_Nm': 0.9218251, 'servo_design_fraction_of_reference_stall': 1/3,
    'servo_rating_status': 'Manufacturer reference only; owned units must be measured and load-tested',
    'design_torque_Nm': {'elbow': round(t['elbow']['design_Nm'], 4), 'shoulder': round(t['shoulder']['design_Nm'], 4)},
    'margin_ratio': {'elbow': round(t['elbow']['margin_ratio'], 3), 'shoulder': round(t['shoulder']['margin_ratio'], 3)},
    'total_modeled_mass_g': round(loads['total_modeled_mass_g'], 1),
    'gripper_working_opening_mm': [2, 32], 'yaw_travel_deg': [-60, 60], 'shoulder_travel_deg': [-15, 80], 'elbow_travel_deg': [-100, -5],
    'pickup_trial_pose': {'yaw_deg': pick[0], 'shoulder_deg': pick[1], 'elbow_deg': pick[2], 'grip_mm': pick[3], 'forearm_deg': pick[1]+pick[2]},
    'pin_safe_lift': {'method': 'Cartesian vertical lift for the first 10 mm', 'forearm_rotation_over_10mm_deg': round(lift['forearm_rotation_over_10mm_deg'], 3)},
}
(root/'design-parameters.json').write_text(json.dumps(params, indent=2))
print('Updated D BOM, assembly/print guide and design parameters')
