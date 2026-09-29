"""Export only individual solids with explicit mm units and fine mesh settings.

With part stems as arguments, only those parts are re-exported and their manifest rows
replaced; other curated files are left as they are. --supersede STEM moves that part's
curated files into a dated superseded folder with its own manifest (never deleted).
"""
import json, shutil, sys
from collections import Counter
from build_native import ROOT, connect, call, integer_ref, nothing
from check_print_meshes import inspect

STATUS_PART = 'Candidate geometry for fit trials; servo spline press fits (FIT-003/FIT-004), bearing/dowel fits and assembly access must be proven before a structural set is printed'
STATUS_COUPON = 'Print and measure coupon first'

def main(selected, supersede):
    sw = connect(); build = json.loads((ROOT/'assembly-build-report.json').read_text())
    counts = Counter(r['file'].split('\\')[-1] for r in build['components'] if r['file'].startswith('parts') and r['file'].split('\\')[-1].startswith('ARM-'))
    counts['FIT-001_Dowel_and_bearing_trial.SLDPRT'] = 1
    for coupon in ('FIT-003_MG996R_spline_socket_trial', 'FIT-004_SG90_spline_socket_trial'):
        counts[coupon+'.SLDPRT'] = 1
    out = ROOT/'fabrication-trial'; out.mkdir(exist_ok=True)
    manifest_path = out/'manifest.json'
    rows = {r['part']: r for r in json.loads(manifest_path.read_text())} if manifest_path.exists() else {}
    if supersede:
        folder = out/'superseded-2026-09-28'; folder.mkdir(exist_ok=True)
        old_path = folder/'superseded-manifest.json'
        old = json.loads(old_path.read_text()) if old_path.exists() else []
        for stem in supersede:
            row = rows.pop(stem, None)
            for sub in ('candidate-parts', 'fit-coupon'):
                for suffix in ('.STL', '.step'):
                    f = out/sub/(stem+suffix)
                    if f.exists(): shutil.move(str(f), str(folder/f.name))
            if row is not None:
                old.append(dict(row, status='SUPERSEDED 2026-09-28: not used by the owned-servo revision D; do not print',
                                file='superseded-2026-09-28/'+stem+'.STL'))
        old_path.write_text(json.dumps(old, indent=2))
    prior_i = {i: sw.GetUserPreferenceIntegerValue(i) for i in (78, 211)}
    prior_t = {i: sw.GetUserPreferenceToggle(i) for i in (69, 70, 191)}
    try:
        sw.SetUserPreferenceIntegerValue(78, 2); sw.SetUserPreferenceIntegerValue(211, 0)
        sw.SetUserPreferenceToggle(69, True); sw.SetUserPreferenceToggle(70, False); sw.SetUserPreferenceToggle(191, False)
        for filename, quantity in sorted(counts.items()):
            stem = filename[:-7]
            if selected and stem not in selected: continue
            source = ROOT/'parts'/filename
            folder = out/('fit-coupon' if filename.startswith('FIT-') else 'candidate-parts'); folder.mkdir(exist_ok=True)
            doc = sw.OpenDoc6(str(source), 1, 1, '', integer_ref(), integer_ref())
            if doc is None: raise RuntimeError('Open failed '+filename)
            sw.ActivateDoc3(str(source), True, 0, integer_ref())
            if call(call(sw, 'ActiveDoc'), 'GetPathName').lower() != str(source).lower(): raise RuntimeError('Wrong active export document')
            props = doc.Extension.CustomPropertyManager('')
            for key, value in [('Print material recommendation', 'PETG'), ('Assembly print quantity', str(quantity)),
                               ('Prototype status', 'Fit trial; physical validation outstanding')]:
                call(props, 'Add3', key, 30, value, 1)
            if not call(doc, 'Save3', 1, integer_ref(), integer_ref()): raise RuntimeError('Could not save part properties')
            path = folder/(stem+'.stl')
            err, warn = integer_ref(), integer_ref()
            if not doc.Extension.SaveAs(str(path), 0, 1, nothing(), err, warn) or err.value: raise RuntimeError('Export failed '+filename)
            mesh = inspect(path)
            if mesh['boundary_edges'] or mesh['nonmanifold_edges'] or mesh['signed_volume_in_file_units_cubed'] <= 0: raise RuntimeError('Invalid mesh '+filename)
            mp = call(doc.Extension, 'CreateMassProperty'); volume = call(mp, 'Volume')*1e9
            if abs(mesh['signed_volume_in_file_units_cubed']/volume-1) > .02: raise RuntimeError('Mesh/native volume mismatch')
            err, warn = integer_ref(), integer_ref()
            if not doc.Extension.SaveAs(str(folder/(stem+'.step')), 0, 1, nothing(), err, warn) or err.value: raise RuntimeError('STEP export failed')
            rows[stem] = {'part': stem, 'quantity': quantity, 'material': 'PETG',
                          'status': STATUS_COUPON if filename.startswith('FIT-') else STATUS_PART,
                          'units': 'mm', 'native_volume_mm3': volume, 'refreshed': '2026-09-28', **mesh}
            sw.CloseDoc(str(source)); print('Exported and checked', stem, flush=True)
        manifest_path.write_text(json.dumps([rows[k] for k in sorted(rows)], indent=2))
    finally:
        for i, v in prior_i.items(): sw.SetUserPreferenceIntegerValue(i, v)
        for i, v in prior_t.items(): sw.SetUserPreferenceToggle(i, v)

if __name__ == '__main__':
    args = sys.argv[1:]
    supersede = [args[i+1] for i, a in enumerate(args) if a == '--supersede']
    selected = [a for i, a in enumerate(args) if a != '--supersede' and (i == 0 or args[i-1] != '--supersede')]
    main(selected, supersede)
