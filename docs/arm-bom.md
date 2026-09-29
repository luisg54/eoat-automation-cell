# Articulated arm D — hardware and budget

Development BOM, 2026-09-28 (owned-servo update). Native assembly: **191 active components, 44 fastener stacks, 24 printed pieces across 15 types**. 75 superseded nominal-servo components stay in the model, suppressed. This is a development model, not a print release. No purchases were made by the agent. Revision C documents are preserved in `cad/arm-v4/development-debug`.

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

- **9 × Nut M2 hex**
- **8 × Nut M3 hex**
- **22 × Nut M3 nyloc**
- **2 × Nut M4 nyloc**
- **2 × Screw M2x10 socket**
- **6 × Screw M2x14 socket**
- **1 × Screw M2x20 socket**
- **1 × Screw M2x4 PAN HEAD D4 H1p6**
- **8 × Screw M3x12 socket**
- **16 × Screw M3x14 socket**
- **2 × Screw M3x30 socket**
- **4 × Screw M3x50 socket**
- **2 × Screw M3x8 LOW HEAD D5p5 H2**
- **2 × Screw M4x35 socket**
- **14 × Washer M2 washer 0p5**
- **52 × Washer M3 washer 0p5**
- **4 × Washer M4 washer 0p5**

Where they go:

- **16 × M3 × 14** — eight MG996R ear stacks (two washers and a nyloc each), four upright-to-platform, four tool-adapter.
- **8 × M3 × 12** — link to ARM-207 hub on an 18 mm bolt circle (one washer each), into **8 plain M3 hex nuts** captured 0.5 mm deep in the hub pockets.
- **2 × M3 × 8 low head** — hub to MG996R spline, into the spline's M3 thread; 7.0 mm engaged of 8.19 mm available.
- **4 × M3 × 50** — cheek standoffs. **2 × M3 × 30** — yaw cassette.
- **2 × M2 × 10** — SG90 ears, with the nut directly under the shelf and **no washers** (the hole centres are 2.4 mm from the case walls).
- **1 × M2 × 4 pan head** — the SG90's own horn screw through the ARM-003 floor.
- **6 × M2 × 14** — bearing keepers. **1 × M2 × 20** — yaw crossbolt.
- **2 × M4 × 35** — gripper axes.

Washers are the modeled **0.5 mm small-series** types: M2 OD5/ID2.2, M3 OD6/ID3.2, M4 OD8/ID4.2. Nyloc envelopes: M3 AF5.5/H4, M4 AF7/H5. Plain nuts: M2 AF4/H1.6, M3 AF5.5/H2.4. Kit-internal gripper hardware is separate from these 44 modeled stacks.

## Printed pieces

- 1 × ARM-001_Base_pedestal
- 1 × ARM-003_Yaw_D_drive_collar
- 1 × ARM-004_Removable_yaw_servo_mount
- 1 × ARM-104_Elbow_bearing_cheek
- 1 × ARM-105_Shoulder_bearing_cheek
- 4 × ARM-107_Dowel_to_608_adapter
- 4 × ARM-108_M3_standoff_32mm
- 2 × ARM-109_Bearing_and_dowel_keeper
- 1 × ARM-201_Upper_link_dual_MG996R
- 1 × ARM-202_Yaw_platform
- 1 × ARM-203_Bolted_shoulder_upright
- 1 × ARM-204_Modular_forearm_MG996R
- 1 × ARM-205_Parallel_gripper_fork_adapter
- 2 × ARM-206_Gripper_lug_crush_spacer_13mm
- 2 × ARM-207_MG996R_printed_spline_hub

Fit coupons, printed first: FIT-001_Dowel_and_bearing_trial, FIT-003_MG996R_spline_socket_trial, FIT-004_SG90_spline_socket_trial.

**Superseded — do not print or buy for D:** ARM-112 horn cap and its four low-head screws, washers and nuts; FIT-002 horn-pocket coupons; HW-006 metal horns; HW-003/HW-004/HW-005 nominal servo and horn envelopes; M2.5 ear hardware. They remain in `parts`/`hardware-reference` and as suppressed components; curated exports are in `fabrication-trial/superseded-2026-09-28`.

## Budget and buying order

The additions total **$125.90–189.90**, before shipping/tax and contingency. With $20–25 shipping/tax and $20–30 contingency, that is **$165.90–244.90 remaining spend**, if none of those additions is already on hand. Adding the earlier recorded $20.17 SG90/bearing/dowel order and the $10 MG996R pair gives **$196.07–275.07 estimated all-in cost**. Existing Mega/kit costs are excluded as sunk costs. These are pack and printing allowances, not a checkout quote.

Buying order:

1. Print FIT-003, FIT-004 and FIT-001, and test them on the owned servos, a bearing and a dowel.
2. Confirm gripper stock.
3. Order the fasteners.
4. Print one structural set.

Reuse workshop power and clamps where suitable to stay near the historical $250 target. Avoid duplicate motors or a new controller.
