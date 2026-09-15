"""Correct measured fastener interferences without rebuilding the arm assembly."""
import json,math,shutil
from build_assembly import Assembly,ROOT,connect,call,integer_ref,pythoncom,win32com,nothing
from build_revision_parts import inherited
from build_fasteners import screw
sw=connect(); path=ROOT/'ARM-D_Modular_parallel_gripper_DEVELOPMENT.SLDASM'
backup=ROOT/'development-debug/before-clearance-corrections'; backup.mkdir(exist_ok=True)
shutil.copy2(path,backup/path.name)
partpath=ROOT/'parts/ARM-202_Yaw_platform.SLDPRT'; shutil.copy2(partpath,backup/partpath.name)
doc=sw.OpenDoc6(str(path),2,1,'',integer_ref(),integer_ref())
if call(doc,'GetSaveFlag'): call(doc,'Save3',1,integer_ref(),integer_ref())
sw.CloseDoc(str(path))
sw.CommandInProgress=True
try:
    p=inherited(sw,'ARM-202_Yaw_platform','ARM-202_Yaw_platform')
    p.sketch('Captured_M3_nyloc_hex_pockets_AF5p7','Top Plane')
    for x,y in [(x,y) for x in (-32,32) for y in (-8,8)]:
        r=5.7/math.sqrt(3)
        pts=[(x+r*math.cos(math.radians(30+i*60)),y+r*math.sin(math.radians(30+i*60))) for i in range(6)]
        for v,w in zip(pts,pts[1:]+pts[:1]): p.sk.CreateLine(v[0]/1000,v[1]/1000,0.,w[0]/1000,w[1]/1000,0.)
    p.extrude('Recess_nuts_3mm_above_platform_underside',3,True,72,through=False)
    p.sketch('Recessed_small_series_washer_seats','Top Plane')
    for x,y in [(x,y) for x in (-32,32) for y in (-8,8)]: p.circle(x,y,3.2)
    p.extrude('Washer_seats_above_captive_nuts',.5,True,74.5,through=False)
    report=p.save(); (ROOT/'platform-recess-build.json').write_text(json.dumps(report,indent=2))
    screw(sw,3,14)
    a=Assembly.__new__(Assembly); a.sw=sw; a.models={}
    a.doc=sw.OpenDoc6(str(path),2,1,'',integer_ref(),integer_ref())
    a.report=json.loads((ROOT/'assembly-build-report.json').read_text())
    replacement=ROOT/'hardware-reference/HW-S_M3x14_socket_ENVELOPE.SLDPRT'
    for old in ('HW-S_M3x20_socket_ENVELOPE','HW-S_M3x16_socket_ENVELOPE'):
        cs=list(call(a.doc,'GetComponents',False))
        c=next(c for c in cs if old in call(c,'GetPathName'))
        call(a.doc,'ClearSelection2',True); c.Select4(False,nothing(),False)
        if not call(a.doc,'ReplaceComponents2',str(replacement),'',True,0,True): raise RuntimeError('Replacement failed '+old)
        candidates=[c for c in call(a.doc,'GetComponents',False) if call(c,'GetPathName').lower()==str(replacement).lower()]
        for row in a.report['components']:
            if old not in row['file']: continue
            c=next(c for c in candidates if max(abs(v*1000-w) for v,w in zip(list(call(c.Transform2,'ArrayData'))[9:12],row['position_mm']))<.001)
            row['instance']=call(c,'Name2'); row['file']=str(replacement.relative_to(ROOT))
    cs={call(c,'Name2'):c for c in call(a.doc,'GetComponents',False)}
    a.components={r['key']:cs[r['instance']] for r in a.report['components']}
    for row in a.report['components']:
        key=row['key']
        if not key.startswith('upright_foot_') or not key.endswith(('_nut','_nut_washer')): continue
        f=a.doc.FeatureByName('Mount_'+key)
        if not call(f,'SetSuppression2',0,2,None): raise RuntimeError('Cannot free '+key)
        f.Name='Mount_'+key+'_superseded_height'
        row['position_mm'][1]+=3
        values=[row['rotation'][j][i] for i in range(3) for j in range(3)]+[v/1000 for v in row['position_mm']]+[1.,0.,0.,0.]
        a.components[key].Transform2=call(call(sw,'GetMathUtility'),'CreateTransform',win32com.client.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_R8,values))
        a.report['mates']=[m for m in a.report['mates'] if m['name']!='Mount_'+key]
        a.rigid('Mount_'+key,'yaw',key)
    for stack in a.report['fastener_stacks']:
        if stack['label'].startswith('upright_foot_'):
            stack.update(length_mm=14,grip_mm=8,thread_protrusion_mm=1,nut_recess_mm=3)
        elif stack['label'].startswith('tool_adapter_'):
            stack.update(length_mm=14,thread_protrusion_mm=1)
    a.save()
finally: sw.CommandInProgress=False
