"""Add a separate native drag configuration with provisional joint angle limits."""
import json,math,shutil
from datetime import datetime
from build_native import ROOT,connect,call,integer_ref,pythoncom,win32com
sw=connect(); path=ROOT/'ARM-D_Modular_parallel_gripper_DEVELOPMENT.SLDASM'
backup=ROOT/'development-debug'/('before-limited-motion-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir(parents=True); shutil.copy2(path,backup/path.name)
doc=sw.OpenDoc6(str(path),2,1,'',integer_ref(),integer_ref())
cm=call(doc,'ConfigurationManager'); name='07_Free_motion_CHECK_COLLISIONS'
if doc.GetConfigurationByName(name) is None:
 call(cm,'AddConfiguration2',name,'Provisional angular bounds; arbitrary combinations and physical servo limits are unverified','',0,'','Free articulation with limit mates',True)
call(doc,'ShowConfiguration2',name)
commands=[('J1_Yaw_command',30,150),('J2_Shoulder_command',75,170),
          ('J3_Elbow_command',5,100)]
build=json.loads((ROOT/'assembly-build-report.json').read_text())
instances={r['key']:r['instance'] for r in build['components']}
components={call(c,'Name2'):c for c in call(doc,'GetComponents',False)}
refs={'J1_Yaw_command':('base','Top Plane'),'J2_Shoulder_command':('yaw','Front Plane'),
      'J3_Elbow_command':('upper','Front Plane')}
rows=[]
try:
 for command,low,high in commands:
  f=doc.FeatureByName(command)
  if not call(f,'SetSuppression2',0,1,None): raise RuntimeError('Could not release '+command)
 for command,low,high in commands:
  limit_name=command.replace('_command','_travel_limit')
  f=doc.FeatureByName(limit_name)
  if f is None:
   definition=call(doc.FeatureByName(command),'GetDefinition')
   data=call(doc,'CreateMateData',6)
   data.EntitiesToMate=win32com.client.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_DISPATCH,call(definition,'EntitiesToMate'))
   key,plane=refs[command]; c=components[instances[key]]
   ref=c.GetCorresponding(call(c,'GetModelDoc2').FeatureByName(plane))
   call(doc,'ClearSelection2',True)
   if not ref.Select2(False,67108864): raise RuntimeError('Direction reference selection failed')
   data.ReferenceEntity=call(doc.SelectionManager,'GetSelectedObject6',1,67108864)
   data.MateAlignment=call(definition,'MateAlignment')
   data.IsAdvancedMate=True; data.Angle=call(definition,'Angle')
   data.MinimumAngle=math.radians(low); data.MaximumAngle=math.radians(high)
   f=call(doc,'CreateMate',data)
   if f is None: raise RuntimeError('Could not create '+limit_name)
   f.Name=limit_name
  if not call(f,'SetSuppression2',0,2,None): raise RuntimeError('Could not isolate '+limit_name)
  if not call(f,'SetSuppression2',1,1,None): raise RuntimeError('Could not enable '+limit_name)
  actual=call(f,'GetDefinition')
  row={'name':limit_name,'minimum_mate_angle_deg':math.degrees(call(actual,'MinimumAngle')),
       'maximum_mate_angle_deg':math.degrees(call(actual,'MaximumAngle'))}
  rows.append(row); print('Created',row,flush=True)
 call(doc,'EditRebuild3')
 for row in rows:
  warning=win32com.client.VARIANT(pythoncom.VT_BYREF|pythoncom.VT_BOOL,False)
  err=call(doc.FeatureByName(row['name']),'GetErrorCode2',warning)
  if err: raise RuntimeError('Limit mate error '+str(err))
 (ROOT/'native-motion-limits.json').write_text(json.dumps({'configuration':name,
  'status':'Native bounds verified; not a certification of all combined poses or actual servo travel','limits':rows},indent=2))
finally:
 call(doc,'ShowConfiguration2','01_Home'); call(doc,'EditRebuild3')
 if not call(doc,'Save3',1,integer_ref(),integer_ref()): raise RuntimeError('Could not save assembly')
