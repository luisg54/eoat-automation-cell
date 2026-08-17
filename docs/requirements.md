# EOAT / Automation Cell — Requirements

**Written:** not yet finalized — draft seeded 2026-08-11
**Last revised:** 2026-08-13

Fill these in with real numbers before opening CAD. Targets marked TBD should be set from
realistic hardware performance, not from ambition. It is better to set a target you can hit
and then tighten it than to miss a number you invented.

## Success criteria

The single statement that decides whether this project worked:

> The system shall autonomously detect, pick, transfer, and place a part for 50 consecutive
> cycles with at least 98% successful completion, documented fault handling, and measured
> positional repeatability.

## Pick object (locked 2026-08-12)

| | |
|---|---|
| **Part** | 608ZZ skate bearing |
| **Why this part** | Rigid, identical, cheap, ferrous (inductive prox), light enough for the SG90, and it has an ID that can take a locating pin — the same class of constraint problem as industrial hole locating |
| **Nominal geometry** | 22 mm OD / 8 mm ID / 7 mm width |
| **Nominal mass** | ~12 g (confirm on a scale before setting final P-04) |
| **Qty to buy** | 5 (spares for drop and offset tests) |

A round bearing has **no clocking datum**. Full 3-2-1 (hole + slot + plane) is out of scope for this object. That is accepted. What this object *is* set up to teach:

- **Hole locating** — pickup nest constrains XY with an ID pin and Z with a rest face
- **Clearance vs constraint** — gripper jaws must approach and retract without hitting the pin or rest pads
- **Constraint transfer** — pickup locates on the ID pin; destination locates on a different scheme (OD pocket or second pin), so the part leaves one datum set and enters another
- **Tolerance sensitivity (P-06)** — offset the part on the pin until pick fails; that number is the interview result
- **Retention without relying on the gripper to locate** — jaws hold for transfer only

If the design becomes two 3D-printed fingers pinching the rim and dropping it in a dish, this object teaches almost nothing. The nest and the clearance problem are the project. The bearing is just the payload.

## Motion scheme (locked 2026-08-13) — option A

A vertical ID pin only works if the tool can come down onto it and lift off it. One gantry
motor that only slides left–right cannot do that.

| | Role | Hardware |
|---|---|---|
| **X** | Transfer between pickup and destination | One powered gantry / linear axis (stepper). Phase 1–2 drives **only this axis** |
| **Z** | Short lift to clear locators (~15–20 mm) | Second SG90 (or equivalent) **on the EOAT**, not a gantry Z |
| **Grip** | Open / close only — does not locate | SG90 already in hand |

Cycle: lower onto pin → close grip → lift clear → X transfer → lower into destination nest → open → lift → return.

Concept sketches (cross-section): [`concept-sketches.html`](concept-sketches.html).

Design intent (confirm when hardware is in hand):

- Pin standout above the rest face: **≤ 6 mm** (stays inside the 7 mm bearing width so jaws can close on the OD)
- Destination OD pocket depth: **~3–4 mm** (captures the part, still liftable)
- Z stroke: **≥ 15 mm** (clears pin + pocket + approach margin)

This is not a 2-axis or 3-axis gantry. A purchased V-slot kit may still have unused axes
mechanically present; they stay unpowered through Phase 2.

## Functional requirements

| ID | Requirement | Verification method | Status |
|---|---|---|---|
| F-01 | The system shall detect the presence of a part at the pickup pose before initiating a cycle | Test | Not verified |
| F-02 | The system shall pick a single part from a fixtured pickup pose | Test | Not verified |
| F-03 | The system shall transfer the part along one gantry (X) axis to a defined destination pose | Test | Not verified |
| F-04 | The system shall confirm part placement before returning to home | Test | Not verified |
| F-05 | The system shall home on start and confirm the home position via switch | Test | Not verified |
| F-06 | The PLC shall own cycle start, permissives, state sequencing, fault detection, and reset | Demonstration | Not verified |
| F-07 | The motion controller shall own low-level movement and shall act only on a PLC permissive | Demonstration | Not verified |
| F-08 | The pickup fixture shall fully locate the bearing before gripper close: Z rest face + ID pin. The gripper shall not be the locator | Inspection + test | Not verified |
| F-09 | Gripper jaws shall clear the pickup locators on approach and retract with no contact | Inspection | Not verified |
| F-10 | The destination fixture shall locate the bearing with a **different** datum scheme than pickup (OD pocket or second pin, not a copy of pickup) | Inspection | Not verified |
| F-11 | The EOAT shall provide a Z stroke ≥ 15 mm to clear pickup and destination locators before any X motion. Z is a tool servo, not a gantry axis | Test | Not verified |

