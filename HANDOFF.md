# EOAT Automation Cell — Handoff

## Active revision D — owned-servo update, 2026-09-28

**Model:** `cad/arm-v4/ARM-D_Modular_parallel_gripper_DEVELOPMENT.SLDASM`. Development only, not a print release.

- 191 active components, 44 fastener stacks, 24 printed pieces across 15 types.
- The 75 nominal-servo components (HW-003/004/005/006, ARM-112 and their fasteners) are suppressed in all 8 configurations. Their 77 mates are suppressed and renamed `*_superseded_nominal_servo`. Nothing was deleted.
- Pre-edit backup: `cad/arm-v4/development-debug/before-owned-servo-geometry-20260928-180253/` (assembly, changed parts, reports, docs, SHA-256 manifest).
- Revision C and `cad/arm-v3` are untouched; all 38 hashes re-checked.

**Measured on the two servo files.** Native B-rep via `measure_owned_servos.py`, written to `owned-servo-measurements.json`. Datum: ear underside on the output axis.

- **`MG996R_servo.SLDPRT`** — native part, 2 bodies (case; spline with modeled M3 thread). No material, **no horn, no cable**.
  - Ears: Ø4.0 open-slot holes at −14.15 / +34.15 × ±5.00 mm (a 48.30 × 10.00 pattern), 19 mm wide. Thickness 2.40 mm at the output end but 1.754 mm at the far end (asymmetric in the file).
  - Case: 40.0 mm at the ears, 40.7 at the bottom (1° draft), × 20.0; 27.99 below the ears.
  - Heights above the ear underside: case 7.5, cover 10.0, raised block 11.0, Ø13.2 boss 11.5, Ø10.8 output ring 12.0, spline top 15.5.
  - Spline: 25 V-teeth, tip Ø5.997, root ≈Ø5.42, 3.5 mm exposed. M3 centre thread 8.19 mm deep.
- **`SERVO_SG90.SLDPRT`** — STEP import, 5 bodies (case, spline, 3 cable stubs). No material, **no horn, no tooth form, no thread**.
  - Ears: 2.4 mm thick, Ø2.5 open-slot holes at −8.4 / +19.4 mm (27.8 pitch). Hole centres are only 2.4 mm from the case walls.
  - Case: 12.0 × 23.0.
  - Gear cover (Ø12 plus a Ø5 lobe at +6.0): top 11.4 above the ear underside, 9.0 above the ear top (D assumed 8.8).
  - Spline: plain Ø5.0 with 40 shallow grooves, 3.0 mm exposed, top 14.4 above the ear underside. The old 13.2 mm horn-front assumption no longer applies.
  - Centre hole: plain Ø1.0. Cables exit the output end 12.7 mm below the ears.

**Functional changes, and why:**

1. **MG996R mounts (ARM-203, ARM-201).**
   - The window is now 41.7 × 21.0 mm: the file's widest case section plus 0.5 mm per side. The old window left 0.15 mm.
   - Ø3.4 holes sit on the measured pattern; the old holes were 1.15 mm off.
   - M3 × 14 with two washers and a nyloc replaces M2.5, because the Ø4 slotted ears need M3. M2.5 hardware is gone from the BOM.
2. **ARM-207 printed spline hub (×2, new)** replaces the unowned OD20/PCD14 metal-horn stack.
   - Ø5.80 press socket over 3.0 mm of the 25-tooth spline; underside 0.5 mm above the output ring.
   - 1.0 mm floor seated on the spline top, clamped by an M3 × 8 low-head centre screw with 7.0 mm engaged.
   - Four M3 × 12 on an 18 mm bolt circle into captured M3 nuts.
   - The hub is sized so the link rear faces stay 16.5 mm above the ears, so world Z is unchanged. Dowels, sleeves, cheeks, 32 mm standoffs and M3 × 50 stacks are all unchanged.
   - The centre-screw head sits inside the link-side sleeve, 1.0 mm below the dowel.
   - A separate hub keeps each link's print face flat and makes a stripped socket a small reprint.
