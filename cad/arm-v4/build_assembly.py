"""Native, articulated SolidWorks assembly with physical reference components.

Development assembly: component transforms establish the initial pose; native
concentric and axial mates retain yaw/shoulder/elbow/gripper rotation.
"""
import math
import json
import sys
from pathlib import Path
from build_native import ROOT, connect, call, methods, nothing, integer_ref, pythoncom, win32com
from build_arm_parts import SG_EAR_TOP, SG_LINK_OFFSET, SG_CAP_RECESS, YAW_EAR_TOP, ELBOW_BEARING_OFFSET

from build_gripper_mount import G_POS,G_ROT,PIN_POINTS,MOUNT_POINTS
SG_LINK_OFFSET=20.5
ELBOW_BEARING_OFFSET=36

TEMPLATE=r'C:\ProgramData\SolidWorks\SOLIDWORKS 2024\templates\Assembly.ASMDOT'

def rotation_z(deg):
    c,s=math.cos(math.radians(deg)),math.sin(math.radians(deg))
    return [[c,-s,0],[s,c,0],[0,0,1]]

def compose(a,b):
    return [[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]

def point(r,p,t=(0,0,0)):
    return [sum(r[i][j]*p[j] for j in range(3))+t[i] for i in range(3)]

I=rotation_z(0)
TOP=[[1,0,0],[0,0,1],[0,-1,0]]

class Assembly:
    def __init__(self):
        self.sw=connect()
        self.existing=[]
        if '--resume-partial' in sys.argv:
            self.doc=self.sw.OpenDoc6(str(ROOT/'development-debug/D_partial_insertion.SLDASM'),2,1,'',integer_ref(),integer_ref())
            if self.doc is None: raise RuntimeError('Cannot reopen preserved partial assembly')
            self.existing=list(call(self.doc,'GetComponents',False) or [])
        else:
            self.doc=self.sw.NewDocument(TEMPLATE,0,0,0)
        methods(self.doc,['AddComponent5','AddMate5','FixComponent','UnfixComponent','ClearSelection2','EditRebuild3','ForceRebuild3'])
        self.components={}
        self.models={}
        self.report={'status':'DEVELOPMENT: motion and interference verification outstanding','components':[],'mates':[]}

    def activate(self):
        self.sw.ActivateDoc3(call(self.doc,'GetTitle'),True,0,integer_ref())

    def add(self,key,filename,pos=(0,0,0),rotation=I,hardware=False):
        path=ROOT/('hardware-reference' if hardware else 'parts')/(filename+'.SLDPRT')
        if not path.is_file():
            raise FileNotFoundError(path)
        expected=[rotation[j][i] for i in range(3) for j in range(3)]+[x/1000 for x in pos]+[1.,0.,0.,0.]
        for index,c in enumerate(self.existing):
            if call(c,'GetPathName').lower()!=str(path).lower(): continue
            actual=list(call(c.Transform2,'ArrayData'))
            if max(abs(x-y) for x,y in zip(actual,expected))>1e-6: continue
            self.existing.pop(index)
            self.components[key]=c
            self.models[str(path)]=call(c,'GetModelDoc2')
            self.report['components'].append({'key':key,'instance':call(c,'Name2'),'file':str(path.relative_to(ROOT)), 'position_mm':pos,'rotation':rotation})
            return c
        err,warn=integer_ref(),integer_ref()
        model=self.models.get(str(path))
        if model is None:
            model=self.sw.OpenDoc6(str(path),1,1,'',err,warn)
            self.models[str(path)]=model
        if model is None:
            raise RuntimeError(f'Open failed {path}: {err.value}')
        self.activate()
        c=self.doc.AddComponent5(str(path),0,'',False,'',0.,0.,0.)
        if c is None:
            raise RuntimeError('Component insertion failed '+key)
        # SolidWorks MathTransform stores local basis vectors (columns) in rows.
        data=[rotation[j][i] for i in range(3) for j in range(3)]
        data += [x/1000 for x in pos]+[1.,0.,0.,0.]
        mu=call(self.sw,'GetMathUtility')
        transform_data=win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8,data)
        c.Transform2=call(mu,'CreateTransform',transform_data)
        self.components[key]=c
        self.report['components'].append({'key':key,'instance':call(c,'Name2'),'file':str(path.relative_to(ROOT)), 'position_mm':pos,'rotation':rotation})
        print('Added',key,flush=True)
        return c

    def plane(self,key,name):
        c=self.components[key]
        p=call(c,'GetModelDoc2')
        f=p.FeatureByName(name)
        if f is None:
            raise RuntimeError('Missing plane '+name)
        return c.GetCorresponding(f)

    def cylinder(self,key,radius):
        c=self.components[key]
        p=call(c,'GetModelDoc2')
        candidates=[]
        for body in call(p,'GetBodies2',0,False) or []:
            for face in call(body,'GetFaces') or []:
                surf=call(face,'GetSurface')
                if call(surf,'IsCylinder'):
                    params=call(surf,'CylinderParams')
                    if abs(params[6]*1000-radius)<.005:
                        candidates.append((call(face,'GetArea'),face))
        if not candidates:
            raise RuntimeError(f'No cylinder on {key} with radius {radius}')
        return c.GetCorresponding(max(candidates,key=lambda x:x[0])[1])

    def mate(self,name,kind,a,b,distance=0,alignment=0,flip=False):
        d=self.doc
        d.ClearSelection2(True)
        if not a.Select2(False,1) or not b.Select2(True,1):
            raise RuntimeError('Mate selections failed: '+name)
        err=integer_ref()
        m=d.AddMate5(kind,alignment,flip,distance/1000,0.,0.,0.,0.,0.,0.,0.,False,False,0,err)
        if m is None or err.value != 1:
            raise RuntimeError(f'Mate failed {name}: {err.value}')
        m.Name=name
        d.ClearSelection2(True)
        self.report['mates'].append({'name':name,'type':kind,'error':err.value})
        print('Mated',name,flush=True)

    def rigid(self,name,a,b):
        # Lock mate on components preserves their current relative transform.
        d=self.doc
        call(d,'ClearSelection2',True)
        data=call(d,'CreateMateData',16)
        data.EntitiesToMate=win32com.client.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_DISPATCH,
                                                   [self.components[a],self.components[b]])
        m=call(d,'CreateMate',data)
        if m is None:
            raise RuntimeError(f'Rigid mate failed {name}')
        m.Name=name
        d.ClearSelection2(True)
        self.report['mates'].append({'name':name,'type':'lock','parent':a,'child':b,'creation_api':'CreateMateData/CreateMate'})

    def joint(self,name,driven,axis_part,r_driven,r_axis,plane_part,offset):
        self.mate(name+'_axis',1,self.cylinder(driven,r_driven),self.cylinder(axis_part,r_axis))
        self.mate(name+'_axial',5 if offset else 0,self.plane(plane_part,'Front Plane'),
                  self.plane(driven,'Front Plane'),offset)

    def save(self):
        call(self.doc,'EditRebuild3')
        self.doc.ShowNamedView2('*Isometric',7)
        call(self.doc,'ViewZoomtofit2')
        err,warn=integer_ref(),integer_ref()
        path=ROOT/'ARM-D_Modular_parallel_gripper_DEVELOPMENT.SLDASM'
        ok=self.doc.Extension.SaveAs(str(path),0,1,nothing(),err,warn)
        if not ok or err.value:
            raise RuntimeError(f'Assembly save failed: {err.value}, {warn.value}')
        self.report['assembly']=str(path)
        (ROOT/'assembly-build-report.json').write_text(json.dumps(self.report,indent=2))
        for model_path in self.models:
            self.sw.CloseDoc(model_path)
        print('SAVED',path,flush=True)

