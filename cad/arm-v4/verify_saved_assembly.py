"""Verify saved poses, active mates, native part features and preserved C hashes."""
import json,hashlib
from check_motion import doc,sw,ROOT,call,pose,integer_ref,pythoncom,win32com
build=json.loads((ROOT/'assembly-build-report.json').read_text())
report={'status':'Native CAD verification; physical fit and performance tests remain','configurations':[]}
for p in json.loads((ROOT/'pose-configurations.json').read_text()):
    call(doc,'ShowConfiguration2',p['name']); call(doc,'ForceRebuild3',False)
    residual=pose(*p['pose_values'],command=False)
    errors=[]
    for m in build['mates']:
        f=doc.FeatureByName(m['name'])
        if f is None: raise RuntimeError('Missing mate '+m['name'])
        if call(f,'IsSuppressed2',1,None)[0]: continue
        warning=win32com.client.VARIANT(pythoncom.VT_BYREF|pythoncom.VT_BOOL,False)
        code=call(f,'GetErrorCode2',warning)
        if code: errors.append({'name':m['name'],'code':code})
    if errors: raise RuntimeError(str(errors))
    report['configurations'].append({'name':p['name'],'transform_residual':residual,'mate_errors':errors})
    print('Verified',p['name'],flush=True)
limits=json.loads((ROOT/'native-motion-limits.json').read_text())
call(doc,'ShowConfiguration2',limits['configuration']); call(doc,'ForceRebuild3',False)
for row in limits['limits']:
    f=doc.FeatureByName(row['name'])
    warning=win32com.client.VARIANT(pythoncom.VT_BYREF|pythoncom.VT_BOOL,False)
    if call(f,'IsSuppressed2',1,None)[0] or call(f,'GetErrorCode2',warning): raise RuntimeError('Invalid free-motion limit')
    if not call(doc.FeatureByName(row['name'].replace('_travel_limit','_command')),'IsSuppressed2',1,None)[0]: raise RuntimeError('Fixed command active in drag configuration')
report['free_arm_motion_limits_verified']=True
call(doc,'ShowConfiguration2','01_Home'); call(doc,'ForceRebuild3',False)
cs={call(c,'Name2'):c for c in call(doc,'GetComponents',False)}
if len(cs)!=len(build['components']): raise RuntimeError('Component count mismatch')
seen=set(); feature_errors=[]
for row in build['components']:
    c=cs[row['instance']]; model=call(c,'GetModelDoc2')
    path=ROOT/row['file']
    if model is None or call(model,'GetPathName').lower()!=str(path).lower(): raise RuntimeError('Wrong reference '+row['key'])
    if row['file'] in seen: continue
    seen.add(row['file'])
    if len(call(model,'GetBodies2',0,False) or [])!=1: raise RuntimeError('Part must contain one solid: '+str(path))
    f=call(model,'FirstFeature')
    while f:
        warning=win32com.client.VARIANT(pythoncom.VT_BYREF|pythoncom.VT_BOOL,False)
        code=call(f,'GetErrorCode2',warning)
        if code: feature_errors.append({'part':row['file'],'feature':call(f,'Name'),'code':code})
        f=call(f,'GetNextFeature')
if feature_errors: raise RuntimeError(str(feature_errors))
report.update(referenced_components_verified=len(cs),unique_parts_verified=len(seen),part_feature_errors=feature_errors)
inspection=json.loads((ROOT/'user-revision-inspection.json').read_text())
for row in inspection['parts']:
    path=ROOT.parent/'arm-v3'/row['file']
    if hashlib.sha256(path.read_bytes()).hexdigest()!=row['sha256']: raise RuntimeError('C source changed: '+str(path))
report['original_C_files_unchanged']=len(inspection['parts'])
if not call(doc,'Save3',1,integer_ref(),integer_ref()): raise RuntimeError('Save failed')
(ROOT/'saved-assembly-verification.json').write_text(json.dumps(report,indent=2))
print('Verified native references, part features and preserved user C files',flush=True)
