"""Publish the D assembly/BOM guide from native counts; retain the C backups."""
import json
from pathlib import Path
from collections import Counter
root=Path(__file__).resolve().parent; project=root.parent.parent
build=json.loads((root/'assembly-build-report.json').read_text())
loads=json.loads((root/'cad-load-and-bom-report.json').read_text())
counts=loads['bom_counts']
printed={k:v for k,v in counts.items() if k.startswith('ARM-')}
fasteners={k:v for k,v in counts.items() if k.startswith(('HW-S_','HW-W_','HW-N_'))}
bom=f'''# Articulated arm D — hardware and budget

Development BOM, 2026-09-12. Native assembly: **{len(build['components'])} components, 45 fastener stacks, {sum(printed.values())} printed pieces across {len(printed)} types**. Purchasing/fabrication remains conditional on actual hardware fit. No purchases were made by the agent. Revision C documents are preserved in `cad/arm-v4/development-debug`.

## Owned hardware to reuse

- **Two MG996R positional servos:** shoulder and elbow. Both are already owned; do not buy another pair.
- **One SG90:** yaw, using its small equal-arm cross horn. Retain the other SG90s as spares.
- **Four 608ZZ bearings**, 8 × 22 × 7 mm. Reserve a fifth as a demonstration object.
- **Two 6.35 × 25.4 mm dowel pins**, plus the existing Mega R3 and signal cables.
- Keep the original horn-center screws belonging to each servo. They are not interchangeable generic screws.

## Additions

- **One [Pololu 3551 micro parallel gripper](https://www.pololu.com/product/3551)**, including its feedback servo: **$29.95** checked 2026-09-12. Supplier showed backorders; confirm delivery before printing its adapter. Official CAD is saved locally. This replaces C's printed fixed/moving fingers and their SG90.
- **Two compatible metal horns:** nominal 25T, OD20, four M3-tapped holes on PCD14, 2 mm plate with 2.5 mm rear hub. Allow **$10–20 total**. Confirm the actual horn drawing and seating on your MG996Rs; the provided plastic horns are not equivalent.
- **One external regulated 5 V supply**, unless a suitable bench supply is available. [Adafruit 658, 5 V/10 A](https://www.adafruit.com/product/658): **$29.95**, shown in stock on 2026-09-12. Supply capacity alone does not rate the downstream connector or wiring.
- Distribution, wire, fuse/protection and accessible DC disconnect: **$15–25** allowance.
- Fastener packs/spares below: **$35–55** allowance; quote the low-profile M2 screws and M3×14 specifically.
- PETG and fit prints: **$10–25**; optional small rubber gripping liners: **$1–5**; bench clamps: **$0–10**; ties/consumables: **$5–10**.

## Fasteners — native assembly quantities

All lengths are under the head. Models omit threads and sockets. Do not substitute longer screws without checking the assembly.

'''
for name,n in sorted(fasteners.items()):
    label=name.removesuffix('.SLDPRT').replace('HW-S_','Screw ').replace('HW-W_','Washer ').replace('HW-N_','Nut ').replace('_ENVELOPE','').replace('_',' ')
    bom+=f'- **{n} × {label}**\n'