3. **ARM-201 / ARM-204:** the PCD14 metal-horn holes are suppressed; PCD18 holes and washer seats are added.
4. **ARM-004:** SG90 ear holes move to −8.4 / +19.4 mm; each was 0.6 mm off. M2 × 10 with no washers, because a Ø5 washer would overlap the case wall by 0.1 mm. Nut flats face the case.
5. **ARM-003:**
   - The horn pocket is suppressed and replaced by a Ø12 boss with a Ø4.85 × 2.5 mm press socket, 0.5 mm above the gear cover.
   - A 1.2 mm floor seats on the spline top, with the SG90 horn screw; its head clears the spindle end by 0.4 mm.
   - The crossbolt hole is opened to Ø2.8 (±0.4 mm axial float). The servo now locates the collar and the platform weight stays on the 608s. The old round hole over-constrained the yaw stack.
6. **ARM-112 cap, its four low-profile M2 × 10 (Ø4 × 1.1) screws, washers, nuts, and FIT-002 are superseded.** There is no horn left to capture, and it removes a hard-to-source screw.
7. **`03_Pickup_trial` moved from −15/−80 to −15/−75.** The forearm is now vertical, so the jaws are coaxial with the pin. The jaw tips sit 16.5 mm above the bench at z ≈ 75.
8. **Pin-safe lift defined:** a Cartesian vertical lift for the first 10 mm (IK at the 90 mm grip point), during which the forearm rotates 1.14°. This replaces the joint-interpolated lift check.
9. **FIT-003 (Ø5.70–6.00) and FIT-004 (Ø4.65–4.95) coupons** will select the real press-fit bores.
10. **The three spare SG90s stay unused.** A wrist-pitch SG90 (about 17 g at about 150 mm) would take the governing shoulder margin from 1.14 to about 1.0, and the vertical lift doesn't need a wrist. Keep them as yaw spares and fit-test units.

**Verified in SolidWorks on the reopened assembly:**

- All 191 active references resolve inside `arm-v4` (38 unique parts).
- Zero mate errors and zero part feature errors (the servo files are allowed to be multibody).
- The 6 saved pose configurations match the kinematic model to ≤1.1×10⁻¹⁵, and the free-motion limits are valid.
- Interference in the 6 saved configurations, 11 review poses and 19 transfer/lift samples: **0 unexpected overlaps**.
  - Every state shows the same 93 designed engagements, reported separately: hub and collar press fits on the modeled splines, and centre screws in the modeled M3 thread and the SG90's Ø1.0 hole.
  - 0 mm closure keeps its 2 known supplier-model overlaps.
- All new sketches are fully defined and the unchanged-solid checks pass.
- Loads (solid density, 20 g payload): shoulder 0.243 N·m, margin 1.14, still governing; elbow 0.077 N·m, margin 3.58; total 639.3 g.
- Curated exports are refreshed for the 8 changed or new parts. The ARM-112 and FIT-002 exports moved to `fabrication-trial/superseded-2026-09-28`.
- Everything is saved and all CAD documents are closed; SolidWorks is left running with no documents.
- Resources: the SolidWorks session I started from already held about 3 GB of private memory. Its working set jumped to 3.47 GB after two small part builds, so I stopped, confirmed nothing was open or unsaved, and restarted it. After that, restarts between heavy runs kept the working set under 2 GB (peak 1.92 GB), well below the earlier 6.6 GB failure.
- `cad/sw_probe.py` now uses the installed pywin32 with late binding, because the `%TEMP%` bridge is gone.

**Still unproven on hardware:**

