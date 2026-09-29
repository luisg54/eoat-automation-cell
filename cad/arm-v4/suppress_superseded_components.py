"""Suppress the superseded nominal-servo components in every configuration.

IFeature.SetSuppression2(all configurations) returned True for component features but left
them resolved, so each configuration is visited and IComponent2.SetSuppression2 is applied
to the active one. Components are suppressed, never deleted; their mates were already
suppressed and renamed by update_owned_servo_assembly.py.
"""
import json
from build_native import ROOT, connect, call, integer_ref, pythoncom, win32com

PATH = ROOT/'ARM-D_Modular_parallel_gripper_DEVELOPMENT.SLDASM'

def main():
    sw = connect()
    report = json.loads((ROOT/'assembly-build-report.json').read_text())
    old = [r['instance'] for r in report['superseded_components']]
    active_instances = [r['instance'] for r in report['components']]
    doc = sw.GetOpenDocumentByName(str(PATH)) or sw.OpenDoc6(str(PATH), 2, 1, '', integer_ref(), integer_ref())
    if doc is None: raise RuntimeError('Assembly did not open')
    configs = list(call(doc, 'GetConfigurationNames'))
    rows = []
    prior = sw.CommandInProgress
    try:
        sw.CommandInProgress = True
        for cfg in configs:
            call(doc, 'ShowConfiguration2', cfg)
            if call(call(doc, 'GetActiveConfiguration'), 'Name') != cfg: raise RuntimeError('Could not activate '+cfg)
            cs = {call(c, 'Name2'): c for c in call(doc, 'GetComponents', False)}
            changed = 0
            for inst in old:
                c = cs[inst]
                if call(c, 'GetSuppression2') != 0:
                    call(c, 'SetSuppression2', 0)
                    changed += 1
            call(doc, 'EditRebuild3')
            cs = {call(c, 'Name2'): c for c in call(doc, 'GetComponents', False)}
            still = [i for i in old if call(cs[i], 'GetSuppression2') != 0]
            inactive = [i for i in active_instances if call(cs[i], 'GetSuppression2') == 0]
            if still or inactive: raise RuntimeError(f'{cfg}: unsuppressed superseded {still[:5]}, suppressed active {inactive[:5]}')
            rows.append({'configuration': cfg, 'newly_suppressed': changed, 'superseded_suppressed': len(old), 'active_resolved': len(active_instances)})
            print(rows[-1], flush=True)
    finally:
        sw.CommandInProgress = prior
    call(doc, 'ShowConfiguration2', '01_Home'); call(doc, 'ForceRebuild3', False)
    if not call(doc, 'Save3', 1, integer_ref(), integer_ref()): raise RuntimeError('Save failed')
    report['owned_servo_update']['component_suppression'] = {'method': 'IComponent2.SetSuppression2 per configuration', 'configurations': rows}
    (ROOT/'assembly-build-report.json').write_text(json.dumps(report, indent=2))
    print('Saved with superseded components suppressed in', len(rows), 'configurations', flush=True)

if __name__ == '__main__':
    main()
