"""Run native operations serially with reduced out-of-process UI updates."""
import sys,runpy
from build_native import ROOT,connect,call,integer_ref
sw=connect(); jobs=sys.argv[1:]; prior=sw.CommandInProgress
try:
    sw.CommandInProgress=True
    for job in jobs:
        name,*args=job.split(':')
        if name=='close_assembly':
            path=ROOT/'ARM-D_Modular_parallel_gripper_DEVELOPMENT.SLDASM'
            doc=sw.GetOpenDocumentByName(str(path))
            if doc is not None:
                if not call(doc,'Save3',1,integer_ref(),integer_ref()): raise RuntimeError('Save before close failed')
                sw.CloseDoc(str(path))
            continue
        sys.argv=[str(ROOT/(name+'.py'))]+args
        sys.modules.pop('check_motion',None)
        print('STAGE',name,flush=True)
        runpy.run_path(sys.argv[0],run_name='__main__')
finally: sw.CommandInProgress=prior
