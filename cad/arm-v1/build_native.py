"""Build lightweight editable native SolidWorks geometry, one document at a time.

Run in the existing SolidWorks 2026 desktop session. Never closes unrelated files.
Dimensions are millimetres in source and metres at the API boundary.
"""
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sw_probe import connect, call, pythoncom, win32com

ROOT = Path(__file__).resolve().parent
TEMPLATE = r'C:\ProgramData\SolidWorks\SOLIDWORKS 2024\templates\Part.PRTDOT'
P = json.loads((ROOT / 'design-parameters.json').read_text())

def nothing():
    return win32com.client.VARIANT(pythoncom.VT_DISPATCH, None)

def integer_ref():
    return win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)

def methods(obj, names):
    for name in names:
        try:
            obj._FlagAsMethod(name)
        except AttributeError:
            pass

class Part:
    def __init__(self, sw, name):
        self.sw, self.name = sw, name
        self.doc = sw.NewDocument(TEMPLATE, 0, 0, 0)
        if self.doc is None:
            raise RuntimeError('SolidWorks failed to create a part')
        methods(self.doc, ['ClearSelection2', 'EditRebuild3', 'ForceRebuild3', 'GetBodies2', 'GetPartBox', 'GetTitle'])
        methods(self.doc.FeatureManager, ['FeatureExtrusion2', 'FeatureCut3'])
        self.features = []

    def sketch(self, label, plane='Front Plane'):
        d = self.doc
        d.ClearSelection2(True)
        ok = d.Extension.SelectByID2(plane, 'PLANE', 0., 0., 0., False, 0, nothing(), 0)
        if not ok:
            raise RuntimeError('Front Plane selection failed')
        self.sk = d.SketchManager
        self.sk.InsertSketch(True)
        self.sk.AddToDB = True
        self.sketch_label = label
        self.plane_name = plane
        self.dimension_queue = []
        d.ClearSelection2(True)

    def circle(self, x, y, radius):
        entity = self.sk.CreateCircleByRadius(x/1000, y/1000, 0., radius/1000)
        self.dimension_queue.append(('diameter', entity, x+radius+4, y+4))
        return entity

    def rectangle(self, x1, y1, x2, y2):
        entities = self.sk.CreateCornerRectangle(x1/1000, y1/1000, 0., x2/1000, y2/1000, 0.)
        self.dimension_queue.append(('length', entities[0], (x1+x2)/2, y1-4))
        self.dimension_queue.append(('length', entities[1], x2+4, (y1+y2)/2))
        return entities

    def extrude(self, label, depth, cut=False, offset=0, flip=False, through=True):
        self.sk.AddToDB = False
        for kind, entity, x, y in self.dimension_queue:
            self.doc.ClearSelection2(True)
            if not entity.Select4(False, nothing()):
                raise RuntimeError('Dimension entity selection failed')
            position = (x/1000, 0., -y/1000) if self.plane_name == 'Top Plane' else (x/1000, y/1000, 0.)
            dim = (self.doc.AddDiameterDimension2(*position) if kind == 'diameter'
                   else self.doc.AddDimension2(*position))
            if dim is None:
                raise RuntimeError('Native sketch dimension failed: '+self.sketch_label)
        self.doc.ClearSelection2(True)
        fm = self.doc.FeatureManager
        if cut:
            feat = fm.FeatureCut3(True, False, not flip, 1 if through else 0, 0, depth/1000, 0., False, False, False, False,
                                  0., 0., False, False, False, False, False, True, True, True, True, False,
                                  3 if offset else 0, abs(offset)/1000, offset < 0)
        else:
            feat = fm.FeatureExtrusion2(True, False, flip, 0, 0, depth/1000, 0.,
                                       False, False, False, False, 0., 0., False, False, False, False,
                                       True, True, True, 3 if offset else 0, abs(offset)/1000, offset < 0)
        if feat is None:
            raise RuntimeError('Failed feature: ' + label)
        feat.Name = label
        child = call(feat, 'GetFirstSubFeature')
        if child:
            child.Name = self.sketch_label
        self.features.append(label)
        return feat

    def save(self, purchased=False):
        d = self.doc
        d.EditRebuild3()
        bodies = call(d, 'GetBodies2', 0, False)
        if not bodies or len(bodies) != 1:
            raise RuntimeError(f'{self.name}: expected one solid, got {len(bodies or [])}')
        box = [v*1000 for v in d.GetPartBox(True)]
        mass = call(d.Extension, 'CreateMassProperty')
        volume_mm3 = float(call(mass, 'Volume')) * 1e9
        if volume_mm3 <= 0:
            raise RuntimeError('Invalid volume')
        folder = ROOT / ('hardware-reference' if purchased else 'parts')
        folder.mkdir(exist_ok=True)
        d.ShowNamedView2('*Isometric', 7)
        call(d, 'ViewZoomtofit2')
        outputs = []
        for suffix in ('.SLDPRT', '.step') + (() if purchased else ('.stl',)):
            path = folder / (self.name + suffix)
            err, warn = integer_ref(), integer_ref()
            ok = d.Extension.SaveAs(str(path), 0, 1, nothing(), err, warn)
            if not ok or err.value:
                raise RuntimeError(f'Save failed: {path}, {err.value}, {warn.value}')
            outputs.append(str(path.relative_to(ROOT)))
        report = dict(name=self.name, solid_count=len(bodies), volume_mm3=volume_mm3,
                      approximate_box_mm=box, features=self.features, files=outputs,
                      status='native geometry saved; fits and physical function not yet validated')
        self.sw.CloseDoc(call(d, 'GetTitle'))
        print(json.dumps(report), flush=True)
        return report

def hardware(sw):
    reports = []
    p = Part(sw, 'HW-001_608ZZ_22x8x7_ENVELOPE')
    p.sketch('Bearing_OD22_ID8')
    p.circle(0, 0, 11)
    p.circle(0, 0, 4)
    p.extrude('Bearing_width_7mm_simplified', 7)
    reports.append(p.save(True))
    p = Part(sw, 'HW-002_Dowel_6p35x25p4')
    p.sketch('Dowel_diameter_6p35mm')
    p.circle(0, 0, 3.175)
    p.extrude('Dowel_length_25p4mm', 25.4)
    reports.append(p.save(True))
    return reports

if __name__ == '__main__':
    sw = connect()
    print('SolidWorks revision', call(sw, 'RevisionNumber'), flush=True)
    prior = sw.GetUserPreferenceToggle(16)
    try:
        sw.SetUserPreferenceToggle(16, False)
        reports = hardware(sw)
        (ROOT / 'native-build-report.json').write_text(json.dumps(reports, indent=2))
    finally:
        sw.SetUserPreferenceToggle(16, prior)
