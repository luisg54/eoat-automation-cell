"""Replace every nominal servo envelope in the saved D assembly with the owned files.

Edits the existing assembly in place (no rebuild): new owned-servo, hub, centre-screw and
fastener components are inserted at the home pose, a checkpoint is saved before mating,
new lock mates are created while every parent is still at home, then the superseded
nominal components, their mates and the old joint-axis mates are suppressed and renamed.
"""
import json, math, sys
from build_assembly import Assembly, ROOT, connect, call, integer_ref, nothing, pythoncom, win32com, rotation_z, compose, point, I, TOP
import owned_servo_design as D

PATH = ROOT/'ARM-D_Modular_parallel_gripper_DEVELOPMENT.SLDASM'
SUFFIX = '_superseded_nominal_servo'
SINGLE = {'yaw_servo', 'shoulder_servo', 'elbow_servo', 'yaw_horn', 'shoulder_horn', 'elbow_horn', 'yaw_horn_cap'}
PREFIXES = ('yaw_servo_mount_', 'shoulder_servo_mount_', 'elbow_servo_mount_', 'shoulder_horn_', 'elbow_horn_', 'yaw_horn_capture_')
NUT_H = {('nyloc', 3): 4.0, ('hex', 2): 1.6, ('hex', 3): 2.4}

def log(*args): print(*args, flush=True)

