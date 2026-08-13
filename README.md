# EOAT Automation Cell

A small-scale automated pick station combining a custom-designed end-of-arm tool (EOAT), a
motion system, and PLC-based control logic — built to apply industry locating and fixturing
principles (NAAMS-inspired) and to integrate PLC sequencing with a separate motion
controller, mirroring how PLC-to-robot I/O handshakes work in real automation cells.

## Status

Concept and CAD phase. Started June 2026, primary solo project for Fall 2026.

Nothing is built yet. Some hardware is in hand — see [`electrical/bom.md`](electrical/bom.md).

## Repo structure

| Path | Contents |
|---|---|
| `cad/` | CAD models and renders for the gripper/EOAT and gantry |
| `firmware/` | Arduino motion control code |
| `plc/` | Allen-Bradley Micro820 ladder logic (CCW project files) |
| `electrical/` | Wiring diagrams and bill of materials |
| `docs/` | Requirements, test plan, build log, photos, demo videos |

Planning documents: [`docs/requirements.md`](docs/requirements.md) ·
[`docs/test-plan.md`](docs/test-plan.md) · [`HANDOFF.md`](HANDOFF.md)

## Project goals

- Design a gripper/locating fixture around a deliberate real-world constraint — geometry
  clearance and tolerance stack-up
- Validate the CAD design against a built, 3D-printed prototype
- Build a small motion system for pick sequences
- Integrate a Micro820 PLC for sensor logic, safety interlocks, and sequencing, handshaking
  with the motion controller

## Success criteria

The single statement that decides whether this project worked:

> The system shall autonomously detect, pick, transfer, and place a part for 50 consecutive
> cycles with at least 98% successful completion, documented fault handling, and measured
> positional repeatability.

Full requirement set in [`docs/requirements.md`](docs/requirements.md).

## Phases

Each phase is independently demonstrable. No phase starts before the previous one has
measured results.

| Phase | Goal | Demonstrable output | Status |
|---|---|---|---|
| 1 — Mechanical proof | One pick object, defined pickup and destination poses, one gripper/locating tool, one linear axis, repeatable hard stops | Manual cycle with basic repeatability data | Not started |
| 2 — Motion and sensing | Motion controller, home switch, part-present sensor, end-position confirmation | Repeatable automatic pick-and-place cycle | Not started |
| 3 — PLC supervisory control | PLC owns cycle start, permissives, state sequence, sensor validation, faults, reset, and the handshake; motion controller owns low-level movement | Fault injected, detected, reported, recovered | Not started |
| 4 — Validation | Measure repeatability, pick rate, cycle time, fault recovery, tolerance sensitivity, payload, gripper retention, sensor robustness | Completed test report | Not started |

## Scope

**In scope:** one pick object, one pickup pose and one destination pose, one gripper or
locating tool, one linear axis, repeatable hard stops, home/part-present/end-position
sensing, PLC supervisory control over a motion controller, and measured validation.

**Explicitly out of scope:** multiple part types, a part feeder, vision, and any industrial
communication architecture beyond a simple PLC-to-motion handshake.

The known failure mode for a project like this is fragmenting it into five — a custom EOAT
plus a custom gantry plus motion control plus a PLC system plus a comms architecture — and
finishing none. The smallest complete system comes first, then it extends.

## Results

Empty until measured. This section gets filled from `docs/test-plan.md`, not from
expectations.

| Metric | Target | Measured |
|---|---|---|
| Positional repeatability | TBD | |
| Successful pick rate | ≥ 98% over 50 cycles | |
| Cycle time | TBD | |
| Payload | TBD | |

## License

See [`LICENSE`](LICENSE).
