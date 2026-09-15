# Articulated arm D — hardware and budget

Development BOM, 2026-09-12. Native assembly: **198 components, 45 fastener stacks, 23 printed pieces across 15 types**. Purchasing/fabrication remains conditional on actual hardware fit. No purchases were made by the agent. Revision C documents are preserved in `cad/arm-v4/development-debug`.

## Owned hardware to reuse

- **Two MG996R positional servos:** shoulder and elbow. Both are already owned; recorded purchase cost: **$10 total**. Do not buy another pair.
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

- **8 × Nut M2.5 nyloc**
- **13 × Nut M2 hex**
- **14 × Nut M3 nyloc**
- **2 × Nut M4 nyloc**
- **8 × Screw M2.5x14 socket**
- **4 × Screw M2x10 LOW HEAD D4 H1p1**
- **2 × Screw M2x10 socket**
- **6 × Screw M2x14 socket**
- **1 × Screw M2x20 socket**
- **8 × Screw M3x12 socket**
- **8 × Screw M3x14 socket**
- **2 × Screw M3x30 socket**
- **4 × Screw M3x50 socket**
- **2 × Screw M4x35 socket**
- **16 × Washer M2.5 washer 0p5**
- **22 × Washer M2 washer 0p5**
- **36 × Washer M3 washer 0p5**
- **4 × Washer M4 washer 0p5**

M2 low-profile heads must be no larger than Ø4 × 1.1 mm; four are needed for the yaw horn cap. Ordinary socket heads do not fit that clearance. Washers are the modeled **0.5 mm small-series** types: M2 OD5/ID2.2, M2.5 OD5/ID2.7, M3 OD6/ID3.2, M4 OD8/ID4.2. Nyloc envelopes: M2.5 AF5/H3.5, M3 AF5.5/H4, M4 AF7/H5. Match these dimensions before ordering.

The eight M3×14 screws divide between the four recessed-nut upright mounts and four tool-adapter mounts. Eight M3×12 screws fasten the two metal horns. Four M3×50 screws support the shoulder/elbow cheeks. Two M3×30 mount the yaw cassette. Two M4×35 retain the gripper on its fork. Kit-internal gripper hardware and the original servo center screws are separate from these 45 modeled stacks.

## Printed pieces

- 1 × ARM-001_Base_pedestal
- 1 × ARM-003_Yaw_D_drive_collar
- 1 × ARM-004_Removable_yaw_servo_mount
- 1 × ARM-104_Elbow_bearing_cheek
- 1 × ARM-105_Shoulder_bearing_cheek
- 4 × ARM-107_Dowel_to_608_adapter
- 4 × ARM-108_M3_standoff_32mm
- 2 × ARM-109_Bearing_and_dowel_keeper
- 1 × ARM-112_SG90_horn_capture_cap
- 1 × ARM-201_Upper_link_dual_MG996R
- 1 × ARM-202_Yaw_platform
- 1 × ARM-203_Bolted_shoulder_upright
- 1 × ARM-204_Modular_forearm_MG996R
- 1 × ARM-205_Parallel_gripper_fork_adapter
- 2 × ARM-206_Gripper_lug_crush_spacer_13mm

## Budget and buying order

The additions total **$135.90–209.90**, before shipping/tax and contingency. Allowing $20–25 shipping/tax and $20–30 contingency gives **$175.90–264.90 remaining spend** if none of those additions is already available. Including the earlier recorded $20.17 SG90/bearing/dowel order and the $10 MG996R pair gives **$206.07–295.07 estimated all-in cost**. Existing Mega/kit costs are excluded as sunk costs. These are pack/printing allowances, not a checkout quote.

Confirm gripper stock and metal-horn geometry first. Print small horn/bearing/dowel trials next. Then order the final fasteners and one structural set. Reuse workshop power/clamps when suitable to stay near the historical $250 target. The user allows worthwhile functional improvements beyond that target; avoid duplicate motors or a new controller.
