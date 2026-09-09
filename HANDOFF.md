# EOAT Automation Cell — Handoff

## Active CAD session — 2026-09-08

Luis explicitly switched the CAD task to an **articulated robot arm** and authorized identifying additional hardware. See `docs/articulated-arm-requirements.md`; the older X-slide architecture below is historical context.

Current native SolidWorks 2026 work is in `cad/arm-v2`; revision A and the original demonstration are preserved. B has 199 components, 21 printed instances across 15 part types, 41 explicit fastener stacks, a removable yaw servo cassette, bearing retainers, positive yaw crossbolt and captured TPU pads. Shoulder ears use M2.5 hardware. The moving-pad servo-ear relief is now built. The fit coupon is built in B. `sketch-constraint-report.json` records 98 fully constrained sketches across 16 files (15 arm types plus coupon), with unchanged-solid checks.

**Native motion now works with dimension-driven mates.** Rebuilding the 194 rigid attachments finished. `refresh_joint_references.py` replaced stale joint references after part regeneration, fixing shoulder pivot translation. Direct `SetTransformAndSolve2` still failed to propagate the full rigid groups reliably; use the four native angle command dimensions instead. `check_motion.py` now does that and independently compares all 199 component transforms against kinematics. Nine revised poses passed with zero solid overlaps (`motion-inspection.json`). The previous -40/-50 shoulder/elbow pickup hit the yaw platform; revised pickup is -30/-60. Twelve samples of lift/yaw transfer also passed (`transfer-path-inspection.json`). These are discrete samples, not a swept proof; cables, tool access, payload and external fixtures are excluded.

Six native pose configurations are saved and their independent dimensions were read back (`pose-configurations.json`). `07_Free_motion_CHECK_COLLISIONS` suppresses command mates and uses four native angle-limit mates; values and zero feature errors verified in `native-motion-limits.json`. Provisional physical-angle bounds: yaw -60..60, shoulder -30..80, elbow -100..-5, grip 0..25. Arbitrary combinations are not certified collision-free. Native config switches invalidate cached component COM objects; re-fetch GetComponents after switching. `SaveConfiguration2` is not used: ShowConfiguration2 can return false when already active, so inspect ActiveConfiguration.Name.

**Fabrication hold at horn interfaces.** The modeled MG horn is a nominal 26 mm plate / 20 mm bolt circle. A sourced common 25T metal disc is 20 mm OD / 14 mm bolt circle / 4.5 mm total thickness / 2 mm plate, four M3 tapped holes (drawing linked in guide). It cannot be substituted directly. Select a real horn, update the upper-link pattern, washer relief, screw engagement and axial stack, then refresh affected mates and recheck. Existing MG model plate front is world Z23; the source metal disc with hub beginning Z16 would put its front at20.5, requiring a stack change. SG90 modeled hole radii8 and M2 through fasteners also require matching to owned horns; supplier drawing shows r8.3 and ~1 mm pilots. Do not release the horn-connected parts or order their fasteners yet. User was asked asynchronously whether calipers/PETG/TPU are available; no reply yet.

The current shoulder proposal is one additional MG996R positional servo; three purchased SG90s handle yaw, elbow and grip. The 3:1 SG90 shoulder candidate was rejected because of restricted travel and small load margin. Upper centers are60 mm; nominal forearm contact65 mm, with a better-centered circular payload location at forearm(69,1,3) mm. `calculate_cad_loads.py` now uses native volumes, conservative printed density and motion-group lever bounds, including jaw rotation. With20 g payload: design elbow0.04088 N m versus0.05884 budget (margin1.44); shoulder0.12858 versus0.27655 (margin2.15). Total modeled mass518.4 g at solid-density assumptions, not a weighed result. Ideal22 mm bearing contact occurs at grip7.83deg; assuming mu0.3 and weight factor2, estimated0.849 N/contact and0.01683 N m grip torque. The 10deg CAD transfer pose is a clearance demonstration, not a holding command. All physical fits, actual servo ratings, pad friction and duty-cycle tests remain pending.

**Revision C status (2026-09-08):** Arm 3 is a candidate interface revision, not a completed assembly. It contains regenerated native parts for the captured compact SG90 horn interface (`ARM-003`, `ARM-102`, `ARM-103`, `ARM-112`), a nominal PCD14/OD20 MG996R horn and upper-link pattern, and three printable SG90 clearance coupons (`FIT-002` at 0.05/0.10/0.15 mm per-side clearance). No `ARM-C_Articulated_prototype_DEVELOPMENT.SLDASM` has been built or verified yet. The compact-horn model is an envelope for layout only: measure the owned horn and servo gear-cover stack or substitute a measured COTS model before releasing Arm 3 for printing. Arm 2 remains the clean, saved native assembly checkpoint.

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
