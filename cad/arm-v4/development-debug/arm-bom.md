# Articulated arm C — hardware and budget

Development BOM, 2026-09-08. Quantities below describe Revision C; verify against the final native assembly report before ordering. Nothing has been purchased by the agent. The historical $250 cell budget is a planning target; Luis explicitly prioritized useful functional improvements over a rigid ceiling.

**Revision C count verification:** the saved native assembly has 190 components, 24 printed instances across 16 part types, and 43 fastener stacks. Component counts match the quantities below. The shoulder targets an OD20 / PCD14 metal horn; three printed caps capture the unmodified SG90 cross horns. Actual seated-horn height, cap clearance and the selected shoulder horn still require fit confirmation; see [the assembly guide](arm-print-and-assembly-guide.md). These are verified CAD quantities, not an unconditional ordering release.

## Reuse the purchased hardware

- **3 SG90 positional servos:** base yaw, elbow, and gripper. Retain the matching stock horns and three original horn center screws. The ordered four-pack plus the existing kit servo provides spares.
- **4 × 608ZZ bearings, 8 × 22 × 7 mm:** two in the yaw tower, one in the shoulder support, one in the elbow support. Reserve a fifth bearing as the demonstration payload.
- **2 × 6.35 × 25.4 mm steel dowels:** passive shoulder and elbow support pins. Printed adapters accommodate the 8 mm bearing bores. The earlier BOM records a 15-pack.
- **1 ELEGOO Mega R3**, its USB cable, and low-current signal jumpers. Servo power requires separate distribution.
- Historical order estimate: SG90 pack $6.99 + bearing pack $5.59 + dowel pack $7.59 = **$20.17 already allocated**. Existing Mega/kit cost is treated as sunk cost, not a new purchase.

## Required additions

