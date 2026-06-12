# EOAT Automation Cell

A small-scale automated pick station combining a custom-designed 
end-of-arm tool (EOAT), a motion system, and PLC-based control logic 
— built to apply industry locating/fixturing principles (NAAMS-inspired) 
and integrate PLC sequencing with a separate motion controller, 
mirroring how PLC-to-robot I/O handshakes work in real automation cells.

## Status
🚧 In progress — concept and CAD phase (started June 2026)

## Repo Structure
- `/cad` — CAD models and renders for the gripper/EOAT and gantry
- `/firmware` — Arduino motion control code
- `/plc` — Allen-Bradley Micro820 ladder logic (CCW project files)
- `/electrical` — wiring diagrams and bill of materials
- `/docs` — build log, photos, and demo videos

## Project Goals
- Design a gripper/locating fixture around a deliberate real-world 
  constraint (geometry clearance, tolerance stack-up)
- Validate CAD design against a built/3D-printed prototype
- Build a small motion system (Arduino-driven) for pick sequences
- Integrate a PLC (Micro820) for sensor logic, safety interlocks, 
  and sequencing — handshaking with the motion controller