"""Expose one native opening variable so the two paddle positions stay symmetric."""
import json,shutil
from build_native import ROOT,connect,call,integer_ref
sw=connect(); path=ROOT/'ARM-D_Modular_parallel_gripper_DEVELOPMENT.SLDASM'
doc=sw.OpenDoc6(str(path),2,1,'',integer_ref(),integer_ref())
cm=call(doc,'ConfigurationManager')
if doc.GetConfigurationByName('01_Home') is None:
    if call(cm,'AddConfiguration2','01_Home','Development home pose','',0,'','',True) is None: raise RuntimeError('Config creation failed')
call(doc,'ShowConfiguration2','01_Home')
eq=call(doc,'GetEquationMgr')
if call(eq,'GetCount'):
    shutil.copy2(path,ROOT/'development-debug/D_before_equation_repair.SLDASM')
    for i in reversed(range(call(eq,'GetCount'))):
        text=eq._oleobj_.Invoke(eq._oleobj_.GetIDsOfNames('Equation'),0,2,True,i)
        if 'Gripper_opening' not in text: raise RuntimeError('Unexpected user equation')
        if call(eq,'Delete',i)<0: raise RuntimeError('Cannot remove malformed generated equation')
equations=['"Gripper_opening" = 32mm','"D1@jaw_right_half_opening" = "Gripper_opening" / 2','"D1@jaw_left_half_opening" = "Gripper_opening" / 2']
for text in equations:
    index=call(eq,'Add3',-1,text,False,2,None)
    if index<0: raise RuntimeError('Equation failed '+text)
call(eq,'EvaluateAll'); call(doc,'EditRebuild3')
if not call(doc,'Save3',1,integer_ref(),integer_ref()): raise RuntimeError('Save failed')
actual=[eq._oleobj_.Invoke(eq._oleobj_.GetIDsOfNames('Equation'),0,2,True,i) for i in range(call(eq,'GetCount'))]
(ROOT/'gripper-equations.json').write_text(json.dumps({'index_policy':'Find by left-hand-side name; SolidWorks may reorder equations','equations':actual,'range_mm':[0,32]},indent=2))
print(actual,flush=True)
print('Saved symmetric jaws driven by Gripper_opening',flush=True)
