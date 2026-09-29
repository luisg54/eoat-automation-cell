"""Verify the reopened D assembly: references, suppression, mates, features, poses, interference.

Run on a freshly opened assembly. For each saved pose configuration it checks the stored
transforms against the kinematic model, active mate errors, superseded-component suppression
and native solid interference (classified by check_motion.classify). Preserved C hashes are
re-checked. Nothing is regenerated; the assembly is saved once at home.
"""
import json, hashlib
from check_motion import doc, sw, ROOT, call, pose, integer_ref, pythoncom, win32com, interference, classify
build = json.loads((ROOT/'assembly-build-report.json').read_text())
superseded = [r['instance'] for r in build.get('superseded_components', [])]
superseded_mates = [m['name'] for m in build.get('superseded_mates', [])]
REFERENCE_MULTIBODY = ('MG996R_servo.SLDPRT', 'SERVO_SG90.SLDPRT')   # user-supplied owned-servo files
report = {'status': 'Native CAD verification of the reopened assembly; physical fit and performance tests remain',
          'opened_fresh': True, 'configurations': []}

def mate_errors():
    errors = []
    for m in build['mates']:
        f = doc.FeatureByName(m['name'])
        if f is None: raise RuntimeError('Missing mate '+m['name'])
        if call(f, 'IsSuppressed2', 1, None)[0]: continue
        warning = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BOOL, False)
        code = call(f, 'GetErrorCode2', warning)
        if code: errors.append({'name': m['name'], 'code': code})
    return errors

def suppression_state():
    cs = {call(c, 'Name2'): c for c in call(doc, 'GetComponents', False)}
    active = [r['instance'] for r in build['components']]
    bad_old = [i for i in superseded if call(cs[i], 'GetSuppression2') != 0]
    bad_new = [i for i in active if call(cs[i], 'GetSuppression2') == 0]
    live_old_mates = [n for n in superseded_mates if not call(doc.FeatureByName(n), 'IsSuppressed2', 1, None)[0]]
    return {'superseded_components_suppressed': len(superseded)-len(bad_old), 'superseded_unsuppressed': bad_old,
            'active_components_resolved': len(active)-len(bad_new), 'active_suppressed': bad_new,
            'superseded_mates_suppressed': len(superseded_mates)-len(live_old_mates), 'superseded_mates_active': live_old_mates}

for p in json.loads((ROOT/'pose-configurations.json').read_text()):
    call(doc, 'ShowConfiguration2', p['name']); call(doc, 'ForceRebuild3', False)
    if call(call(doc, 'GetActiveConfiguration'), 'Name') != p['name']: raise RuntimeError('Could not activate '+p['name'])
    residual = pose(*p['pose_values'], command=False)
    errors = mate_errors()
    state = suppression_state()
    expected, known, unexpected = classify(interference(), p['pose_values'][3])
    row = {'name': p['name'], 'pose_values': p['pose_values'], 'transform_residual': residual, 'mate_errors': errors,
           **state, 'unexpected_interferences': unexpected,
           'expected_designed_engagements': len(expected),
           'expected_engagement_volume_mm3': sum(e['volume_mm3'] for e in expected), 'known_supplier_overlaps': known}
    report['configurations'].append(row)
    print(p['name'], 'residual', residual, 'mate errors', len(errors), 'unexpected', len(unexpected),
          'expected', len(expected), 'superseded live', len(state['superseded_unsuppressed']), flush=True)
    if errors or unexpected or state['superseded_unsuppressed'] or state['active_suppressed'] or state['superseded_mates_active'] or residual > 1e-6:
        (ROOT/'saved-assembly-verification.json').write_text(json.dumps(report, indent=2))
        raise RuntimeError('Verification failed in '+p['name'])

limits = json.loads((ROOT/'native-motion-limits.json').read_text())
call(doc, 'ShowConfiguration2', limits['configuration']); call(doc, 'ForceRebuild3', False)
for row in limits['limits']:
    f = doc.FeatureByName(row['name'])
    warning = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BOOL, False)
    if call(f, 'IsSuppressed2', 1, None)[0] or call(f, 'GetErrorCode2', warning): raise RuntimeError('Invalid free-motion limit')
    if not call(doc.FeatureByName(row['name'].replace('_travel_limit', '_command')), 'IsSuppressed2', 1, None)[0]:
        raise RuntimeError('Fixed command active in drag configuration')
free_state = suppression_state()
if free_state['superseded_unsuppressed'] or free_state['active_suppressed'] or mate_errors(): raise RuntimeError('Free-motion configuration invalid')
report['free_arm_motion_limits_verified'] = True
report['free_motion_configuration'] = {'name': limits['configuration'], **free_state}

call(doc, 'ShowConfiguration2', '01_Home'); call(doc, 'ForceRebuild3', False)
cs = {call(c, 'Name2'): c for c in call(doc, 'GetComponents', False)}
if len(cs) != len(build['components'])+len(superseded): raise RuntimeError('Component count mismatch')
seen = {}; feature_errors = []; outside = []
for row in build['components']:
    c = cs[row['instance']]; model = call(c, 'GetModelDoc2')
    path = ROOT/row['file']
    if model is None or call(model, 'GetPathName').lower() != str(path).lower(): raise RuntimeError('Wrong reference '+row['key'])
    if not str(path).lower().startswith(str(ROOT).lower()): outside.append(str(path))
    if row['file'] in seen: continue
    bodies = len(call(model, 'GetBodies2', 0, False) or [])
    if bodies != 1 and path.name not in REFERENCE_MULTIBODY: raise RuntimeError('Part must contain one solid: '+str(path))
    mp = call(model.Extension, 'CreateMassProperty')
    seen[row['file']] = {'solid_bodies': bodies, 'volume_mm3': call(mp, 'Volume')*1e9}
    f = call(model, 'FirstFeature')
    while f:
        warning = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BOOL, False)
        code = call(f, 'GetErrorCode2', warning)
        if code: feature_errors.append({'part': row['file'], 'feature': call(f, 'Name'), 'code': code})
        f = call(f, 'GetNextFeature')
if feature_errors or outside: raise RuntimeError(str(feature_errors or outside))
report.update(active_components_verified=len(build['components']), superseded_components_suppressed=len(superseded),
              unique_active_parts_verified=len(seen), unique_parts=seen, part_feature_errors=feature_errors,
              reference_multibody_allowed=list(REFERENCE_MULTIBODY))
inspection = json.loads((ROOT/'user-revision-inspection.json').read_text())
for row in inspection['parts']:
    path = ROOT.parent/'arm-v3'/row['file']
    if hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']: raise RuntimeError('C source changed: '+str(path))
report['original_C_files_unchanged'] = len(inspection['parts'])
if not call(doc, 'Save3', 1, integer_ref(), integer_ref()): raise RuntimeError('Save failed')
(ROOT/'saved-assembly-verification.json').write_text(json.dumps(report, indent=2))
print('Verified', len(report['configurations']), 'pose configurations, references, features, suppression and preserved C files', flush=True)
