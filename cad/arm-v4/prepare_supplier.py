"""Save the supplier's two unique solids locally and inspect mounting cylinders."""
import json
from build_native import ROOT,connect,call,integer_ref,nothing
sw=connect(); doc=call(sw,'ActiveDoc'); rows=[]; saved=set()
for c in call(doc,'GetComponents',False):
    model=call(c,'GetModelDoc2')
    if call(model,'GetType')!=1: continue
    title=call(model,'GetTitle')
    is_body='assembled_gripper' in title
    name='HW-202_Pololu3551_body' if is_body else 'HW-203_Pololu3551_jaw'
    transform=list(call(c.Transform2,'ArrayData'))
    row={'key':name,'instance':call(c,'Name2'),'transform':transform,'cylinders':[]}
    if name not in saved:
        for body in call(model,'GetBodies2',0,False) or []:
            for face in call(body,'GetFaces') or []:
                surf=call(face,'GetSurface')
                if call(surf,'IsCylinder'):
                    values=list(call(surf,'CylinderParams'))
                    if abs(values[6]*1000-2.1)<.01:
                        row['cylinders'].append({'params':values,'box_mm':[v*1000 for v in call(face,'GetBox')]})
        err,warn=integer_ref(),integer_ref()
        if not model.Extension.SaveAs(str(ROOT/'hardware-reference'/(name+'.SLDPRT')),0,1,nothing(),err,warn): raise RuntimeError('Save failed')
        saved.add(name)
        row['body_count']=len(call(model,'GetBodies2',0,False) or [])
    rows.append(row)
(ROOT/'supplier-mounting-inspection.json').write_text(json.dumps(rows,indent=2))
# Preserve the imported display assembly with local native references, bottom-up.
for c in call(doc,'GetComponents',False):
    model=call(c,'GetModelDoc2')
    if call(model,'GetType')==2:
        model.Extension.SaveAs(str(ROOT/'hardware-reference/HW-201a_Pololu3551_import.SLDASM'),0,1,nothing(),integer_ref(),integer_ref())
doc.Save3(1,integer_ref(),integer_ref())
print(json.dumps(rows),flush=True)
# Close supplier documents so subsequent modeling uses little memory.
sw.CloseDoc(call(doc,'GetPathName'))
sw.CloseDoc(str(ROOT/'hardware-reference/HW-201a_Pololu3551_import.SLDASM'))
for name in saved: sw.CloseDoc(str(ROOT/'hardware-reference'/(name+'.SLDPRT')))
