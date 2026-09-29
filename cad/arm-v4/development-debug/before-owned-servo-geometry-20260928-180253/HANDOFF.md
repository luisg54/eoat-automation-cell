# EOAT Automation Cell — Handoff

## Active revision D - 2026-09-12

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
