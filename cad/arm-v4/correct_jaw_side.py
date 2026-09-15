"""Put the right paddle on the negative half of the parallel jaw opening."""
import json
from build_assembly import Assembly,ROOT,connect,call,integer_ref
a=Assembly.__new__(Assembly); a.sw=connect(); a.models={}
path=ROOT/'ARM-D_Modular_parallel_gripper_DEVELOPMENT.SLDASM'
a.doc=a.sw.OpenDoc6(str(path),2,1,'',integer_ref(),integer_ref())
a.report=json.loads((ROOT/'assembly-build-report.json').read_text())
cs={call(c,'Name2'):c for c in call(a.doc,'GetComponents',False)}
a.components={r['key']:cs[r['instance']] for r in a.report['components']}
f=a.doc.FeatureByName('jaw_right_half_opening')
if not call(f,'SetSuppression2',0,2,None): raise RuntimeError('Cannot suppress jaw mate')
f.Name='jaw_right_half_opening_superseded_side'
call(a.doc,'ClearSelection2',True)
a.plane('forearm','Top Plane').Select2(False,1)
a.plane('jaw_right','Right Plane').Select2(True,1)
err=integer_ref()
mate=a.doc.AddMate5(5,2,True,.016,0.,0.,0.,0.,0.,0.,0.,False,False,0,err)
if err.value!=1: raise RuntimeError('Cannot flip distance mate '+str(err.value))
mate.Name='jaw_right_half_opening'
a.save()
