# EOAT Automation Cell — Handoff

**Last updated:** 2026-08-13
**Status:** Planning. Pick object locked (608ZZ). Motion locked (option A: gantry X + EOAT Z servo). Nothing built.
**School start:** 2026-08-24. Pre-school window is 2026-08-12 → 2026-08-23.

## Current state

Repo scaffolded in June 2026 with the `cad` / `firmware` / `plc` / `electrical` / `docs`
layout. No CAD models committed, no firmware, no ladder logic, no wiring diagrams.

A bill of materials exists in `electrical/bom.md` with real part selections. Three items are
already owned: an ELEGOO Mega R3, an SG90 servo for gripper actuation, and a breadboard and
jumper set. Everything else is identified but not ordered, including the Allen-Bradley
Micro820 (`2080-LC20-20QWB`).

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
| Machine shop and 3D printing access for Fall 2026 not confirmed | Determines whether the EOAT is fabricated or purchased; changes BOM and timeline | Confirm WashU shop access and required training |
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
