# Articulated arm — print and assembly guide

Revision C development, 2026-09-08. Arm 3 is now assembled in SolidWorks: 190 components, 43 fastener stacks, and 24 printed instances across 16 part types. Nine review poses and twelve transfer-path samples passed native solid-interference checks. These discrete checks do not prove continuous swept clearance. No physical arm has been tested. Hardware quantities and planning costs are in [arm-bom.md](arm-bom.md).

## Fabrication hold: match the actual horns

Print the fit coupons first. The C shoulder interface now targets a 20 mm disc with four M3 tapped holes on a **14 mm bolt circle**, matching this [commercial MG996R-compatible 25T horn drawing](https://robu-prod-media.s3.ap-south-1.amazonaws.com/uploads/2017/06/watermarked_sku-30643.pdf). The upper link includes raised washer seats and uses four M3 screws threaded into the metal horn. Confirm the selected horn's dimensions, spline compatibility and screw engagement before ordering its attachment hardware.

Luis confirmed the small equal-arm cross horn. Arm 3 captures that unmodified horn in a shaped pocket with a removable rear cap; four M2 bolts pass **between** its arms. The stock spline and blade edges transmit torque. The tiny stock pilot holes are not enlarged. The [supplier drawing, pages 4–5](https://www.auselectronicsdirect.com.au/assets/brochures/TA0132.pdf) informs the reference envelope, including the raised gearbox cover and 4 mm overall horn thickness. The assumed seated horn-front height is 13.2 mm above the mounting-ear top; this must be checked on the actual motor. The modeled minimum cap-screw/cover axial gap is only 0.2 mm, so measure it across travel and adjust before use. Imported COTS models can replace these simple references.

Try the three FIT-002 pockets (0.05, 0.10 and 0.15 mm nominal flank clearance per side) with one ARM-112 cap. Choose a snug sliding fit with no forced seating or perceptible rocking. The pocket is 1.65 mm deep for a nominal 1.5 mm blade; a measured thin PET shim can remove axial rattle. Tighten against the printed cap seats, never use bolt force to pull a partly seated horn onto its spline. Keep the original center screw accessible and install the passive dowel afterward.

## Material choice

Use **PETG for working housings, bearing retainers, servo mounts and structural links**, subject to makerspace support. Its toughness and layer adhesion suit mechanical mounts. **PLA is suitable for initial fit coupons and low-duty indoor geometry trials**; it is easier to print but more brittle and less heat tolerant. Both materials can creep under sustained clamp loads: use washers and positive shaft retainers. Material characteristics: [Prusa PETG guide](https://help.prusa3d.com/article/petg_2059) and [PLA guide](https://help.prusa3d.com/article/pla_2062).

Use captured soft rubber or **TPU pads** at the gripper contacts. Pad friction remains a measured input, especially with oily bearings. Do not assume carbon-filled filament or nylon fixes weak geometry: they require controlled printing, drying and fit calibration. Start with an ordinary material supported by the shop and change it only in response to a measured problem.

## Proposed starting print settings

These are engineering starting points, not validated strength data or universal printer profiles.

- 0.4 mm nozzle; 0.20 mm layers; manufacturer-approved filament temperatures and bed preparation.
- Five perimeters, five to six top/bottom layers, and 35–40% infill on structural parts. Inspect sliced thin sections; they may be almost all perimeters.
- Print links flat with their long axes in the bed plane. Keep primary bending loads along continuous extrusion paths, not peeling across layer boundaries.
- Prefer vertical hole axes for bearing and pin seats. Avoid support scars on fits; split a housing and add a bolted keeper if needed.
- Add local solid regions around holes if needed. More infill does not replace edge distance, fillets, washers or a sound load path.
- Weigh the finished parts and update the torque calculation before fitting the payload. CAD solid volume is not the slicer's printed mass.

## Measure and print coupons first

Measure two SG90 bodies, mounting tabs, shaft offsets, stock horns and fasteners. Keep the purchased horn/spline interfaces; a guessed printed spline is unacceptable. The MG996R shoulder is additional hardware, with a reference envelope pending confirmation of the actual purchased unit.

The BOM gives 608ZZ bearings at 22 mm OD × 8 mm ID × 7 mm wide and dowels at 6.35 × 25.4 mm. A bare dowel in that bearing has **0.825 mm radial clearance**. Use an engineered sleeve or a smooth 8 mm shaft at working bearing pivots. Do not run a bearing inner race directly on screw threads.

Print trials for bearing seats at 22.0, 22.1, 22.2 and 22.3 mm and dowel fits at 6.35, 6.45, 6.55 and 6.65 mm. This is an experimental sweep, not a tolerance class. Measure cooled prints and choose the fit from insertion and rotation behavior. Seat the outer race without crushing the housing, and retain it with a removable keeper. During installation, apply force only to the race being seated. A washer must not bridge and clamp both races together.

Print a servo mount and captured-horn trial next. Verify screw access, horn sweep and cable clearance before printing complete links. The SG90 case sits through the mounting window, with its ears on the mounting shelf and two M2 screws retaining it. The revised elbow spacing and taller moving finger provide room for the raised servo cover.

## Hardware and power

The project lists purchased SG90s, 608ZZ bearings and 6.35 × 25.4 mm dowels, plus an ELEGOO Mega R3, breadboard and jumpers. The arm assigns three SG90s to yaw, elbow and grip. The proposed shoulder uses **one MG996R positional servo**, additional hardware. Do not buy a continuous-rotation variant.

The [TowerPro SG90 reference](https://towerpro.com.tw/product/sg90-7/) gives 1.8 kgf·cm stall torque at 4.8 V for its digital variant and recommends external power. That is about 0.177 N·m at stall, not a continuous-duty rating for the user's actual motors. [TowerPro's MG996R reference](https://towerpro.com.tw/product/mg996r/) lists 9.4 kgf·cm at 4.8 V and nominal dimensions 40.7 × 19.7 × 42.9 mm. Both references require checking against the actual units.

The calculation budgets one-third of reference stall torque, applies a 1.25 load multiplier, and reserves 10% at the direct shoulder connection. These are design assumptions, not measured ratings. The earlier 3:1 SG90 shoulder candidate was abandoned because it restricted shoulder travel to about 50 degrees and had little estimated load margin.

Additional hardware will include machine screws/nuts/washers for removable housings, actual horn-compatible screws, positive bearing/shaft retainers, soft pads and a catch tray. Exact screw lengths and quantities must come from the verified assembly stack. Keep each original servo center screw with its horn; verify engagement and avoid bottoming it out.

Use a regulated external servo supply and proper power distribution. Select current capacity from simultaneous-load measurements and actual servo specifications. Do not power the loaded arm through the Mega USB supply, board regulator or breadboard power rails. Connect controller and servo grounds; size the wiring for the intended current and provide an accessible power disconnect.

## Intended assembly and test sequence

1. Inspect and deburr prints. Fit bearings and verify each axis moves freely before adding servos. Install positive axial retainers.
2. Assemble the base; clamp it to the bench for first tests. Check the support polygon and overturning moment before relying on an unclamped base.
3. Center each unloaded servo at a verified electrical position before fitting its stock horn. Keep center-screw access and allow small mounting adjustments.
4. Assemble shoulder, upper link and elbow. Bearings/bushings should carry bending loads; the servo should primarily transmit torque. Check all clamping and retention stacks.
5. Add forearm and gripper. Confirm pad contact, bearing clearance and full release. Servo stall must not be the normal closing stop.
6. Route service loops with strain relief. Cables must never become motion stops.
7. Support the arm and bring up one unloaded axis at a time. Establish actual travel limits before fitting a payload. Software limits stop short of physical and cable limits.
8. Check the full swept volume and pickup/placement poses. This arm has no independent wrist orientation: reachable position alone is insufficient.
9. Increase load in steps, such as 5, 10 and 20 g. Record voltage/current, sag, backlash and temperature over the proposed duty cycle. Investigate binding or sustained buzzing.
10. Run 50-cycle retention and repeatability trials only after low-speed checks pass. Record measured results. On power loss the arm may back-drive or drop the payload; support it during assembly and keep the work above a catch tray.

## Files and memory

Current work lives in `cad/arm-v3`; Arm 2 remains preserved in `cad/arm-v2`. Open `ARM-C_Articulated_prototype_DEVELOPMENT.SLDASM`. Native SLDPRT/SLDASM features are the editing masters; STEP is for exchange and STL for slicing. Its 16 active printed part types have 115 fully constrained sketches, with unchanged-solid checks. Consult the C verification reports for saved-assembly checks. The JSON sizing parameters are a calculation record; they do not drive every dimension in the geometry generator. Preserve a revision before regenerating anything manually edited. After replacing a native part, refresh mates referencing its old faces; a cached position is not proof that the references still resolve.

Build one part at a time, save it, then close its document. Purchased parts use simplified envelopes, without balls, threads or motor internals. Keep only the assembly and the part being edited open. Avoid FEA and render jobs during CAD construction on this 16 GB computer.

## Review the articulation in SolidWorks

Use the ConfigurationManager to select `01_Home`, `02_Grip_open`, `03_Pickup_trial`, `04_Transfer`, `05_Transfer_left` or `06_Transfer_right`. These store independent native mate dimensions. The first six configurations hold a pose; edit their angle mates to move them.

`07_Free_motion_CHECK_COLLISIONS` suppresses the four fixed angle commands and enables native limit mates for dragging. Provisional bounds are yaw -60 to +60, shoulder -30 to +80, elbow -100 to -5 and grip 0 to 25 degrees. The native limits have been read back and their mate features report no errors. These bounds do not guarantee that every combination clears the rest of the arm; use collision detection while exploring and return to a named checked pose for review. They are not the actual servos' calibrated electrical limits.

In the Mates folder, the four command dimensions are `D1@J1_Yaw_command`, `D1@J2_Shoulder_command`, `D1@J3_Elbow_command` and `D1@J4_Grip_command`. Their CAD values in degrees are respectively **90 + yaw**, **90 + shoulder elevation**, **minus elbow relative angle**, and **90 + grip opening**. Home is 90, 135, 45 and 90 degrees. These are CAD angles, not calibrated servo commands. Change dimensions for the current configuration and rebuild; keep backups before editing geometry.

The revised pickup uses yaw 0, shoulder -30, elbow -60 and grip 10 degrees. The earlier shoulder -40/elbow -50 pose hit the yaw platform and is rejected. Transfer uses shoulder 20 and elbow -20; yaw samples cover -60 to +60 degrees. Grip 25 degrees clears the corrected pad relief. Arbitrary combinations, cables, tools, the payload and external fixtures require their own checks.

## Current first-principles estimates

`cad/arm-v3/cad-load-and-bom-report.json` uses native volumes, 100% solid PETG mass, nominal purchased masses and explicit cable/payload allowances. Total modeled mass is about **526 g**, before unmodeled wiring and the payload. This overstates the printed infill mass but does not establish the true servo or bearing mass.

The mass calculation is external to SolidWorks' default material assignments. Use this report for the stated assumptions; do not treat an unassigned native material's mass-property result as the arm's measured mass.

With a 20 g payload, the calculated elbow design torque is **0.0427 N·m** against an assumed **0.0588 N·m** budget; the shoulder is **0.1336 N·m** against **0.2765 N·m**. Margins are approximately **1.38** and **2.07**. These include the 1.25 load multiplier and conservative lever bounds; the budgets are assumptions derived from reference stall torque, not continuous ratings. Retest with weighed parts and actual servos.

For a 22 mm circular object centered at forearm coordinates (69, 1, 3) mm, ideal rigid pad contact occurs near **7.83 degrees grip opening**, inside the usable pad face. With assumed friction coefficient 0.3, a two-times-weight allowance and allowance for the jaw angle, the estimate is **0.85 N normal force per contact** and **0.0168 N·m grip torque**. Pad compression, friction, contact width and retention remain physical tests. The 10-degree CAD transfer pose is a clearance demonstration, not a validated holding command.

## Part orientation and fabrication files

Use the curated `cad/arm-v3/fabrication-trial` files and manifest: 16 arm part types and four coupon types have been exported and checked for watertightness, positive volume and agreement with native volume. `fit-coupon` is the first print; add one ARM-112 cap from `candidate-parts` for the horn trial. The full candidate set remains subject to the horn and hardware-fit hold above. Individual exports use millimetres and fine STL resolution. Do not batch-print the raw `parts` directory, which preserves superseded candidates alongside the native masters.

- **ARM-001 base:** bench face on the bed; support the elevated bearing bridge. Keep support contact out of the finished bearing seats where possible.
- **ARM-002 yaw upright:** its spindle, platform and upright prevent a simple support-free orientation. Review a side-on orientation with the makerspace and use removable supports beneath the platform/shaft. Verify the spindle and bearing-fit surfaces after support removal; this is a candidate that may benefit from splitting into bolted parts after the first fit trial.
- **ARM-003 collar and ARM-004 cassette:** place a broad flat face down. Keep the collar axis vertical if possible; use local support only where the cassette geometry requires it.
- **ARM-101 upper:** broad rear web face on the bed, bearing axis vertical.
- **ARM-102 forearm:** keep its web parallel to the bed. The horn-pocket boss extends 1.65 mm behind the web, so this is not a single flat-bottom print. Plan removable support beneath the raised web and gripper mount, with the horn pocket kept clear of support scars. Review this orientation in the slicer before committing the full link.
- **ARM-103 moving finger:** horn attachment plate on the bed, with the hanging finger extending upward. This avoids bridging the full horn plate above a narrow fingertip.
- **ARM-104/105 bearing cheeks:** place the inner lip face down, open bearing pocket upward. Confirm the slicer preserves the retaining lip.
- **ARM-106/108 standoffs and ARM-107 sleeves:** axes vertical; use enough perimeters to make the thin sleeve wall continuous. Print extra sleeves for fit selection.
- **ARM-109 keepers:** cup end on the bed, open cavity upward, with supports under the outward flange if required. Inspect and deburr the internal pin clearance.
- **ARM-110 fixed TPU sock:** the pocket runs along the finger; orient its open passage vertically where adhesion permits, with a brim. Avoid trapped support in the sleeve.
- **ARM-111 moving TPU sock:** closed bottom on the bed, open pocket upward.
- **ARM-112 horn caps:** plain flat face on the bed, head counterbores upward; keep the thin remaining floor clean. Three caps are required. Low-profile screw heads must match the modeled maximum 4 mm diameter × 1.1 mm height.
- **FIT-002 horn trials:** broad load-plate face down, shaped pocket upward. Print one cap alongside the three trial clearances.
- **FIT-001 coupon:** broad face on the bed, hole axes vertical. Bearing holes increase left to right from 22.0 to 22.3 mm; dowel holes increase from 6.35 to 6.65 mm. Mark the underside before removing it from the bed so orientation is unambiguous.

## Part-by-part walkthrough: gripper down to the bench

**Moving pad — ARM-111.** This is the soft TPU contact sleeve at the moving fingertip. Slide it over the bottom of ARM-103. Two M2 × 30 screws pass through the taller C finger and pad; use a washer at each end and an M2 nut. Tighten only enough to retain the sleeve. Excess preload crushes the TPU and can split printed walls.

**Moving finger — ARM-103.** Capture the gripper's stock cross horn between its shaped pocket and one ARM-112 cap. Use four M2 × 10 low-profile screws, four front washers and four front nuts. Heads face the servo and sit in the cap recesses; omit rear washers. The central opening gives access to the original horn center screw. Closing rotates this finger; the jaws do not remain parallel. Calibrate closing at actual object contact and do not use continuous servo stall to hold the bearing.

**Fixed pad — ARM-110.** This TPU sleeve wraps the fixed finger built into the forearm. Slide it along the bar to align the two holes. Two M2 × 10 screws, four washers and two nuts capture it. It can be replaced independently when worn.

**Forearm and fixed jaw — ARM-102.** This PETG part carries the fixed contact, gripper servo and elbow horn connection. Mount the gripper SG90 through the body window with two M2 × 10 ordinary socket screws, four washers and two nuts. At the elbow end, capture its stock horn using one ARM-112 cap, four M2 × 10 low-profile screws, four front washers and four nuts. Secure the original horn center screw before inserting the passive support pin.

**Elbow support pin and sleeves — HW-002 and ARM-107.** One 6.35 × 25.4 mm dowel spans the forearm hub and passive-side bearing. Two printed sleeves adapt the pin to the 8 mm nominal seats, one in the link and one in the bearing. Check fits first; there must be no perceptible radial slop, binding or sleeve migration. The pin is a support axle, not a substitute for the servo horn's torque connection. Its inner end is offset to preserve center-screw clearance; its outer end is enclosed by the keeper.

**Elbow bearing cheek — ARM-104.** This stationary support relative to the upper link carries one 608ZZ bearing. Insert the bearing from the open outer side until it meets the inner retaining lip. Two C ARM-106 standoffs, each 28.6 mm long, connect the cheek to the upper link using two M3 × 45 screws, four small-series M3 washers and two M3 nylon-insert nuts. These screws clamp the printed standoffs, not the rotating link. Do not use the preserved 24 mm B standoffs with this revision.

**Elbow keeper — ARM-109.** Three M2 × 14 screws, six washers and three nuts attach this cap to ARM-104. Its thin outer contact rim seats against the housing while leaving nominal axial clearance at the bearing face. The central cup encloses the pin end. Check that the pin and inner race rotate freely after tightening; neither should rub the cap.

**Upper link — ARM-101.** This PETG link places the elbow axis 60 mm from the shoulder. It holds the elbow SG90 with two M2 × 10 screws, four washers and two nuts. Four M3 × 12 screws with four small-series washers connect its shoulder flange to the metal horn's tapped holes; no separate horn nuts are used. Raised washer seats clear the central sleeve. Confirm screw engagement and case clearance on the actual horn. Install the original shoulder center screw while access remains open, then fit the support pin.

**Shoulder passive support — ARM-105, ARM-108, ARM-107, HW-002 and ARM-109.** This repeats the elbow's bearing-supported arrangement at the stronger joint. Use one 608ZZ, one dowel, two adapter sleeves and two 32 mm ARM-108 standoffs. Two M3 × 50 screws, four small-series M3 washers and two M3 nylon-insert nuts clamp the standoffs between the rotating base's upright and the cheek. Three M2 × 14 screws, six washers and three nuts secure the outer keeper. The cheek stays with the yaw upright while the upper link rotates.

**Shoulder servo — MG996R reference.** Its case fits through the upright window in ARM-002. Four M2.5 × 14 screws, eight small-series M2.5 washers and four M2.5 nylon-insert nuts secure its ears. These smaller fasteners leave clearance beside the servo case; do not substitute larger nuts simply because they fit through the printed hole. The horn transmits torque, while the opposite dowel/bearing support reduces cantilever loading on the servo output.

**Yaw platform and upright — ARM-002.** This part rotates the shoulder and the whole arm about the vertical base axis. Its hollow spindle runs through the two base bearings. The spindle's D-shaped end engages ARM-003. Preserve the spindle shoulders, flat and crosshole when editing: they define the support and retention stack.

**Yaw drive collar — ARM-003.** One ARM-112 cap and four M2 × 10 low-profile screws capture the stock yaw cross horn; use four front washers and nuts. Assemble this connection and its original center screw before inserting the cassette. A single M2 × 20 crossbolt, two washers and one nut positively retain the collar and spindle. The recessed flat seats support the crossbolt hardware; the D-shaped interface carries driving torque.

**Removable yaw-servo cassette — ARM-004.** Mount its SG90 with two M2 × 10 screws, four washers and two nuts. Center the servo and fit its stock horn/center screw before closing access. The cassette attaches to the pedestal backbone using two M3 × 30 screws, four small-series M3 washers and two M3 nylon-insert nuts. The side pockets allow nut access. The intended insertion is from the open side below the bearing bridge, then upward into the final position; verify this path with the actual horn and leads before loading the arm.

**Base pedestal — ARM-001.** Two 608ZZ bearings support the yaw spindle above the servo. The spacer shoulder separates them. Fit the bearings, spindle and collar as one retained module; support loose bearings during assembly. The base includes tool access to the crossbolt and four 5.5 mm fixture holes. Clamp or bolt it to a rigid bench board. Choose fixture screw lengths from the actual board thickness rather than the CAD base alone.

## Practical build order

Read the walkthrough from gripper to base to understand the load path, but physically build the base first. Then prepare the three link/horn subassemblies on the bench, fit the shoulder and elbow supports, and add the pads and service loops. Keep each original servo center screw accessible until its horn has been centered and verified. Check free motion after every support or keeper is tightened.

The arm has yaw, shoulder, elbow and grip actuation. It has **no independently controlled wrist orientation**. A pickup fixture and trajectory must accommodate the gripper's changing orientation. The old vertical locating-pin pickup is not automatically compatible with this new articulated architecture.