- The owned servos have not been calipered. The files were trusted as instructed, including the thin 1.754 mm far ear.
- Spline press fits and hub/collar torque and creep: run FIT-003 and FIT-004 first.
- Whether the original MG996R centre screw fits, or the M3 × 8 low head is needed. Whether the SG90 horn screw bites (the file shows only a Ø1.0 hole).
- The 0.5 mm running gaps under the hubs and collar at printed tolerance.
- Bearing and dowel fits (FIT-001) and crossbolt alignment.
- Cable routing across yaw and screwdriver access.
- Shoulder torque, current and temperature; the 1.14 margin is an estimate.
- Grip retention, repeatability, the 50-cycle test, and the pickup fixture itself.

## Previous D checkpoint - 2026-09-12 (superseded by the owned-servo update above)

**Latest saved model: `cad/arm-v4/ARM-D_Modular_parallel_gripper_DEVELOPMENT.SLDASM`.** 198 components, 45 fastener stacks. Verification in progress; no print or production release. Latest motion report: home: 5 overlaps.

User asked to improve functional geometry beyond fillets, including ARM-002/102/103. He owns TWO MG996Rs and permits sensible COTS. His saved C edits were inspected and preserved (38 unique parts, no feature errors; hashes in `user-revision-inspection.json`). Do not regenerate C. D derives ARM-201/202/203 from his native histories and copies unchanged parts from saved C.

New parts: ARM-201 upper link for both MG996Rs, ARM-202 separate yaw platform, ARM-203 bolt-on upright, ARM-204 straight modular forearm, ARM-205 removable parallel-gripper fork, ARM-206 crush spacers (two). Both pitch joints use 20.5 mm horn spacing, 32 mm standoffs, OD20/PCD14 metal horns. One SG90 remains for yaw. Tool candidate is Pololu 3551, 32 mm stroke, supplier 30 g including FS90-FB servo, $29.95; supplier showed backorders. Official STEP/PDF saved and drawing visually inspected. HW-202/HW-203 are supplier body/jaws. No purchase occurred. Fork uses the actual two 4.2 mm axes, M4x35, 0.5 mm small-series washers, nylocs and 13 mm crush spacers inside 13.4 mm ear gaps. Four M3x16 attach the adapter; four M3x20 attach the upright.

Resource fix: visible part windows grew SW to ~6.6 GB and a fastener OpenDoc returned null. Saved 158-component partial insertion under `development-debug/D_partial_insertion.SLDASM`; resumed without rebuilding with `--resume-partial`, DocumentVisible(False,1), CommandInProgress=True. Complete model saved; SW was ~0.86 GB. Keep component windows hidden during assembly insertion; do not run concurrent COM scripts. Initial jaw alignment QA caught flipped imported planes; corrected with closest alignment and a flipped right-side opening distance. Superseded mates are suppressed, not deleted. Full builder now includes these settings and a pre-mate save checkpoint.

Next: finish transform/collision checks including reduced shoulder clearance with larger elbow case, calculate D loads/BOM, constrain new sketches, verify saved configurations/references, update guide/BOM and curated exports. Current documents below still describe C until explicitly revised. Physical horn fit, bearing/dowel trials, cables/driver access, grip force/current and repeatability/cycle evidence remain required. User latest instruction: continue and verify carefully; usage reset, laptop 16 GB. No new subagents authorized.

## Active CAD session — 2026-09-08

**Latest checkpoint: Arm 3 / Revision C is built and verified in CAD.** Open `cad/arm-v3/ARM-C_Articulated_prototype_DEVELOPMENT.SLDASM`. It has 190 components, 185 rigid attachments, four articulated joints, 43 fastener stacks, and 24 printed instances across 16 active part types. Those printed types contain 115 fully constrained sketches with unchanged-solid checks. `saved-assembly-verification.json` confirms clean reopen, all 190 native references, six saved pose transforms, zero active mate errors and native free-motion limits. Nine review poses and twelve lift/yaw samples have zero native solid overlaps. These are discrete samples; no full swept-clearance or physical performance claim is made.

