# Articulated arm B — hardware and budget

Development BOM, 2026-09-07. Quantities below describe the current design; verify against the final native assembly report before ordering. Nothing has been purchased by the agent. The historical $250 cell budget is a planning target; Luis explicitly prioritized useful functional improvements over a rigid ceiling.

**2026-09-08 verification:** native component counts match the fastener quantities below (199 total assembly components, including 41 modeled fastener stacks). **Horn attachment hardware remains on hold:** the current nominal MG shoulder pattern does not match the commonly sold 14 mm bolt-circle metal disc, and actual SG90 horn pilots/spacing must be measured. See the fabrication hold in [the assembly guide](arm-print-and-assembly-guide.md). A selected metal shoulder horn may need an additional $5–10 allowance and different attachment screws; the current counts are a development BOM, not an ordering release.

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

- **M2 × 8 socket screws: 10** — four elbow horn, four gripper horn, two yaw horn.
- **M2 × 10 socket screws: 8** — six SG90 mounting-ear screws and two fixed-pad capture screws.
- **M2 × 14 socket screws: 6** — three per passive bearing keeper.
- **M2 × 20 socket screw: 1** — yaw spindle/collar crossbolt.
- **M2 × 25 socket screws: 2** — moving-pad capture through the tall finger.
- **M2 plain hex nuts: 27**, nominal 4 mm across flats × 1.6 mm high.
- **M2 washers: 54**, nominal 2.2 mm ID × 5 mm OD × 0.5 mm thick.
- **M2.5 × 14 socket screws: 4** — shoulder servo ears.
- **M2.5 nylon-insert nuts: 4**, maximum modeled 5 mm across flats × 3.5 mm high; verify the actual supplier dimensions. See [manufacturer dimension reference](https://www.jcfasteners.com/wp-content/uploads/DIN-985-Nylock-Nut-THIN-A2C34-MS-ZN.pdf).
- **M2.5 small-series washers: 8**, 2.7 mm ID × 5 mm OD × 0.5 mm thick. See [manufacturer/supplier dimensions](https://www.vital-parts.co.uk/washers-for-cheese-heads-din-433/31341-w433-m25-a2).
- **M3 × 12 socket screws: 4** — shoulder horn.
- **M3 × 30 socket screws: 2** — removable yaw servo cassette.
- **M3 × 40 socket screws: 2** — elbow support standoffs.
- **M3 × 50 socket screws: 2** — shoulder support standoffs.
- **M3 plain hex nuts: 4** for the shoulder horn; **M3 nylon-insert nuts: 6** for the structural standoffs and cassette.
- **M3 small-series washers: 20**, 3.2 mm ID × 6 mm OD × 0.5 mm thick. Standard larger washers do not fit every modeled location. See [steel washer dimension reference](https://www.ettinger.de/en/product-datasheet/f891308e688fe98aa3fc3e33a869b97d/create).
- **Original servo horn center screws: 4**, matched to each purchased servo; their thread and engagement are not guessed from the reference envelopes.

## Budget position

The additions above total **$114.95–199.95** before shipping/tax and contingency. Add **$20–25** for shipping/tax and **$20–30** contingency. Including the recorded $20.17 hardware order gives **$175.12–275.12 total**. Most lines are planning allowances; the supply is the only fixed live quote used here.

If a separate compatible metal shoulder horn is needed, reserve another **$5–10**, bringing the planning envelope to **$180.12–285.12**. This allowance does not resolve the current CAD horn-pattern mismatch; select the actual horn and revise its interface before ordering the attachment screws.

Aim near $230–250 by consolidating hardware orders and using the makerspace's small quantities of material. Keep useful power and joint-support improvements if their actual quotes push the project slightly over that target. Requote before buying: the final total depends heavily on fastener pack sizes, printing fees and shipping.

The current arm does not require a gantry kit, stepper drivers, or a new PLC. A future PLC is outside this arm estimate, consistent with the earlier project budget. No new electronics board is required solely to generate four servo signals from the existing Mega.
