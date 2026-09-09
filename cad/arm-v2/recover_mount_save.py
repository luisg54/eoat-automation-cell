"""Finish saving the successful component replacement after a dispatch wrapper error."""
import json
from build_assembly import Assembly,ROOT,connect,call,integer_ref,I
a=Assembly.__new__(Assembly); a.sw=connect(); a.models={}
path=ROOT/'ARM-B_Articulated_prototype_DEVELOPMENT.SLDASM'
a.doc=a.sw.OpenDoc6(str(path),2,1,'',integer_ref(),integer_ref())
a.report=json.loads((ROOT/'assembly-build-report.json').read_text())
new=[c for c in call(a.doc,'GetComponents',False) if 'M2.5' in call(c,'GetPathName')]
if len(new)!=16: raise RuntimeError('Expected completed replacement in current document')
for row in a.report['components']:
    if not row['key'].startswith('shoulder_servo_mount_'): continue
    suffix=row['key'].split('_')[-1]
    kind=('HW-S_' if suffix=='screw' else 'HW-N_' if suffix=='nut' else 'HW-W_')
    expected=row['position_mm'][:]
    if suffix=='nut': expected[2]=-4.
    matches=[]
    for c in new:
        p=call(c,'GetPathName')
        actual=[v*1000 for v in call(call(c,'Transform2'),'ArrayData')[9:12]]
        if kind in p and max(abs(x-y) for x,y in zip(actual,expected))<1e-4: matches.append(c)
    if len(matches)!=1: raise RuntimeError('Replacement match failed '+row['key'])
    c=matches[0]
    from pathlib import Path
    row.update(instance=call(c,'Name2'),file=str(Path(call(c,'GetPathName')).relative_to(ROOT)),position_mm=expected,rotation=I)
for row in a.report['fastener_stacks']:
    if row['label'].startswith('shoulder_servo_mount_'):
        row.update(diameter_mm=2.5,length_mm=14,thread_protrusion_mm=2.5)
a.save()