C corrects the SG90 raised gearbox-cover envelope and compact horn hub projection, lowers the removable yaw-servo shelf, increases elbow axial spacing to 19.6 mm and its printed standoffs to 28.6 mm, and lengthens the moving finger while retaining pad contact height. Each compact stock horn is captured in a shaped pocket with an ARM-112 cap and four M2 × 10 low-profile screws (head maximum D4 × H1.1). The C shoulder uses an OD20 / PCD14 M3-tapped metal-horn reference and raised washer seats. No tiny stock horn pilots need drilling. C native views in `review-images` were visually inspected.

**Physical fit hold:** the 13.2 mm seated SG90 horn-front height above its ear top is an assumption; Luis has been asked for this measurement. The minimum modeled screw/gear-cover axial gap is 0.2 mm, so the real cap must clear through travel before release. Three FIT-002 pocket clearances and a cap are the next small print trial, alongside FIT-001 bearing/dowel checks. Confirm actual MG996R/horn dimensions, assembly insertion, driver access and cable paths. Final fastener ordering depends on these checks and a quote for the twelve low-profile M2 screws. User prefers simple COTS envelopes and can import purchased models; avoid detailing internals.

C load estimate: 526.0 g modeled mass at solid-density assumptions; with 20 g payload, elbow design torque 0.04273 N m versus assumed 0.05884 budget (margin 1.38), shoulder 0.13363 versus 0.27655 (margin 2.07). These are sizing estimates, not measured ratings. `docs/arm-bom.md` now matches C native quantities; `docs/arm-print-and-assembly-guide.md` follows the revised physical stack and staged purchase/print/test plan. Budget remains an allowance of about $180–285, pending current quotes. No purchases occurred. Curated C fabrication exports are complete: `fabrication-trial/manifest.json` lists 20 individual part/coupon types with zero mesh failures and native-volume checks. Print the four coupon types and one ARM-112 cap first. All saved task CAD documents were closed after exports to release memory; SolidWorks itself remains open. Preserve B as the prior checkpoint and the C development backups. Goal remains incomplete pending fabrication/access checks and physical fit/test evidence.

### Preserved Arm 2 checkpoint and prior-session context

Luis explicitly switched the CAD task to an **articulated robot arm** and authorized identifying additional hardware. See `docs/articulated-arm-requirements.md`; the older X-slide architecture below is historical context.

Current native SolidWorks 2026 work is in `cad/arm-v2`; revision A and the original demonstration are preserved. B has 199 components, 21 printed instances across 15 part types, 41 explicit fastener stacks, a removable yaw servo cassette, bearing retainers, positive yaw crossbolt and captured TPU pads. Shoulder ears use M2.5 hardware. The moving-pad servo-ear relief is now built. The fit coupon is built in B. `sketch-constraint-report.json` records 98 fully constrained sketches across 16 files (15 arm types plus coupon), with unchanged-solid checks.

**Native motion now works with dimension-driven mates.** Rebuilding the 194 rigid attachments finished. `refresh_joint_references.py` replaced stale joint references after part regeneration, fixing shoulder pivot translation. Direct `SetTransformAndSolve2` still failed to propagate the full rigid groups reliably; use the four native angle command dimensions instead. `check_motion.py` now does that and independently compares all 199 component transforms against kinematics. Nine revised poses passed with zero solid overlaps (`motion-inspection.json`). The previous -40/-50 shoulder/elbow pickup hit the yaw platform; revised pickup is -30/-60. Twelve samples of lift/yaw transfer also passed (`transfer-path-inspection.json`). These are discrete samples, not a swept proof; cables, tool access, payload and external fixtures are excluded.

Six native pose configurations are saved and their independent dimensions were read back (`pose-configurations.json`). `07_Free_motion_CHECK_COLLISIONS` suppresses command mates and uses four native angle-limit mates; values and zero feature errors verified in `native-motion-limits.json`. Provisional physical-angle bounds: yaw -60..60, shoulder -30..80, elbow -100..-5, grip 0..25. Arbitrary combinations are not certified collision-free. Native config switches invalidate cached component COM objects; re-fetch GetComponents after switching. `SaveConfiguration2` is not used: ShowConfiguration2 can return false when already active, so inspect ActiveConfiguration.Name.

