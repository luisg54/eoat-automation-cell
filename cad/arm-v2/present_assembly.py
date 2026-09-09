"""Apply readable component appearances and export native CAD views for review."""
import json
from build_native import ROOT,connect,call,integer_ref,nothing,pythoncom,win32com
sw=connect(); path=ROOT/'ARM-B_Articulated_prototype_DEVELOPMENT.SLDASM'
doc=sw.OpenDoc6(str(path),2,1,'',integer_ref(),integer_ref())
if doc is None: raise RuntimeError('Assembly did not open')
sw.ActivateDoc3(str(path),True,0,integer_ref())
report=json.loads((ROOT/'assembly-build-report.json').read_text())
names={r['instance']:r for r in report['components']}
for c in call(doc,'GetComponents',False):
    row=names[call(c,'Name2')]; name=row['file']
    if 'TPU' in name: rgb=[.94,.45,.10]
    elif 'HW-003' in name: rgb=[.10,.23,.48]
    elif 'HW-004' in name: rgb=[.13,.15,.17]
    elif 'stock_horn' in name: rgb=[.85,.76,.47]
    elif 'HW-' in name: rgb=[.64,.67,.71]
    elif row['key'] in ('base','yaw_servo_cassette'): rgb=[.24,.29,.34]
    else: rgb=[.06,.46,.59]
    values=win32com.client.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_R8,rgb+[.35,.8,.25,.25,0.,0.])
    call(c,'SetMaterialPropertyValues2',values,1,nothing())
    c.ComponentReference=row['key']
call(doc,'GraphicsRedraw2')
out=ROOT/'review-images'; out.mkdir(exist_ok=True)
for name,number in [('isometric',7),('front',1),('right',4)]:
    doc.ShowNamedView2('*'+name.capitalize(),number)
    call(doc,'ViewZoomtofit2'); call(doc,'GraphicsRedraw2')
    if not call(doc,'SaveBMP',str(out/(name+'.bmp')),1600,1000):
        raise RuntimeError('Native view export failed')
    print('Exported',name,flush=True)
doc.ShowNamedView2('*Isometric',7); call(doc,'ViewZoomtofit2')
if not call(doc,'Save3',1,integer_ref(),integer_ref()): raise RuntimeError('Assembly save failed')
