"""Native, articulated SolidWorks assembly with physical reference components.

Development assembly: component transforms establish the initial pose; native
concentric and axial mates retain yaw/shoulder/elbow/gripper rotation.
"""
import math
import json
from pathlib import Path
from build_native import ROOT, connect, call, methods, nothing, integer_ref, pythoncom, win32com

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
        self.doc=self.sw.NewDocument(TEMPLATE,0,0,0)
        methods(self.doc,['AddComponent5','AddMate5','FixComponent','UnfixComponent','ClearSelection2','EditRebuild3','ForceRebuild3'])
        self.components={}
        self.report={'status':'DEVELOPMENT: motion and interference verification outstanding','components':[],'mates':[]}

    def activate(self):
        self.sw.ActivateDoc3(call(self.doc,'GetTitle'),True,0,integer_ref())

    def add(self,key,filename,pos=(0,0,0),rotation=I,hardware=False):
        path=ROOT/('hardware-reference' if hardware else 'parts')/(filename+'.SLDPRT')
        if not path.is_file():
            raise FileNotFoundError(path)
        err,warn=integer_ref(),integer_ref()
        model=self.sw.OpenDoc6(str(path),1,1,'',err,warn)
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
        self.report['components'].append({'key':key,'file':str(path.relative_to(ROOT)), 'position_mm':pos})
        self.sw.CloseDoc(call(model,'GetTitle'))
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

    def mate(self,name,kind,a,b,distance=0):
        d=self.doc
        d.ClearSelection2(True)
        if not a.Select2(False,1) or not b.Select2(True,1):
            raise RuntimeError('Mate selections failed: '+name)
        err=integer_ref()
        m=d.AddMate5(kind,0,False,distance/1000,0.,0.,0.,0.,0.,0.,0.,False,False,0,err)
        if m is None or err.value not in (0,1):
            raise RuntimeError(f'Mate failed {name}: {err.value}')
        m.Name=name
        d.ClearSelection2(True)
        self.report['mates'].append({'name':name,'type':kind,'error':err.value})
        print('Mated',name,flush=True)

    def rigid(self,name,a,b):
        # Lock mate on components preserves their current relative transform.
        d=self.doc
        d.ClearSelection2(True)
        if not self.components[a].Select4(False,nothing(),False):
            raise RuntimeError('Component select failed '+a)
        if not self.components[b].Select4(True,nothing(),False):
            raise RuntimeError('Component select failed '+b)
        err=integer_ref()
        m=d.AddMate5(16,0,False,0.,0.,0.,0.,0.,0.,0.,0.,False,False,0,err)
        if m is None or err.value not in (0,1):
            raise RuntimeError(f'Rigid mate failed {name}: {err.value}')
        m.Name=name
        d.ClearSelection2(True)
        self.report['mates'].append({'name':name,'type':'lock','error':err.value})

    def joint(self,name,driven,axis_part,r_driven,r_axis,plane_part,offset):
        self.mate(name+'_axis',1,self.cylinder(driven,r_driven),self.cylinder(axis_part,r_axis))
        self.mate(name+'_axial',5 if offset else 0,self.plane(plane_part,'Front Plane'),
                  self.plane(driven,'Front Plane'),offset)

    def save(self):
        self.doc.EditRebuild3()
        self.doc.ShowNamedView2('*Isometric',7)
        call(self.doc,'ViewZoomtofit2')
        err,warn=integer_ref(),integer_ref()
        path=ROOT/'ARM-A_Articulated_prototype_DEVELOPMENT.SLDASM'
        ok=self.doc.Extension.SaveAs(str(path),0,1,nothing(),err,warn)
        if not ok or err.value:
            raise RuntimeError(f'Assembly save failed: {err.value}, {warn.value}')
        self.report['assembly']=str(path)
        (ROOT/'assembly-build-report.json').write_text(json.dumps(self.report,indent=2))
        print('SAVED',path,flush=True)

def main():
    a=Assembly()
    a.add('base','ARM-001_Base_pedestal')
    a.add('yaw','ARM-002_Yaw_platform_and_shoulder_mount')
    a.add('collar','ARM-003_Yaw_D_drive_collar')
    a.add('yaw_servo','HW-003_SG90_NOMINAL_VERIFY',(0,32,0),TOP,True)
    a.add('yaw_bearing_low','HW-001_608ZZ_22x8x7_ENVELOPE',(0,48,0),TOP,True)
    a.add('yaw_bearing_high','HW-001_608ZZ_22x8x7_ENVELOPE',(0,63,0),TOP,True)
    a.add('shoulder_servo','HW-004_MG996R_NOMINAL_VERIFY',(0,122,7),I,True)
    shoulder=rotation_z(45)
    upper_origin=(0,122,23)
    a.add('upper','ARM-101_Upper_link_60mm_MG996_SG90',upper_origin,shoulder)
    elbow=point(shoulder,(60,0,0),upper_origin)
    elbow_servo=point(shoulder,(60,0,4),upper_origin)
    a.add('elbow_servo','HW-003_SG90_NOMINAL_VERIFY',elbow_servo,shoulder,True)
    forearm_rotation=rotation_z(0)
    forearm_origin=[elbow[0],elbow[1],elbow[2]+15]
    a.add('forearm','ARM-102_Forearm_and_fixed_jaw',forearm_origin,forearm_rotation)
    grip_servo=point(forearm_rotation,(45,18,4),forearm_origin)
    a.add('grip_servo','HW-003_SG90_NOMINAL_VERIFY',grip_servo,forearm_rotation,True)
    jaw_origin=point(forearm_rotation,(45,18,0),forearm_origin)
    a.add('jaw','ARM-103_Grip_moving_finger',jaw_origin,forearm_rotation)
    # Fix only the base. Native joints retain the intended rotational freedoms.
    a.doc.ClearSelection2(True)
    a.components['base'].Select4(False,nothing(),False)
    a.doc.FixComponent()
    a.doc.ClearSelection2(True)
    a.mate('J1_yaw_axis',1,a.cylinder('yaw',3.95),a.cylinder('base',11.1))
    a.mate('J1_yaw_height',0,a.plane('base','Top Plane'),a.plane('yaw','Top Plane'))
    for item,parent in [('collar','yaw'),('yaw_servo','base'),('yaw_bearing_low','base'),
                        ('yaw_bearing_high','base'),('shoulder_servo','yaw'),
                        ('elbow_servo','upper'),('grip_servo','forearm')]:
        a.rigid('Mount_'+item,parent,item)
    a.joint('J2_shoulder','upper','shoulder_servo',4,3,'yaw',23)
    a.joint('J3_elbow','forearm','elbow_servo',3,2.5,'upper',15)
    a.joint('J4_grip','jaw','grip_servo',3,2.5,'forearm',0)
    a.save()

if __name__=='__main__':
    main()