**Fabrication hold at horn interfaces.** The modeled MG horn is a nominal 26 mm plate / 20 mm bolt circle. A sourced common 25T metal disc is 20 mm OD / 14 mm bolt circle / 4.5 mm total thickness / 2 mm plate, four M3 tapped holes (drawing linked in guide). It cannot be substituted directly. Select a real horn, update the upper-link pattern, washer relief, screw engagement and axial stack, then refresh affected mates and recheck. Existing MG model plate front is world Z23; the source metal disc with hub beginning Z16 would put its front at20.5, requiring a stack change. SG90 modeled hole radii8 and M2 through fasteners also require matching to owned horns; supplier drawing shows r8.3 and ~1 mm pilots. Do not release the horn-connected parts or order their fasteners yet. User was asked asynchronously whether calipers/PETG/TPU are available; no reply yet.

The current shoulder proposal is one additional MG996R positional servo; three purchased SG90s handle yaw, elbow and grip. The 3:1 SG90 shoulder candidate was rejected because of restricted travel and small load margin. Upper centers are60 mm; nominal forearm contact65 mm, with a better-centered circular payload location at forearm(69,1,3) mm. `calculate_cad_loads.py` now uses native volumes, conservative printed density and motion-group lever bounds, including jaw rotation. With20 g payload: design elbow0.04088 N m versus0.05884 budget (margin1.44); shoulder0.12858 versus0.27655 (margin2.15). Total modeled mass518.4 g at solid-density assumptions, not a weighed result. Ideal22 mm bearing contact occurs at grip7.83deg; assuming mu0.3 and weight factor2, estimated0.849 N/contact and0.01683 N m grip torque. The 10deg CAD transfer pose is a clearance demonstration, not a holding command. All physical fits, actual servo ratings, pad friction and duty-cycle tests remain pending.

**Earlier C preparation (superseded by the latest checkpoint above):** revised horn-interface parts and FIT-002 coupons were initially generated without a complete assembly. The resumed session subsequently built and verified that C assembly. Arm 2 is preserved for comparison.

`docs/arm-print-and-assembly-guide.md` includes the full gripper-to-bench walkthrough, materials, per-part orientation, configuration controls, calculations and horn fabrication hold. `docs/arm-bom.md` has native-verified development quantities and planning allowances. User explicitly allows useful function improvements beyond the historical$250 target. A compatible shoulder horn adds an estimated$5–10 to the earlier$175.12–275.12 total; no purchase occurred. Only the supply has a checked fixed quote. Native colors and component references are saved; `review-images` contains actual SolidWorks BMP views, visually inspected. SW working set stayed around1.3–1.4 GB. Curated fine/mm exports are being generated by `export_fabrication_trials.py` into `fabrication-trial/fit-coupon` and `candidate-parts`, with mesh/native-volume checks and a manifest. Raw `parts` still preserves mixed assembly STLs; use only curated files for trial fabrication. Remaining: finish export and saved/reopened QA; resolve actual horn interfaces, insertion/tool/cable access and continuous travel; physically fit/test. Goal is not complete and no full print-ready release has occurred.

SolidWorks initially failed to finish startup; Luis opened it manually and authorized control. The COM connection now works (revision 34.3.2). Temporary failed sketches were preserved under `cad/arm-v1/development-debug` before closing them. Scripts use the bundled Python 3.12 plus a temporary pywin32 bridge and require the desktop COM session.

---

**Historical handoff last updated:** 2026-09-03
**Status:** Phase 1 parts **ordered** (608ZZ 20-pack + 1/4" × 1" dowels + SG90 4-pack, ~$20). ETA ~Sat 2026-09-05. Nothing built yet. WashU makerspace / 3D print access **confirmed**. Cardboard mock starts after delivery.
**School start:** 2026-08-24. Pre-school window is 2026-08-12 → 2026-08-23.