- **1 MG996R positional shoulder servo**, with compatible horn and original center screw. Allow **$15–30**, pending the actual supplier quote. Measure the purchased unit before printing its mount. Reference dimensions and torque come from [TowerPro](https://towerpro.com.tw/product/mg996r/); this is not a promise that an unverified clone matches those values.
- **1 regulated external 5 V supply.** Preferred planning option: [Adafruit 5 V 10 A supply, product 658](https://www.adafruit.com/product/658), **$29.95 listed on 2026-09-07**, excluding shipping/tax. Extra current capacity provides room for startup peaks; it does not establish the actual motor current or validate the wiring. An existing regulated bench supply can replace this purchase during commissioning.
- **Power distribution, accessible DC disconnect, correctly rated connector, wire, and fuse holder/fuse:** allow **$15–25**. Match protection to the smallest wire/connector rating and confirm simultaneous current during tests. Keep the servo load off the Mega regulator and solderless breadboard rails. Connect signal ground to the servo supply ground.
- **Machine screws, nuts, washers:** allow **$35–55** for purchasable packs and spares, rather than pricing only individual screws. Quantities and dimensions follow below. The M2.5 shoulder-ear hardware is intentional: larger nut corners can contact the servo case.
- **PETG structural prints and fit coupons:** allow **$10–25** for material/print access, pending the makerspace quote. This is an allowance, not a slicer-derived cost.
- **Two small TPU jaw pads:** allow **$5–15** for a shared-material print. A whole spool, if required, changes this estimate. The pads are captured with screws; adhesive is not the sole retention method.
- **Bench fixture/clamps and catch surface:** allow **$0–10** if workshop clamps or scrap board are available. Base holes are 5.5 mm clearance; fixture bolt length depends on the actual board/bench thickness.
- **Cable ties, sleeve-retention consumables and miscellaneous small parts:** allow **$5–10**. Keep any sleeve adhesive away from the bearing races; fit and retention must be checked first.

## Exact arm fastener quantities

All lengths are under-head lengths. Screw models omit threads and drive sockets. Use matching thread pitches and verify the supplied horn attachment holes. Original servo center screws are separate from these counts.

- **M2 × 10 low-profile screws: 12** — four per SG90 horn cap. Maximum modeled head dimensions: 4 mm diameter × 1.1 mm height. These are distinct from ordinary socket screws; confirm a purchasable matching head and re-quote the pack cost.
- **M2 × 10 socket screws: 8** — six SG90 mounting-ear screws and two fixed-pad capture screws.
- **M2 × 14 socket screws: 6** — three per passive bearing keeper.
- **M2 × 20 socket screw: 1** — yaw spindle/collar crossbolt.
- **M2 × 30 socket screws: 2** — moving-pad capture through the taller C finger.
- **M2 plain hex nuts: 29**, nominal 4 mm across flats × 1.6 mm high.
- **M2 washers: 46**, nominal 2.2 mm ID × 5 mm OD × 0.5 mm thick. Each horn-cap bolt uses one front washer; the other M2 stacks use two.
- **M2.5 × 14 socket screws: 4** — shoulder servo ears.
- **M2.5 nylon-insert nuts: 4**, maximum modeled 5 mm across flats × 3.5 mm high; verify the actual supplier dimensions. See [manufacturer dimension reference](https://www.jcfasteners.com/wp-content/uploads/DIN-985-Nylock-Nut-THIN-A2C34-MS-ZN.pdf).
- **M2.5 small-series washers: 8**, 2.7 mm ID × 5 mm OD × 0.5 mm thick. See [manufacturer/supplier dimensions](https://www.vital-parts.co.uk/washers-for-cheese-heads-din-433/31341-w433-m25-a2).
- **M3 × 12 socket screws: 4** — shoulder horn.
- **M3 × 30 socket screws: 2** — removable yaw servo cassette.
- **M3 × 45 socket screws: 2** — 28.6 mm C elbow support standoffs.
- **M3 × 50 socket screws: 2** — shoulder support standoffs.
- **M3 nylon-insert nuts: 6** for the structural standoffs and cassette. The four shoulder-horn screws thread into the metal horn and use no separate nuts.
- **M3 small-series washers: 16**, 3.2 mm ID × 6 mm OD × 0.5 mm thick. Standard larger washers do not fit every modeled location. See [steel washer dimension reference](https://www.ettinger.de/en/product-datasheet/f891308e688fe98aa3fc3e33a869b97d/create).
- **Original servo horn center screws: 4**, matched to each purchased servo; their thread and engagement are not guessed from the reference envelopes.

## Budget position

The additions above total **$114.95–199.95** before shipping/tax and contingency. Add **$20–25** for shipping/tax and **$20–30** contingency. Including the recorded $20.17 hardware order gives **$175.12–275.12 total**. Most lines are planning allowances; the supply is the only fixed live quote used here.

Reserve **$5–10** for the separate compatible metal shoulder horn, bringing the planning envelope to **$180.12–285.12**. This remains a planning estimate. The C cap design requires twelve low-profile M2 screws; their pack price and availability must fit the hardware allowance or the estimate must be revised. No new supplier quotes were obtained for this revision.

## Purchase sequence

1. Reuse the owned SG90s, bearings, dowels and Mega. Print and fit the bearing/dowel coupon and one horn-cap trial first.
2. Source the positional MG996R and matching OD20 / PCD14 25T metal horn together, confirming the actual dimensions. A regulated 5 V supply and suitable power distribution can be sourced independently of the final printed fits.
3. After the horn trial and native C assembly checks pass, order the final fastener pack quantities above. Check the low-profile M2 heads specifically and include a few spare screws/nuts.
4. Print one set of structural PETG parts and TPU pads, then run unloaded and incremental-load commissioning before ordering duplicate print sets or upgrades.

Aim near $230–250 by consolidating hardware orders and using the makerspace's small quantities of material. Keep useful power and joint-support improvements if their actual quotes push the project slightly over that target. Requote before buying: the final total depends heavily on fastener pack sizes, printing fees and shipping.

The current arm does not require a gantry kit, stepper drivers, or a new PLC. A future PLC is outside this arm estimate, consistent with the earlier project budget. No new electronics board is required solely to generate four servo signals from the existing Mega.
