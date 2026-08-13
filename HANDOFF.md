# EOAT Automation Cell — Handoff

**Last updated:** 2026-08-11
**Status:** Planning. Nothing built. Some hardware in hand, most not ordered.

## Current state

Repo scaffolded in June 2026 with the `cad` / `firmware` / `plc` / `electrical` / `docs`
layout. No CAD models committed, no firmware, no ladder logic, no wiring diagrams.

A bill of materials exists in `electrical/bom.md` with real part selections. Three items are
already owned: an ELEGOO Mega R3, an SG90 servo for gripper actuation, and a breadboard and
jumper set. Everything else is identified but not ordered, including the Allen-Bradley
Micro820 (`2080-LC20-20QWB`).

Scope, phases, and success criteria are in `README.md`. Testable requirements are in
`docs/requirements.md` — several targets are still TBD and need real numbers once hardware
is selected.

## Scope tension to resolve first

The BOM lists **three NEMA17 steppers, three TB6600 drivers, and a V-slot gantry kit**. That
is a three-axis gantry. The plan's Phase 1 calls for **one linear axis** and warns explicitly
against expanding this into a custom EOAT plus a custom gantry plus motion control plus a PLC
system plus a comms architecture.

Three axes is not automatically wrong — a purchased V-slot kit is much less work than
building an axis. But committing to three axes before one axis has measured repeatability
data is how this project stalls. Recommended path: buy the kit if it's cheap enough, then
**drive only one axis through Phase 1 and Phase 2** and leave the other two mechanically
present but unpowered until Phase 3 is done.

Decide this before ordering, because it changes the driver count, the power supply sizing,
and the PLC I/O count.

## Blockers

| Blocker | Impact | What would unblock it |
|---|---|---|
| Machine shop and 3D printing access for Fall 2026 not confirmed | Determines whether the EOAT is fabricated or purchased; changes BOM and timeline | Confirm WashU shop access and required training |
| Micro820 not ordered | Phase 3 cannot start | Check whether a lab unit can be borrowed before buying; confirm Connected Components Workbench access |
| Budget not set | Cannot order long-lead items | Set a number |
| Axis count not decided | Blocks the BOM order | See "Scope tension" above |
| Performance targets still TBD | Requirements are not yet testable | Set once the gantry kit and gripper are chosen |

## Open questions

- What is the one pick object? Choosing it constrains the gripper, the fixture, and the
  payload requirement all at once. This is the highest-leverage unblocked decision.
- Is the SG90 servo adequate for the gripper, or does the chosen pick object need more
  holding force? Cheap to test early with hardware already in hand.
- Is a physical Micro820 worth buying, or is a simulated PLC acceptable for demonstrating
  state-machine and handshake logic? Physical hardware is a much stronger interview story.

## Next steps

1. Choose the pick object. Nothing else should be ordered first.
2. Resolve the axis-count question above.
3. Prototype the gripper with the Mega and SG90 already in hand — no purchase required, and
   it de-risks the payload and retention requirements.
4. Replace every TBD in `docs/requirements.md` with a real number.
5. Confirm shop access, printing access, and Micro820 availability.
6. Create the project in Engineering OS so evidence is captured as it happens rather than
   reconstructed later.
7. Start Phase 1. Do not begin Phase 2 until Phase 1 has measured repeatability data.

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
