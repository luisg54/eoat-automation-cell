"""Replace only the sixteen shoulder servo mounting components and their mates."""
import json,shutil
from datetime import datetime
from build_assembly import Assembly,ROOT,connect,call,integer_ref,nothing,I
a=Assembly.__new__(Assembly)
a.sw=connect(); a.models={}
path=ROOT/'ARM-B_Articulated_prototype_DEVELOPMENT.SLDASM'
backup=ROOT/'development-debug'/('before-servo-fasteners-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir(parents=True)
shutil.copy2(path,backup/path.name)
a.report=json.loads((ROOT/'assembly-build-report.json').read_text())
a.doc=a.sw.OpenDoc6(str(path),2,1,'',integer_ref(),integer_ref())
if a.doc is None: raise RuntimeError('Could not open assembly')
by_name={call(c,'Name2'):c for c in call(a.doc,'GetComponents',False)}
a.components={r['key']:by_name[r['instance']] for r in a.report['components']}
keys=[key for key in a.components if key.startswith('shoulder_servo_mount_')]
if len(keys)!=16: raise RuntimeError('Expected sixteen old mounting components')
a.doc.ClearSelection2(True)
for i,key in enumerate(keys):
    if not a.components[key].Select4(bool(i),nothing(),False): raise RuntimeError('Selection failed')
if not a.doc.Extension.DeleteSelection2(0): raise RuntimeError('Component replacement deletion failed')
if len(call(a.doc,'GetComponents',False))!=len(by_name)-16: raise RuntimeError('Unexpected component count')
for key in keys: a.components.pop(key)
a.report['components']=[r for r in a.report['components'] if r['key'] not in keys]
a.report['mates']=[r for r in a.report['mates'] if r.get('child') not in keys]
a.report['rigid_attachments']=[r for r in a.report['rigid_attachments'] if r[0] not in keys]
a.report['fastener_stacks']=[r for r in a.report['fastener_stacks'] if not r['label'].startswith('shoulder_servo_mount_')]
for i,(x,y) in enumerate([(-13,-5),(-13,5),(34,-5),(34,5)]):
    label='shoulder_servo_mount_'+str(i)
    items=[('screw','HW-S_M2.5x14_socket_ENVELOPE',7.5),
           ('head_washer','HW-W_M2.5_washer_0p5_ENVELOPE',7),
           ('nut_washer','HW-W_M2.5_washer_0p5_ENVELOPE',-.5),
           ('nut','HW-N_M2.5_nyloc_ENVELOPE',-4)]
    for suffix,filename,z in items:
        key=label+'_'+suffix
        a.add(key,filename,(x,122+y,z),I,True)
        a.rigid('Mount_'+key,'yaw',key)
        a.report['rigid_attachments'].append((key,'yaw'))
    a.report['fastener_stacks'].append({'label':label,'parent':'yaw','diameter_mm':2.5,
        'length_mm':14,'nut':'nyloc','grip_mm':7,'thread_protrusion_mm':2.5})
a.save()