## Performance requirements

| ID | Requirement | Target | Measured | Status |
|---|---|---|---|---|
| P-01 | Positional repeatability at the destination pose | ± TBD mm | | Not verified |
| P-02 | Successful completion rate | ≥ 98% over 50 consecutive cycles | | Not verified |
| P-03 | Cycle time | ≤ TBD s | | Not verified |
| P-04 | Payload | ≥ 20 g | | Not verified |
| P-05 | Gripper retention through full transfer | 0 drops in 50 cycles | | Not verified |
| P-06 | Tolerance sensitivity — part position offset the system still handles | ± TBD mm | | Not verified |

## Interface and environment

| ID | Requirement |
|---|---|
| I-01 | Operates from a single bench supply at TBD V, ≤ TBD A |
| I-02 | Fits within a TBD × TBD × TBD mm bench envelope |
| I-03 | Operates on a standard desk or bench surface without anchoring to the building |
| I-04 | Assembles and disassembles with hand tools only |

## Safety and fault handling

| ID | Requirement |
|---|---|
| S-01 | The system shall reach a safe, de-energized state on loss of power, without dropping a held part onto a hand path |
| S-02 | The system shall detect a missing part at pickup, report the fault, and require an explicit reset |
| S-03 | The system shall detect a failed placement confirmation, report the fault, and require an explicit reset |
| S-04 | The system shall detect a homing failure and refuse to run a cycle |
| S-05 | No motion shall be commanded without a PLC permissive |

Fault handling is a first-class requirement here, not an afterthought. A cell that only works
when nothing goes wrong does not demonstrate anything an automation employer cares about.

## Constraints

- **Budget:** **$250 for the cell** (gantry / one powered axis, drivers, PSU, sensors,
  printed EOAT/nests, pick object, extra servo if needed). **PLC is separate:** borrow from
  WashU first; if buying a Micro820, expect ~$200–400 on top. Do not fold the PLC into the
  $250 or replace it with “Arduino does both.” If a decent linear kit alone blows past ~$150,
  raise the cell budget rather than cheap out on the axis you will use all semester.
- **Timeline:** Fall 2026 semester, alongside one selective team or research activity
- **Tools available:** TBD — confirm machine shop, 3D printing, and PLC hardware access
- **Skills to be learned:** locating / constraint (ID pin + rest, clearance vs locator
  geometry), datum transfer between fixtures, tolerance sensitivity, PLC ladder logic,
  state machines, PLC-to-motion handshakes, safety logic fundamentals, fault recovery,
  sensor selection, electrical schematics

### Hardware already in hand

Prototyping against these costs nothing and can start immediately.

| Item | Use |
|---|---|
| ELEGOO Mega R3 | Motion controller for Phases 1–2 |
| SG90 servo | Gripper open/close — verify it meets P-04 payload and P-05 retention |
| Breadboard and jumper set | Sensor and I/O bring-up |

### Hardware identified, not ordered

Allen-Bradley Micro820 `2080-LC20-20QWB`, NEMA17 steppers, TB6600 drivers, 24 V supply,
inductive proximity sensors, limit switches, V-slot gantry kit. Full list and status in
`../electrical/bom.md`.

**Axis decision (locked 2026-08-13):** Phase 1–2 powers **one gantry axis (X)** plus a tool
Z servo (F-11). Do not buy or wire three TB6600s for Phase 1. A 3-axis kit is allowed only
if it is cheaper as a kit; unused axes stay unpowered. See `../HANDOFF.md`.

## Revision log

| Date | Requirement | Change | Why |
|---|---|---|---|
| 2026-08-11 | all | Initial draft seeded from the Fall 2026 plan | Project scoping |
| 2026-08-12 | pick object, F-08–F-10, P-04 | Locked 608ZZ; locating/clearance rules; payload ≥ 20 g | Object choice + keep the EOAT from becoming a pinch gripper |
| 2026-08-13 | budget | Cell $250; PLC separate, borrow-first | Avoid Arduino-as-PLC and under-buying the axis |
| 2026-08-13 | motion, F-03, F-11 | Option A: one gantry X + EOAT Z servo ≥ 15 mm | Vertical ID pin is otherwise kinematically impossible |