def main():
    a=Assembly()
    a.add('base','ARM-001_Base_pedestal')
    a.add('yaw','ARM-202_Yaw_platform')
    a.add('collar','ARM-003_Yaw_D_drive_collar')
    a.add('yaw_servo','HW-003_SG90_NOMINAL_VERIFY',(0,YAW_EAR_TOP,0),TOP,True)
    a.add('yaw_bearing_low','HW-001_608ZZ_22x8x7_ENVELOPE',(0,48,0),TOP,True)
    a.add('yaw_bearing_high','HW-001_608ZZ_22x8x7_ENVELOPE',(0,63,0),TOP,True)
    a.add('shoulder_servo','HW-004_MG996R_NOMINAL_VERIFY',(0,122,7),I,True)
    shoulder=rotation_z(45)
    upper_origin=(0,122,20.5)
    a.add('upper','ARM-201_Upper_link_dual_MG996R',upper_origin,shoulder)
    elbow=point(shoulder,(60,0,0),upper_origin)
    elbow_servo=point(shoulder,(60,0,7),upper_origin)
    a.add('elbow_servo','HW-004_MG996R_NOMINAL_VERIFY',elbow_servo,shoulder,True)
    forearm_rotation=rotation_z(0)
    forearm_origin=[elbow[0],elbow[1],elbow[2]+SG_LINK_OFFSET]
    a.add('forearm','ARM-204_Modular_forearm_MG996R',forearm_origin,forearm_rotation)
    attachments=[]
    def attached(key,filename,parent,pos,rotation=I,hardware=False):
        a.add(key,filename,pos,rotation,hardware)
        attachments.append((key,parent))
    attached('yaw_servo_cassette','ARM-004_Removable_yaw_servo_mount','base',(0,0,0))
    attached('upright','ARM-203_Bolted_shoulder_upright','yaw',(0,0,0))
    attached('yaw_horn','HW-005_SG90_COMPACT_CROSS_REFERENCE','yaw',(0,39.5,0),TOP,True)
    attached('shoulder_horn','HW-006_MG996_25T_D20_PCD14_HORN','upper',(0,122,18.5),shoulder,True)
    attached('elbow_horn','HW-006_MG996_25T_D20_PCD14_HORN','forearm',point(forearm_rotation,(0,0,-2),forearm_origin),forearm_rotation,True)
    attached('yaw_horn_cap','ARM-112_SG90_horn_capture_cap','yaw',(0,37.35,0),TOP)
    attached('shoulder_cheek','ARM-105_Shoulder_bearing_cheek','yaw',(0,122,36))
    attached('shoulder_bearing','HW-001_608ZZ_22x8x7_ENVELOPE','yaw',(0,122,36),I,True)
    attached('shoulder_keeper','ARM-109_Bearing_and_dowel_keeper','yaw',(0,122,43.2))
    attached('shoulder_pin','HW-002_Dowel_6p35x25p4','upper',(0,122,23.5),I,True)
    for i,z in enumerate((20.5,36)):
        attached('shoulder_sleeve_'+str(i),'ARM-107_Dowel_to_608_adapter','upper',(0,122,z))
    for i,y in enumerate((104,140)):
        attached('shoulder_standoff_'+str(i),'ARM-108_M3_standoff_32mm','yaw',(-36,y,4))
    attached('elbow_cheek','ARM-104_Elbow_bearing_cheek','upper',
             point(shoulder,(60,0,ELBOW_BEARING_OFFSET),upper_origin),shoulder)
    attached('elbow_bearing','HW-001_608ZZ_22x8x7_ENVELOPE','upper',
             point(shoulder,(60,0,ELBOW_BEARING_OFFSET),upper_origin),shoulder,True)
    attached('elbow_keeper','ARM-109_Bearing_and_dowel_keeper','upper',
             point(shoulder,(60,0,ELBOW_BEARING_OFFSET+7.2),upper_origin),shoulder)
    attached('elbow_pin','HW-002_Dowel_6p35x25p4','forearm',
             point(forearm_rotation,(0,0,3),forearm_origin),forearm_rotation,True)
    for i,z in enumerate((SG_LINK_OFFSET,ELBOW_BEARING_OFFSET)):
        attached('elbow_sleeve_'+str(i),'ARM-107_Dowel_to_608_adapter','forearm',
                 point(shoulder,(60,0,z),upper_origin),shoulder)
    for i,y in enumerate((-9,9)):
        attached('elbow_standoff_'+str(i),'ARM-108_M3_standoff_32mm','upper',
                 point(shoulder,(35,y,4),upper_origin),shoulder)
    attached('gripper_adapter','ARM-205_Parallel_gripper_fork_adapter','forearm',forearm_origin,forearm_rotation)
    supplier=json.loads((ROOT/'supplier-mounting-inspection.json').read_text())
    jaw_index=0
    for row in supplier:
        data=row['transform']
        sr=[[data[j*3+i] for j in range(3)] for i in range(3)]
        sp=[x*1000 for x in data[9:12]]
        rot=compose(forearm_rotation,compose(G_ROT,sr))
        pos=point(forearm_rotation,point(G_ROT,sp,G_POS),forearm_origin)
        if 'body' in row['key']:
            attached('gripper_body',row['key'],'forearm',pos,rot,True)
        else:
            key='jaw_right' if jaw_index==0 else 'jaw_left'; jaw_index+=1
            a.add(key,row['key'],pos,rot,True)
    for i,(x,z) in enumerate(PIN_POINTS):
        attached('gripper_crush_spacer_'+str(i),'ARM-206_Gripper_lug_crush_spacer_13mm','forearm',point(forearm_rotation,(x,-6.5,z),forearm_origin),compose(forearm_rotation,TOP))
    # Real screw/nut envelopes, grouped rigidly with the supported structure.
    # All stacks use local +Z for the head and local -Z for the screw shank.
    a.report['fastener_stacks']=[]
    def stack(label,parent,origin,rot,xy,top,bottom,d,length,nyloc=False):
        nut_height=({2.5:3.5,3:4,4:5}[d] if nyloc else {2:1.6,2.5:2.,3:2.4,4:3.2}[d])
        nut_kind='nyloc' if nyloc else 'hex'
        items=[('screw',f'HW-S_M{d}x{length}_socket_ENVELOPE',top+.5),
               ('head_washer',f'HW-W_M{d}_washer_0p5_ENVELOPE',top),
               ('nut_washer',f'HW-W_M{d}_washer_0p5_ENVELOPE',bottom-.5),
               ('nut',f'HW-N_M{d}_{nut_kind}_ENVELOPE',bottom-.5-nut_height)]
        for suffix,filename,z in items:
            item_rot=compose(rot,rotation_z(30)) if suffix=='nut' and d==3 else rot
            attached(label+'_'+suffix,filename,parent,point(rot,(*xy,z),origin),item_rot,True)
        a.report['fastener_stacks'].append({'label':label,'parent':parent,'diameter_mm':d,
            'length_mm':length,'nut':nut_kind,'grip_mm':top-bottom,
            'thread_protrusion_mm':length-(top-bottom+1+nut_height)})
    for label,parent,origin,rot in [('yaw_servo','base',(0,YAW_EAR_TOP,0),TOP)]:
        for i,x in enumerate((-9,20)):
            stack(label+'_mount_'+str(i),parent,origin,rot,(x,0),0,-SG_EAR_TOP,2,10)
    for role,parent,origin,rot in [('shoulder','yaw',(0,122,7),I),('elbow','upper',elbow_servo,shoulder)]:
        for i,xy in enumerate([(-13,-5),(-13,5),(34,-5),(34,5)]):
            stack(role+'_servo_mount_'+str(i),parent,origin,rot,xy,0,-7,2.5,14,True)
    for i,xy in enumerate([(x,z) for x in (-32,32) for z in (-8,8)]):
        stack('upright_foot_'+str(i),'yaw',(0,0,0),TOP,xy,83,75,3,14,True)
    for i,xy in enumerate(MOUNT_POINTS):
        stack('tool_adapter_'+str(i),'forearm',forearm_origin,forearm_rotation,xy,8,0,3,14,True)
    for i,(x,z) in enumerate(PIN_POINTS):
        stack('gripper_pin_'+str(i),'forearm',point(forearm_rotation,(x,0,z),forearm_origin),compose(forearm_rotation,TOP),(0,0),14.2,-14.2,4,35,True)
    for i,y in enumerate((-18,18)):
        stack('shoulder_support_'+str(i),'yaw',(0,122,36),I,(-36,y),4,-36,3,50,True)
    for i,y in enumerate((-9,9)):
        stack('elbow_support_'+str(i),'upper',point(shoulder,(60,0,ELBOW_BEARING_OFFSET),upper_origin),shoulder,
              (-25,y),4,-ELBOW_BEARING_OFFSET,3,50,True)
    for label,parent,origin,rot in [('shoulder','yaw',(0,122,36),I),
            ('elbow','upper',point(shoulder,(60,0,ELBOW_BEARING_OFFSET),upper_origin),shoulder)]:
        for i,xy in enumerate([(14,0),(0,-14),(0,14)]):
            stack(label+'_keeper_'+str(i),parent,origin,rot,xy,9.2,-1,2,14)
    for role,parent,origin,rot in [('shoulder','upper',upper_origin,shoulder),('elbow','forearm',forearm_origin,forearm_rotation)]:
        for i,xy in enumerate([(7,0),(-7,0),(0,7),(0,-7)]):
            label=role+'_horn_'+str(i)
            attached(label+'_screw','HW-S_M3x12_socket_ENVELOPE',parent,point(rot,(*xy,8.5),origin),rot,True)
            attached(label+'_head_washer','HW-W_M3_washer_0p5_ENVELOPE',parent,point(rot,(*xy,8),origin),rot,True)
            a.report['fastener_stacks'].append({'label':label,'parent':parent,'diameter_mm':3,'length_mm':12,
                'nut':'none; M3 tapped metal horn','printed_grip_mm':8,'metal_thread_engagement_mm':2,
                'thread_protrusion_past_horn_mm':1.5,'clearance_to_servo_case_front_mm':3})
    # Rear-facing low heads and front nuts capture each unmodified stock cross horn.
    reverse_z=[[1,0,0],[0,-1,0],[0,0,-1]]
    for role,parent,origin,rot,seat,front in [('yaw','yaw',(0,0,0),TOP,41,44)]:
        for i,xy in enumerate([(7,7),(-7,7),(-7,-7),(7,-7)]):
            label=role+'_horn_capture_'+str(i)
            attached(label+'_screw','HW-S_M2x10_LOW_HEAD_D4_H1p1_ENVELOPE',parent,
                     point(rot,(*xy,seat-3.65+SG_CAP_RECESS),origin),compose(rot,reverse_z),True)
            attached(label+'_washer','HW-W_M2_washer_0p5_ENVELOPE',parent,point(rot,(*xy,front),origin),rot,True)
            attached(label+'_nut','HW-N_M2_hex_ENVELOPE',parent,point(rot,(*xy,front+.5),origin),rot,True)
            a.report['fastener_stacks'].append({'label':label,'parent':parent,'diameter_mm':2,'length_mm':10,
                'head':'low profile D4 x1.1; rear side','nut':'M2 plain; front side','washer_count':1,
                'thread_protrusion_mm':seat-3.65+SG_CAP_RECESS+10-(front+2.1),
                'minimum_axial_cover_clearance_mm':13.2-3.65+SG_CAP_RECESS-1.1-8.8,
                'status':'Seated-horn height is assumed; physical clearance required'})
    cross=[[0,0,-1],[0,1,0],[1,0,0]]
    stack('yaw_retention_crossbolt','yaw',(0,45.5,0),cross,(0,0),6,-6,2,20)
    for i,z in enumerate((-12,12)):
        stack('cassette_mount_'+str(i),'base',(0,28,0),cross,(z,0),35,14,3,30,True)
    a.report['rigid_attachments']=attachments
    if a.existing: raise RuntimeError('Unexpected leftover components in resumed assembly')
    a.save()  # Durable insertion checkpoint before adding mates.
    for key,parent in attachments:
        a.rigid('Mount_'+key,parent,key)
    # Fix only the base. Native joints retain the intended rotational freedoms.
    a.doc.ClearSelection2(True)
    a.components['base'].Select4(False,nothing(),False)
    a.doc.FixComponent()
    a.doc.ClearSelection2(True)
    a.mate('J1_yaw_axis',1,a.cylinder('yaw',3.95),a.cylinder('base',11.1))
    a.mate('J1_yaw_height',0,a.plane('base','Top Plane'),a.plane('yaw','Top Plane'))
    for item,parent in [('collar','yaw'),('yaw_servo','base'),('yaw_bearing_low','base'),
                        ('yaw_bearing_high','base'),('shoulder_servo','yaw'),
                        ('elbow_servo','upper')]:
        a.rigid('Mount_'+item,parent,item)
    a.joint('J2_shoulder','upper','shoulder_servo',4,3,'yaw',20.5)
    a.joint('J3_elbow','forearm','elbow_servo',4,3,'upper',SG_LINK_OFFSET)
    for key in ('jaw_right','jaw_left'):
        row=next(r for r in a.report['components'] if r['key']==key)
        rel=[row['position_mm'][i]-forearm_origin[i] for i in range(3)]
        a.mate(key+'_height',5,a.plane('forearm','Front Plane'),a.plane(key,'Front Plane'),abs(rel[2]),2)
        a.mate(key+'_reach',5,a.plane('forearm','Right Plane'),a.plane(key,'Top Plane'),abs(rel[0]),2)
        a.mate(key+'_half_opening',5,a.plane('forearm','Top Plane'),a.plane(key,'Right Plane'),abs(rel[1]),2,key=='jaw_right')
    a.save()

if __name__=='__main__':
    sw=connect(); visible=sw.GetDocumentVisible(1)
    try:
        sw.CommandInProgress=True
        sw.DocumentVisible(False,1)
        main()
    finally:
        sw.DocumentVisible(visible,1)
        sw.CommandInProgress=False
