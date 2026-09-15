"""Record D's native evidence without overwriting the preserved C history."""
import json
from pathlib import Path
root=Path(__file__).resolve().parent
project=root.parent.parent
build=json.loads((root/'assembly-build-report.json').read_text())
status='Verification in progress; no print or production release.'
motion=root/'motion-inspection.json'
if motion.exists():
    samples=json.loads(motion.read_text())['samples']
    status+=' Latest motion report: '+', '.join(s['name']+': '+str(len(s['interferences']))+' overlaps' for s in samples)+'.'
section=f'''## Active revision D - 2026-09-12

**Latest saved model: `cad/arm-v4/ARM-D_Modular_parallel_gripper_DEVELOPMENT.SLDASM`.** {len(build['components'])} components, {len(build['fastener_stacks'])} fastener stacks. {status}

User asked to improve functional geometry beyond fillets, including ARM-002/102/103. He owns TWO MG996Rs and permits sensible COTS. His saved C edits were inspected and preserved (38 unique parts, no feature errors; hashes in `user-revision-inspection.json`). Do not regenerate C. D derives ARM-201/202/203 from his native histories and copies unchanged parts from saved C.

New parts: ARM-201 upper link for both MG996Rs, ARM-202 separate yaw platform, ARM-203 bolt-on upright, ARM-204 straight modular forearm, ARM-205 removable parallel-gripper fork, ARM-206 crush spacers (two). Both pitch joints use 20.5 mm horn spacing, 32 mm standoffs, OD20/PCD14 metal horns. One SG90 remains for yaw. Tool candidate is Pololu 3551, 32 mm stroke, supplier 30 g including FS90-FB servo, $29.95; supplier showed backorders. Official STEP/PDF saved and drawing visually inspected. HW-202/HW-203 are supplier body/jaws. No purchase occurred. Fork uses the actual two 4.2 mm axes, M4x35, 0.5 mm small-series washers, nylocs and 13 mm crush spacers inside 13.4 mm ear gaps. Four M3x16 attach the adapter; four M3x20 attach the upright.

Resource fix: visible part windows grew SW to ~6.6 GB and a fastener OpenDoc returned null. Saved 158-component partial insertion under `development-debug/D_partial_insertion.SLDASM`; resumed without rebuilding with `--resume-partial`, DocumentVisible(False,1), CommandInProgress=True. Complete model saved; SW was ~0.86 GB. Keep component windows hidden during assembly insertion; do not run concurrent COM scripts. Initial jaw alignment QA caught flipped imported planes; corrected with closest alignment and a flipped right-side opening distance. Superseded mates are suppressed, not deleted. Full builder now includes these settings and a pre-mate save checkpoint.

Next: finish transform/collision checks including reduced shoulder clearance with larger elbow case, calculate D loads/BOM, constrain new sketches, verify saved configurations/references, update guide/BOM and curated exports. Current documents below still describe C until explicitly revised. Physical horn fit, bearing/dowel trials, cables/driver access, grip force/current and repeatability/cycle evidence remain required. User latest instruction: continue and verify carefully; usage reset, laptop 16 GB. No new subagents authorized.

'''
path=project/'HANDOFF.md'; old=path.read_text(encoding='utf-8-sig')
start=old.find('## Active revision D'); end=old.find('## Active CAD session')
if end<0: raise RuntimeError('Historical C handoff not found')
old=old[:start if start>=0 else end]+section+old[end:]
path.write_text(old,encoding='utf-8')
print('Recorded D checkpoint')