## Current state

Repo scaffolded in June 2026 with the `cad` / `firmware` / `plc` / `electrical` / `docs`
layout. No CAD models committed, no firmware, no ladder logic, no wiring diagrams.

A bill of materials exists in `electrical/bom.md` with real part selections. Three items are
already owned: an ELEGOO Mega R3, an SG90 servo for gripper actuation, and a breadboard and
jumper set. Phase 1 order placed 2026-09-03 (ETA ~Sat 9/5): 608ZZ 20-pack, 1/4" × 1" dowels,
SG90 4-pack. Gantry / Micro820 / drivers still not ordered — correctly deferred.

Scope, phases, and success criteria are in `README.md`. Testable requirements are in
`docs/requirements.md`. Pick object is locked: **608ZZ bearing**, located by an ID pin +
rest at pickup and a different datum scheme at destination (F-08–F-10). Motion is locked:
**one powered gantry X + EOAT Z servo ≥ 15 mm (F-11)**. Payload P-04 is ≥ 20 g. Remaining
TBDs wait on gantry selection and the SG90 mock.

## Scope tension — resolved for Phase 1–2 (2026-08-13)

**Option A locked:** one powered gantry axis (X) + a short Z servo on the EOAT (≥ 15 mm) to
clear the vertical ID pin. Z is not a gantry axis and does not justify buying/wiring three
TB6600s.

A 3-axis V-slot kit is still allowed if it is cheaper as a kit. Unused axes stay
mechanically present and **unpowered** through Phase 2. Do not treat kit-Z as the lift.

## Blockers

| Blocker | Impact | What would unblock it |
|---|---|---|
| ~~Machine shop / 3D printing access~~ | **Cleared 2026-09-03** — WashU makerspace + 3D print access confirmed | Fabricate after cardboard mock passes |
| Micro820 not ordered | Phase 3 cannot start | Check whether a lab unit can be borrowed before buying; confirm Connected Components Workbench access |
| Budget not set | Cannot order long-lead items | **Partial lock:** $250 cell; PLC separate. Raise cell budget if the linear kit is >~$150 |
| Axis count not decided | ~~Blocks the BOM order~~ | **Resolved:** one powered X + EOAT Z servo. Kit extras stay unpowered |
| Performance targets still TBD (P-01, P-03, P-06) | Requirements not fully testable | Set after SG90 mock + gantry choice. P-04 is locked at ≥ 20 g |

## Open questions

- Is the gripper SG90 adequate to retain a 608ZZ through transfer (P-05), including during
  the Z lift? Cheap to test 8/15–8/17. Order bearings + dowels + second SG90 first.
- Is a physical Micro820 worth buying, or is a simulated PLC acceptable for demonstrating
  state-machine and handshake logic? Physical hardware is a much stronger interview story.

## Next steps


### Session — 2026-09-03

- Phase 1 Amazon order placed (Luis, afternoon 2026-09-03). Cart: 608ZZ (20), 1/4" × 1" dowels (15), SG90 4-pack. ~$20. ETA ~Sat 2026-09-05.
- Luis has WashU makerspace / 3D print access (blocker cleared).
- Owned unchanged: ELEGOO Mega R3, one kit SG90 (gripper), breadboard/jumpers.
- **Next after delivery:** cardboard/foam mock (jaws + Z lift off pin, hand-slide X). Pass/fail retention + pin clearance. Household tape/glue. Mega USB power. Do not buy more until mock results.

### Active — from 2026-08-31

SpaceX call is done. Still in process until they email (~1 week from 8/28). **Do not wait on
that to start building.**

This week, split time:

1. **EOAT Phase 1** (primary build): **order placed**, waiting on ~Sat 9/5 delivery → cardboard
   mock (jaws + Z lift off pin, hand-slide X). Pass/fail on retention and pin clearance.
   Shop/print access already confirmed.
