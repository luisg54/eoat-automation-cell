"""Preserve the supplier jaw handedness when mating imported reference planes."""
import json,shutil
from build_assembly import Assembly,ROOT,connect,call,integer_ref,pythoncom,win32com
a=Assembly.__new__(Assembly); a.sw=connect(); a.models={}
path=ROOT/'ARM-D_Modular_parallel_gripper_DEVELOPMENT.SLDASM'
shutil.copy2(path,ROOT/'development-debug/D_before_jaw_alignment.SLDASM')
a.doc=a.sw.OpenDoc6(str(path),2,1,'',integer_ref(),integer_ref())
a.report=json.loads((ROOT/'assembly-build-report.json').read_text())
cs={call(c,'Name2'):c for c in call(a.doc,'GetComponents',False)}
a.components={r['key']:cs[r['instance']] for r in a.report['components']}
rows={r['key']:r for r in a.report['components']}
for key in ('jaw_right','jaw_left'):
    for suffix in ('height','reach','half_opening'):
        name=key+'_'+suffix; f=a.doc.FeatureByName(name)
        if f is None: raise RuntimeError('Missing '+name)
        if not call(f,'SetSuppression2',0,2,None): raise RuntimeError('Could not suppress '+name)
        f.Name=name+'_superseded_alignment'
        a.report['mates']=[r for r in a.report['mates'] if r['name']!=name]
for key in ('jaw_right','jaw_left'):
    row=rows[key]; r=row['rotation']; p=row['position_mm']
    values=[r[j][i] for i in range(3) for j in range(3)]+[v/1000 for v in p]+[1.,0.,0.,0.]
    a.components[key].Transform2=call(call(a.sw,'GetMathUtility'),'CreateTransform',win32com.client.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_R8,values))
    rel=[p[i]-rows['forearm']['position_mm'][i] for i in range(3)]
    for suffix,first,second,distance in [('height','Front Plane','Front Plane',rel[2]),('reach','Right Plane','Top Plane',rel[0]),('half_opening','Top Plane','Right Plane',abs(rel[1]))]:
        call(a.doc,'ClearSelection2',True)
        a.plane('forearm',first).Select2(False,1); a.plane(key,second).Select2(True,1)
        err=integer_ref()
        mate=a.doc.AddMate5(5,2,False,distance/1000,0.,0.,0.,0.,0.,0.,0.,False,False,0,err)
        if mate is None or err.value!=1: raise RuntimeError('Jaw mate failed '+str(err.value))
        mate.Name=key+'_'+suffix
        a.report['mates'].append({'name':key+'_'+suffix,'type':5,'alignment':'closest preserves supplier handedness','error':1})
a.save()