bom+='''
M2 low-profile heads must be no larger than Ø4 × 1.1 mm; four are needed for the yaw horn cap. Ordinary socket heads do not fit that clearance. Washers are the modeled **0.5 mm small-series** types: M2 OD5/ID2.2, M2.5 OD5/ID2.7, M3 OD6/ID3.2, M4 OD8/ID4.2. Nyloc envelopes: M2.5 AF5/H3.5, M3 AF5.5/H4, M4 AF7/H5. Match these dimensions before ordering.

The eight M3×14 screws divide between the four recessed-nut upright mounts and four tool-adapter mounts. Eight M3×12 screws fasten the two metal horns. Four M3×50 screws support the shoulder/elbow cheeks. Two M3×30 mount the yaw cassette. Two M4×35 retain the gripper on its fork. Kit-internal gripper hardware and the original servo center screws are separate from these 45 modeled stacks.

## Printed pieces

'''
for name,n in sorted(printed.items()): bom+=f'- {n} × {name.removesuffix(".SLDPRT")}\n'
bom+='''
## Budget and buying order

The additions total **$135.90–209.90**, before shipping/tax and contingency. Allowing $20–25 shipping/tax and $20–30 contingency gives **$175.90–264.90 remaining spend** if none of those additions is already available. Including the earlier recorded $20.17 SG90/bearing/dowel order gives **$196.07–285.07 plus the actual price already paid for the MG996R pair**. That pair's receipt value is unknown, so a precise all-in total would be misleading. Existing Mega/kit costs are excluded as sunk costs. These are pack/printing allowances, not a checkout quote.

Confirm gripper stock and metal-horn geometry first. Print small horn/bearing/dowel trials next. Then order the final fasteners and one structural set. Reuse workshop power/clamps when suitable to stay near the historical $250 target. The user allows worthwhile functional improvements beyond that target; avoid duplicate motors or a new controller.
'''
(project/'docs/arm-bom.md').write_text(bom,encoding='utf-8')
guide=f'''# Arm D — printing, assembly and commissioning

Open `cad/arm-v4/ARM-D_Modular_parallel_gripper_DEVELOPMENT.SLDASM`. This is the serviceable development revision, with preserved user C files. It is **not physically qualified for production**. The native model uses a modular parallel gripper, two owned MG996Rs, and separate yaw platform/upright parts.

## What changed and why

- ARM-002's combined spindle/platform/upright becomes **ARM-202 platform** and **ARM-203 upright**. They can be printed and replaced separately. Captured nuts sit 3 mm into the platform so the hardware clears the base during yaw.
- The asymmetric ARM-102/103 finger arrangement becomes a **straight ARM-204 forearm**, **ARM-205 removable fork**, and purchased synchronized parallel jaws. Opposed contact avoids the old finger's sweeping/wedging geometry. The supplier mechanism also removes two custom SG90 horn clamps.
- **ARM-201** uses the second MG996R at the elbow. Both pitch joints now share the same metal-horn interface and 32 mm standoff length. The 60 mm upper-link centers are retained.
- Your saved C fillets/chamfers remain in the derived platform/upright/upper-link histories and copied unchanged components. Old C fingers remain archived; do not print them for D.

## Native controls and verified limits

Use the six named configurations for home, 22 mm grip, pickup and transfer. `07_Free_motion_CHECK_COLLISIONS` releases the three arm angles with provisional limits; it does not certify every combined pose.

- Physical yaw: −60 to +60°. Native D1@J1_Yaw_command = 90° + yaw.
- Shoulder: −15 to +80°. D1@J2_Shoulder_command = 90° + shoulder.
- Elbow: −100 to −5°. D1@J3_Elbow_command = −elbow.
- Edit the native **Gripper_opening** global variable, provisionally **2–32 mm**. It drives both jaw positions symmetrically; do not edit one paddle independently.

Pickup is now shoulder −15° / elbow −80°. The larger elbow case collided with the upright at the old −30° shoulder position. Ten intended poses and twelve lift/yaw samples were checked with independent component-transform comparisons and native solid interference detection. All were clear after the screw/nut corrections. Full closure at 0 mm produced two small supplier-internal overlaps (~0.092 mm³ each); 2 mm and reopening were clear. This is the reason for the provisional minimum. Continuous swept clearance, external fixtures, loose cables and a real payload are not covered by those checks.

## Material and printing

Use **PETG for the first structural set**. It is a practical technical-print material, with good toughness and relatively low warping; bridges and support removal need care. Follow the actual filament/printer profile rather than universal temperature settings. [Prusa PETG guidance](https://help.prusa3d.com/article/petg_2059)

Starting process proposal: 0.4 mm nozzle, 0.20 mm layers, 5–6 walls, 5 top/bottom layers, 35–50% infill on broad structures, and locally solid bearing seats/bolt regions. Small sleeves, horn cap and crush spacers should print solid. These are trial settings, not a validated strength specification. Check slicer mass and load-direction layer bonding. PLA is useful for quick dimensional mockups; avoid treating a PLA mockup as a sustained-load/thermal qualification. TPU/rubber is optional for gripping surfaces, not structural links. ASA/PC/nylon require a suitable printer and new fit/process validation; a more expensive filament does not automatically improve this arm.

- **Base ARM-001:** foot flat on the bed. Support the elevated bridge as needed; keep support scars out of bearing seats.
- **Platform ARM-202:** broad upper face on the bed, spindle pointing upward. The underside nut recesses then open upward. Inspect the D-flat/cross-hole and remaining walls.
- **Upright ARM-203:** foot on the bed, with supports for the servo-window roof as needed. Inspect the rib/foot junction and keep bearing/servo mounting datums clean.
- **Upper ARM-201 and forearm ARM-204:** broad rear face on the bed, hubs upward. This keeps the long link geometry in the layer plane.
- **Fork ARM-205:** base flat. Clean the two horizontal 4.3 mm holes; confirm a sliding M4 fit without forcing the plastic ears.
- **Cheeks/keepers/cassette:** orient their broad mounting faces for stable support. Remove support before trying bearings. Print sleeves and round standoffs with bores vertical.

Use only `cad/arm-v4/fabrication-trial/manifest.json` and its individual candidate/coupon files once that export is complete. The raw parts folder contains preserved superseded parts and development exports. Never print HW reference parts. Print FIT-001 bearing/dowel trials, FIT-002 horn-pocket trials and one ARM-112 cap first. Check the real seated yaw-horn height: the earlier 13.2 mm value is assumed and its minimum modeled cap/cover gap is only 0.2 mm.

## Assembly, tool to base

1. **Purchased gripper:** assemble the kit using the [supplier's Romi-arm guide](https://www.pololu.com/docs/0J76). Verify both paddles slide freely before installing it. Its servo is included; an SG90 substitution is not assumed compatible.
2. **Fork and crush spacers:** insert the two ARM-206 spacers between the paired plastic mounting ears. Place the gripper between ARM-205's outer cheeks. Fit two M4×35 screws, two washers per screw and M4 nylocs through the matching axes. Tighten by hand only enough to remove play; the spacers resist squeezing the ears inward. Verify smooth jaw travel afterward.
3. **Forearm tool deck:** fasten ARM-205 to ARM-204 with four M3×14, two small-series washers each and M3 nylocs. Assemble this module before attaching it to the elbow so the underside nuts are accessible. Longer screws can reach the elbow case.
4. **Elbow drive:** center the actual MG996R electrically, then fit its matching metal horn and original center screw. Bolt the forearm flange to the horn with four M3×12 and small-series washers. The raised seats clear the dowel sleeve. Confirm thread engagement and that protruding screw tips clear the case through travel.
5. **Elbow passive support:** install the dowel and two ARM-107 sleeves. The dowel starts 3 mm into the forearm-side stack and spans the passive support. Fit the 608 bearing in ARM-104, add its ARM-109 keeper using three M2×14 stacks, and mount the cheek on two 32 mm ARM-108 standoffs with M3×50 stacks. The keeper prevents pin escape while preserving the modeled end float; do not preload/bind the bearing. Elbow servo ears use four M2.5×14 stacks in ARM-201.
6. **Shoulder:** repeat the metal-horn/center-screw arrangement using four M3×12 at ARM-201. Fit the shoulder dowel, two sleeves, 608 bearing, ARM-105 cheek and ARM-109 keeper. Use two 32 mm standoffs/M3×50 stacks and three M2×14 keeper stacks. Mount the shoulder servo to ARM-203 using four M2.5×14 stacks.
7. **Upright to platform:** place the M3 nylocs in ARM-202's underside hex recesses and the small-series washers in the shallow circular seats above them. Bolt ARM-203 down with four M3×14 and top washers. The nut recesses retain orientation and keep all tips above the base backbone. Check the recess fit before final assembly.
8. **Yaw bearing/drive:** fit two 608 bearings in ARM-001. Install the platform spindle and ARM-003 D-drive collar; retain the D interface with the M2×20 crossbolt stack. The spindle/inner-race shoulder must seat without binding. Capture the unmodified SG90 cross horn with ARM-112, four specified low-head M2×10 screws, front washers and nuts; retain the original horn center screw. Fit the SG90 in ARM-004 using two M2×10 stacks, then attach the removable cassette with two M3×30 stacks. Verify cap/gear-cover clearance throughout yaw by hand before power.
9. **Bench and cables:** clamp the 140×120 mm base securely. Route strain-relieved service loops outside every joint sweep; use the existing cable-tie holes. Check screwdriver access and cable clearance in the real assembly. CAD does not model flexible wires.

## Loads, power and proof before repeated use

The solid-PETG/native-volume estimate is **{loads['total_modeled_mass_g']:.1f} g** for modeled hardware/prints, excluding supply/controller. With a 20 g payload at 90 mm, cable allowances and a 1.25 load multiplier, elbow design torque is **{loads['torques']['elbow']['design_Nm']:.3f} N·m**, shoulder **{loads['torques']['shoulder']['design_Nm']:.3f} N·m**. Each uses an assumed **0.277 N·m** operating budget (one-third reference stall torque, further reduced 10%). Margins are **{loads['torques']['elbow']['margin_ratio']:.2f} elbow / {loads['torques']['shoulder']['margin_ratio']:.2f} shoulder**. The gripper's entire specified mass is conservatively allocated at 90 mm because its true mass distribution is unknown. These are sizing assumptions, not measured continuous servo ratings. The shoulder governs; do not increase payload or sustained duty from these numbers alone.

Power servos from the separate regulated supply and appropriately rated distribution, sharing signal ground with the Mega. Keep motor current off the Mega regulator and solderless breadboard rails. Use an accessible DC disconnect and support the arm when power is removed. Verify voltage at the servos during simultaneous starts and choose wiring/protection from measured current and component ratings.

Calibrate one servo at a time with the arm supported, then try slow unloaded motion. The [gripper supplier](https://www.pololu.com/product/3551) specifies an unusually wide nominal pulse range; find actual usable endpoints gradually and stop before hard-stop loading. Feedback indicates position, not grip force. Do not hold a servo stalled to increase grip. Test retention over a catch surface, then increase payload through 5, 10 and 20 g. Record current, voltage, case temperature, drift, slips and fastener movement. If rubber liners are added, retain them mechanically and recalibrate the effective opening.

For the next production-readiness gate, run 50 pick/place cycles with at least 49 successful cycles, record actual placement spread and failures, inspect printed joints/fasteners, and repeat after a sustained-duty trial. Shoulder heating/drift or insufficient repeatability is a reason to reduce load/duty or revise the drive. No cycle, thermal, grip-force or repeatability performance has yet been measured.
'''
(project/'docs/arm-print-and-assembly-guide.md').write_text(guide,encoding='utf-8')
p=json.loads((root/'design-parameters.json').read_text())
p.update(revision='D-development',status='See saved native QA and fabrication manifest; physical fit and performance qualification remain',forearm_link_centres_mm=90,servo_roles=['SG90 yaw (owned)','MG996R shoulder (owned)','MG996R elbow (owned)','FS90-FB included in Pololu3551'],elbow_axial_offset_mm=20.5,elbow_standoff_mm=32,gripper_working_opening_mm=[2,32],shoulder_travel_deg=[-15,80])
(root/'design-parameters.json').write_text(json.dumps(p,indent=2))
print('Updated D BOM, assembly/print guide and design parameters')