2. **Interview repair** (20 min/day, parallel): cantilever / shear / bolts-vs-pins drill per
   `Career/Interview-Prep/Mock-Sessions/2026-08-28-spacex-phone-debrief.md` — round 2 or
   the next company will ask the same chain.

Do **not** yet: gantry kit, Micro820, firmware, full-cell CAD.

### Was paused — through Fri 2026-08-28

### Stopped — 2026-08-13 ~01:08 (sleep)

Session done. Concept is locked and the 3D cycle is in `docs/cycle-animation.html`.

**When you wake up:** order 608ZZs + two 1/4" × 1" dowels + extra SG90 (~$15–30). Internship wrap still owns Thu–Fri — no build until Sat 8/15. Then cardboard mock: jaws + Z lift off the pin.

### Done — 2026-08-12 / early 2026-08-13

Pick object locked: **608ZZ**. Locating rules in `docs/requirements.md` (F-08–F-10). P-04 ≥ 20 g.

**Order soon:** 5–10× 608ZZ + two 1/4" × 1" steel dowel pins + one extra SG90 (Z). Listed in
`electrical/bom.md`. ~$15–30 total.

**Budget partial lock:** $250 for the cell. Micro820 is **not** in that number — borrow from
WashU first; buy only if they will not loan one (~$200–400 extra). Arduino is the motion
controller, not a substitute PLC.

**Kinematics locked — option A.** One gantry X + EOAT Z servo ≥ 15 mm. Pin standout ≤ 6 mm.
Destination pocket ~3–4 mm deep. Animated full stack: `docs/cycle-animation.html`.

### Pre-school window — 2026-08-13 → 2026-08-23

Internship wrap-up still competes through **Fri 8/14**. Do not start a build those two days.
From **Sat 8/15** this is the primary technical work.

| When | Do | Do not |
|---|---|---|
| 8/13–8/14 | Optional: sketch the cycle on paper (lower → grip → lift → X → lower → open). No CAD. | CAD the full cell, order the gantry, open firmware |
| 8/15–8/17 | Cardboard/foam mock: jaws + Z lift off a 1/4" dowel + Mega + both SG90s. Pass/fail on P-05 through a hand-moved X transfer. Photograph it. | Wait for 3D printing. A mock that fails is more useful than a pretty jaw you cannot print yet |
| 8/18–8/20 | Replace every TBD in `docs/requirements.md` with numbers from the mock + datasheets. Set a budget ceiling. Price a **one-axis** BOM (or kit-with-two-axes-unpowered). Flag anything >2 week lead time | Order three TB6600s "just in case." Do not buy the Micro820 until you know whether WashU will loan one |
| 8/21–8/23 | Email/check WashU shop + 3D print training + Micro820 / CCW access so day 1 of school is not spent hunting that. Create the project in Engineering OS. If Fusion/SW is available at home, CAD **jaws + nest only** around the locked object | Start Phase 2 motion code. Do not begin a second project |

Success for this window is **not** a running cell. It is: pick object locked, SG90
retention known, requirements no longer TBD, budget set, long-lead flagged, shop/PLC access
asked, one-axis Phase 1 ready to fabricate the week of 8/24.

### After school starts — 2026-08-24

Start Phase 1 fabrication (printed jaws/nest, hard stops, one linear axis). Do not begin
Phase 2 until Phase 1 has measured repeatability data.

## Risks

- **Scope creep**, and specifically the three-axis question above.
- **Long-lead parts stalling the semester.** Flag anything over two weeks and order early.
- **Stopping at CAD.** A modeled cell with no test data does not satisfy the point of this
  project. Phase 4 is not optional.
- **Competing commitments.** The plan is one serious solo project plus one selective team or
  research activity. More than that puts this one at risk.

## Resume prompt

> I'm continuing work on `eoat-automation-cell`. Read `HANDOFF.md`, `README.md`, and
> `docs/requirements.md` for context, plus `Projects/Rules.md` in the dashboard. I need help
> with <next task>.
