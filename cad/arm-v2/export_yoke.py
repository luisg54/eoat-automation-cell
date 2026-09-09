from build_native import ROOT,connect,call,integer_ref,nothing
sw=connect()
path=ROOT/'parts/ARM-002_Yaw_platform_and_shoulder_mount.SLDPRT'
d=sw.OpenDoc6(str(path),1,1,'',integer_ref(),integer_ref())
if d is None or call(d,'GetType')!=1: raise RuntimeError('Expected native part')
sw.ActivateDoc3(str(path),True,0,integer_ref())
if call(call(sw,'ActiveDoc'),'GetPathName').lower()!=str(path).lower():
    raise RuntimeError('Part is not active; export stopped')
for suffix in ('.step','.stl'):
    err,warn=integer_ref(),integer_ref()
    if not d.Extension.SaveAs(str(path.with_suffix(suffix)),0,1,nothing(),err,warn) or err.value:
        raise RuntimeError('Export failed')
    print('Exported',path.with_suffix(suffix),flush=True)
sw.CloseDoc(str(path))