def main():
    sw = connect()
    report = json.loads((ROOT/'assembly-build-report.json').read_text())
    if 'owned_servo_update' in report: raise RuntimeError('Owned-servo update already recorded in the build report')
    rows = {r['key']: r for r in report['components']}
    old = sorted(k for k in rows if k in SINGLE or k.startswith(PREFIXES))
    if len(old) != 75: raise RuntimeError(f'Expected 75 superseded nominal components, found {len(old)}')
    old_locks = [m['name'] for m in report['mates'] if m['type'] == 'lock' and m['child'] in old]
    old_mates = old_locks+['J2_shoulder_axis', 'J3_elbow_axis']

    a = Assembly.__new__(Assembly); a.sw = sw; a.models = {}; a.existing = []
    a.doc = sw.OpenDoc6(str(PATH), 2, 1, '', integer_ref(), integer_ref())
    if a.doc is None: raise RuntimeError('Assembly did not open')
    from build_assembly import methods
    methods(a.doc, ['AddComponent5', 'AddMate5', 'ClearSelection2', 'EditRebuild3', 'ForceRebuild3'])
    a.report = report
    if call(call(a.doc, 'GetActiveConfiguration'), 'Name') != '01_Home':
        call(a.doc, 'ShowConfiguration2', '01_Home')
    call(a.doc, 'ForceRebuild3', False)
    cs = {call(c, 'Name2'): c for c in call(a.doc, 'GetComponents', False)}
    a.components = {r['key']: cs[r['instance']] for r in report['components']}

    def residual(keys):
        worst = 0.
        for key in keys:
            r = next(x for x in report['components'] if x['key'] == key)
            want = [r['rotation'][j][i] for i in range(3) for j in range(3)]+[v/1000 for v in r['position_mm']]
            got = list(call(call(a.components[key], 'Transform2'), 'ArrayData'))[:12]
            worst = max(worst, max(abs(x-y) for x, y in zip(want, got)))
        return worst
    home = residual(list(rows))
    log('Home residual before edits', home)
    if home > 1e-6: raise RuntimeError('Assembly is not at the recorded home pose')
    for key in old:
        if a.doc.FeatureByName(rows[key]['instance']) is None: raise RuntimeError('Component feature lookup failed: '+key)
    for name in old_mates:
        if a.doc.FeatureByName(name) is None: raise RuntimeError('Missing superseded mate '+name)

    shoulder = rotation_z(45)
    upper_origin = rows['upper']['position_mm']
    forearm_origin = rows['forearm']['position_mm']
    forearm_rotation = rows['forearm']['rotation']
    new_attachments, stacks = [], []

    def attached(key, filename, parent, pos, rot, hardware):
        a.add(key, filename, pos, rot, hardware)
        new_attachments.append((key, parent))

    def stack(label, parent, origin, rot, xy, top, bottom, d, length, nut_kind, washers, note):
        nut_h = NUT_H[(nut_kind, d)]
        w = .5 if washers else 0.
        items = [('screw', f'HW-S_M{d}x{length}_socket_ENVELOPE', top+w)]
        if washers:
            items += [('head_washer', f'HW-W_M{d}_washer_0p5_ENVELOPE', top), ('nut_washer', f'HW-W_M{d}_washer_0p5_ENVELOPE', bottom-.5)]
        items += [('nut', f'HW-N_M{d}_{nut_kind}_ENVELOPE', bottom-w-nut_h)]
        for suffix, filename, z in items:
            item_rot = compose(rot, rotation_z(30)) if suffix == 'nut' else rot
            attached(label+'_'+suffix, filename, parent, point(rot, (*xy, z), origin), item_rot, True)
        stacks.append({'label': label, 'parent': parent, 'diameter_mm': d, 'length_mm': length, 'nut': nut_kind,
                       'washers': 2 if washers else 0, 'grip_mm': top-bottom,
                       'thread_protrusion_mm': length-(top-bottom+2*w+nut_h), 'note': note})

    prior = sw.CommandInProgress; visible = sw.GetDocumentVisible(1)
    try:
        sw.CommandInProgress = True
        sw.DocumentVisible(False, 1)
        # Owned servos, placed from the measured interface frames.
        mounts = {'shoulder_servo_owned': (D.MG, D.MG_FILE, I, (0, 122, D.MG_PLATE), 'yaw'),
                  'elbow_servo_owned': (D.MG, D.MG_FILE, shoulder, point(shoulder, (60, 0, D.MG_PLATE), upper_origin), 'upper'),
                  'yaw_servo_owned': (D.SG, D.SG_FILE, TOP, (0, D.SG_SHELF_TOP_WORLD_Y, 0), 'base')}
        for key, (servo, filename, rw, origin, parent) in mounts.items():
            rot, pos = D.servo_transform(servo, rw, origin)
            attached(key, filename, parent, pos, rot, False)
        # Printed spline hubs and the servos' own centre screws.
        attached('shoulder_spline_hub', 'ARM-207_MG996R_printed_spline_hub', 'upper', point(shoulder, (0, 0, -D.HUB_THICKNESS), upper_origin), shoulder, False)
        attached('elbow_spline_hub', 'ARM-207_MG996R_printed_spline_hub', 'forearm', point(forearm_rotation, (0, 0, -D.HUB_THICKNESS), forearm_origin), forearm_rotation, False)
        centre = f'HW-S_M3x{D.MG_CENTRE_SCREW}_LOW_HEAD_D5p5_H2_ENVELOPE'
        attached('shoulder_spline_screw', centre, 'upper', point(shoulder, (0, 0, 0), upper_origin), shoulder, True)
        attached('elbow_spline_screw', centre, 'forearm', point(forearm_rotation, (0, 0, 0), forearm_origin), forearm_rotation, True)
        attached('yaw_spline_screw', f'HW-S_M2x{D.SG_CENTRE_SCREW}_PAN_HEAD_D4_H1p6_ENVELOPE', 'yaw', (0, D.COLLAR_FLOOR_TOP_Y, 0), TOP, True)
        for role, parent in (('shoulder', 'upper'), ('elbow', 'forearm')):
            stacks.append({'label': role+'_spline_screw', 'parent': parent, 'diameter_mm': 3, 'length_mm': D.MG_CENTRE_SCREW,
                           'head': 'DIN 7984 low head D5.5 x 2.0 on the ARM-207 floor', 'nut': 'none; MG996R spline M3 thread',
                           'thread_engagement_mm': D.MG_CENTRE_SCREW-D.HUB_FLOOR, 'thread_depth_in_file_mm': D.MG_THREAD_DEPTH,
                           'head_to_dowel_gap_mm': 3.0-D.MG_CENTRE_HEAD})
        stacks.append({'label': 'yaw_spline_screw', 'parent': 'yaw', 'diameter_mm': 2, 'length_mm': D.SG_CENTRE_SCREW,
                       'head': 'pan D4.0 x 1.6 on the ARM-003 floor', 'nut': 'none; SG90 output (file shows a 1.0 mm plain hole)',
                       'engagement_mm': D.SG_CENTRE_SCREW-(D.COLLAR_FLOOR_TOP_Y-D.COLLAR_SPLINE_TOP_Y),
                       'head_to_spindle_gap_mm': D.YAW_SPINDLE_END_Y-D.COLLAR_FLOOR_TOP_Y-D.SG_CENTRE_HEAD})
        # Hub-to-link M3 x 12 with nuts captured, recessed 0.5 mm, in ARM-207.
        for role, parent, origin, rot in (('shoulder', 'upper', upper_origin, shoulder), ('elbow', 'forearm', forearm_origin, forearm_rotation)):
            for i, (x, y) in enumerate(D.HUB_POINTS):
                label = f'{role}_hub_{i}'
                attached(label+'_screw', f'HW-S_M3x{D.HUB_SCREW}_socket_ENVELOPE', parent, point(rot, (x, y, 8.5), origin), rot, True)
                attached(label+'_head_washer', 'HW-W_M3_washer_0p5_ENVELOPE', parent, point(rot, (x, y, 8.0), origin), rot, True)
                nut_z = -D.HUB_THICKNESS+D.HUB_NUT_RECESS
                attached(label+'_nut', 'HW-N_M3_hex_ENVELOPE', parent, point(rot, (x, y, nut_z), origin),
                         compose(rot, rotation_z(math.degrees(math.atan2(y, x))+30)), True)
                stacks.append({'label': label, 'parent': parent, 'diameter_mm': 3, 'length_mm': D.HUB_SCREW,
                               'nut': 'M3 hex captured in ARM-207 pocket, recessed 0.5 mm', 'washers': 1,
                               'grip_mm': 8.5-(nut_z+2.4), 'thread_protrusion_mm': round(8.5-D.HUB_SCREW-nut_z, 6)})
        # MG996R ears: M3 through the measured D4 slotted ears; the far ear is 1.754 mm in the file.
        for role, parent, origin, rot in (('shoulder', 'yaw', (0, 122, D.MG_PLATE), I),
                                          ('elbow', 'upper', point(shoulder, (60, 0, D.MG_PLATE), upper_origin), shoulder)):
            for i, xy in enumerate(D.MG_EAR_HOLES):
                top = D.MG_EAR_NEAR if xy[0] < 0 else D.MG_EAR_FAR
                stack(f'{role}_servo_ear_{i}', parent, origin, rot, xy, top, -D.MG_PLATE, 3, D.MG_EAR_SCREW, 'nyloc', True,
                      'owned MG996R ear '+('output end 2.4 mm' if xy[0] < 0 else 'far end 1.754 mm'))
        # SG90 ears: no washers, because hole centres are 2.4 mm from the case walls.
        for i, xy in enumerate(D.SG_EAR_HOLES):
            stack(f'yaw_servo_ear_{i}', 'base', (0, D.SG_SHELF_TOP_WORLD_Y, 0), TOP, xy, D.SG_EAR, -D.SG_SHELF, 2, D.SG_EAR_SCREW, 'hex', False,
                  'owned SG90 ear; washers omitted because a 5 mm washer would overlap the case wall')
        log('Inserted', len(new_attachments), 'components')
    finally:
        sw.DocumentVisible(visible, 1)
        sw.CommandInProgress = prior

    # Durable checkpoint before any mate is created or suppressed.
    call(a.doc, 'EditRebuild3')
    if not call(a.doc, 'Save3', 1, integer_ref(), integer_ref()): raise RuntimeError('Checkpoint save failed')
    log('Saved pre-mate checkpoint')

    new_keys = [k for k, _ in new_attachments]
    if residual([k for k in rows]) > 1e-6: raise RuntimeError('Parents moved during insertion')
    for key, parent in new_attachments:
        a.rigid('Mount_'+key, parent, key)
    log('Created', len(new_attachments), 'lock mates')
    for name in old_mates:
        f = a.doc.FeatureByName(name)
        if f is None: raise RuntimeError('Missing superseded mate '+name)
        if not call(f, 'SetSuppression2', 0, 2, None): raise RuntimeError('Cannot suppress '+name)
        f.Name = name+SUFFIX
    a.mate('J2_shoulder_axis_owned_servo', 1, a.cylinder('upper', 4), a.cylinder('shoulder_servo_owned', 3.0), 0, 2)
    a.mate('J3_elbow_axis_owned_servo', 1, a.cylinder('forearm', 4), a.cylinder('elbow_servo_owned', 3.0), 0, 2)
    for key in old:
        f = a.doc.FeatureByName(rows[key]['instance'])
        if f is None: raise RuntimeError('Missing component feature '+rows[key]['instance'])
        if not call(f, 'SetSuppression2', 0, 2, None): raise RuntimeError('Cannot suppress component '+key)
    call(a.doc, 'ForceRebuild3', False)

    errors = []
    for m in [x for x in report['mates'] if x['name'] not in old_mates]:
        f = a.doc.FeatureByName(m['name'])
        if f is None: raise RuntimeError('Missing mate '+m['name'])
        if call(f, 'IsSuppressed2', 1, None)[0]: continue
        warning = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BOOL, False)
        code = call(f, 'GetErrorCode2', warning)
        if code: errors.append((m['name'], code))
    if errors: raise RuntimeError('Mate errors after update: '+str(errors))
    cs = {call(c, 'Name2'): c for c in call(a.doc, 'GetComponents', False)}
    a.components = {r['key']: cs[r['instance']] for r in report['components'] if r['key'] not in old}
    worst = residual([k for k in a.components])
    log('Home residual after update', worst)
    if worst > 1e-6: raise RuntimeError('Home pose changed after mate update: '+str(worst))

    # Record: superseded rows move out of the active lists; nothing is deleted.
    report['superseded_components'] = [rows[k] for k in old]
    report['components'] = [r for r in report['components'] if r['key'] not in old]
    report['superseded_mates'] = [dict(m, name=m['name']+SUFFIX) for m in report['mates'] if m['name'] in old_mates]
    report['mates'] = [m for m in report['mates'] if m['name'] not in old_mates]
    old_labels = {s['label'] for s in report['fastener_stacks'] if s['label'].startswith(PREFIXES)}
    report['superseded_fastener_stacks'] = [s for s in report['fastener_stacks'] if s['label'] in old_labels]
    report['fastener_stacks'] = [s for s in report['fastener_stacks'] if s['label'] not in old_labels]+stacks
    report['rigid_attachments'] = [x for x in report['rigid_attachments'] if x[1] not in old and x[0] not in old]+[list(x) for x in new_attachments]
    report['owned_servo_update'] = {'date': '2026-09-28', 'measurements': 'owned-servo-measurements.json',
        'design': 'owned_servo_design.py', 'inserted_components': len(new_keys), 'superseded_components': len(old),
        'superseded_mates': len(old_mates), 'status': 'Native CAD update; physical fits and performance unproven'}
    report['status'] = 'DEVELOPMENT: owned-servo geometry; physical fit and performance tests remain'
    if not call(a.doc, 'Save3', 1, integer_ref(), integer_ref()): raise RuntimeError('Final save failed')
    (ROOT/'assembly-build-report.json').write_text(json.dumps(report, indent=2))
    log('Saved assembly;', len(report['components']), 'active components,', len(report['mates']), 'active recorded mates')
    for model_path in a.models: sw.CloseDoc(model_path)
    sw.CloseDoc(str(PATH))
    log('Closed assembly and inserted part documents')

if __name__ == '__main__':
    main()
