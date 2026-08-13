# EOAT / Automation Cell — Requirements

**Written:** not yet finalized — draft seeded 2026-08-11
**Last revised:** 2026-08-11

Fill these in with real numbers before opening CAD. Targets marked TBD should be set from
realistic hardware performance, not from ambition. It is better to set a target you can hit
and then tighten it than to miss a number you invented.

## Success criteria

The single statement that decides whether this project worked:

> The system shall autonomously detect, pick, transfer, and place a part for 50 consecutive
> cycles with at least 98% successful completion, documented fault handling, and measured
> positional repeatability.

## Functional requirements

| ID | Requirement | Verification method | Status |
|---|---|---|---|
| F-01 | The system shall detect the presence of a part at the pickup pose before initiating a cycle | Test | Not verified |
| F-02 | The system shall pick a single part from a fixtured pickup pose | Test | Not verified |
| F-03 | The system shall transfer the part along one linear axis to a defined destination pose | Test | Not verified |
| F-04 | The system shall confirm part placement before returning to home | Test | Not verified |
| F-05 | The system shall home on start and confirm the home position via switch | Test | Not verified |
| F-06 | The PLC shall own cycle start, permissives, state sequencing, fault detection, and reset | Demonstration | Not verified |
| F-07 | The motion controller shall own low-level movement and shall act only on a PLC permissive | Demonstration | Not verified |

## Performance requirements

| ID | Requirement | Target | Measured | Status |
|---|---|---|---|---|
| P-01 | Positional repeatability at the destination pose | ± TBD mm | | Not verified |
| P-02 | Successful completion rate | ≥ 98% over 50 consecutive cycles | | Not verified |
| P-03 | Cycle time | ≤ TBD s | | Not verified |
| P-04 | Payload | ≥ TBD g | | Not verified |
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

- **Budget:** TBD
- **Timeline:** Fall 2026 semester, alongside one selective team or research activity
- **Tools available:** TBD — confirm machine shop, 3D printing, and PLC hardware access
- **Skills to be learned:** PLC ladder logic, state machines, PLC-to-motion handshakes,
  safety logic fundamentals, fault recovery, sensor selection, electrical schematics

### Hardware already in hand

Prototyping against these costs nothing and can start immediately.

| Item | Use |
|---|---|
| ELEGOO Mega R3 | Motion controller for Phases 1–2 |
| SG90 servo | Gripper actuation — verify it meets P-04 payload and P-05 retention |
| Breadboard and jumper set | Sensor and I/O bring-up |

### Hardware identified, not ordered

Allen-Bradley Micro820 `2080-LC20-20QWB`, NEMA17 steppers, TB6600 drivers, 24 V supply,
inductive proximity sensors, limit switches, V-slot gantry kit. Full list and status in
`../electrical/bom.md`.

**Open decision affecting these requirements:** the BOM specifies three steppers and a
gantry kit, while Phase 1 calls for one linear axis. See "Scope tension" in `../HANDOFF.md`.
Resolve before ordering — it changes I-01 current draw and the PLC I/O count.

## Revision log

| Date | Requirement | Change | Why |
|---|---|---|---|
| 2026-08-11 | all | Initial draft seeded from the Fall 2026 plan | Project scoping |
