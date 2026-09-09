"""Save and close only this task's revision documents; preserve unsaved debug work."""
from datetime import datetime
from pathlib import Path
import shutil
from build_native import ROOT,connect,call,integer_ref,nothing
sw=connect()
allowed=[ROOT.resolve(),(ROOT.parent/'arm-v1').resolve()]
backup=ROOT/'development-debug'/datetime.now().strftime('%Y%m%d-%H%M%S')
backup.mkdir(parents=True,exist_ok=False)
docs=[]
d=call(sw,'GetFirstDocument')
while d:
    docs.append(d)
    d=call(d,'GetNext')
targets=[]
for d in docs:
    path=call(d,'GetPathName')
    title=call(d,'GetTitle')
    if not path and title in ('Part15','Assem1'):
        suffix='.SLDASM' if call(d,'GetType')==2 else '.SLDPRT'
        path=str(backup/(title+suffix))
        err,warn=integer_ref(),integer_ref()
        if not d.Extension.SaveAs(path,0,1,nothing(),err,warn) or err.value:
            raise RuntimeError('Could not preserve debug document: '+title)
    elif path and any(Path(path).resolve().is_relative_to(root) for root in allowed):
        if call(d,'GetSaveFlag'):
            shutil.copy2(path,backup/(Path(path).parent.name+'_'+Path(path).name))
            err,warn=integer_ref(),integer_ref()
            if not call(d,'Save3',1,err,warn) or err.value:
                raise RuntimeError('Could not save '+path)
    else:
        continue
    if call(d,'GetSaveFlag'):
        raise RuntimeError('Still unsaved; will not close '+path)
    targets.append((call(d,'GetType'),path))
for kind,path in sorted(targets,reverse=True):
    sw.CloseDoc(path)
    print('Closed saved document:',path,flush=True)
