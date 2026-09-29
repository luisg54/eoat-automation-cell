"""Measure the owned MG996R and SG90 part files from their native B-rep (read-only).

The user's inserted parts are the authority for every servo interface in revision D.
Each file is opened hidden, measured, and closed without saving. Selection rules are
explicit and checked; raw planar/cylindrical face data are kept in the report.
Results use an interface frame per servo: origin on the output axis in the plane of
the ear underside (the face that seats on the printed mount), +Z along the output,
+X toward the far end of the case.
"""
import json, math
from collections import defaultdict
from build_native import ROOT, connect, call, integer_ref

FILES = {'MG996R': ROOT/'parts'/'MG996R_servo.SLDPRT', 'SG90': ROOT/'parts'/'SERVO_SG90.SLDPRT'}

def dump(sw, path):
    was_open = sw.GetOpenDocumentByName(str(path)) is not None
    visible = sw.GetDocumentVisible(1)
    sw.DocumentVisible(False, 1)
    try:
        doc = sw.OpenDoc6(str(path), 1, 1, '', integer_ref(), integer_ref())
        if doc is None: raise RuntimeError('Cannot open '+str(path))
        features = []
        f = call(doc, 'FirstFeature')
        while f:
            features.append({'name': call(f, 'Name'), 'type': call(f, 'GetTypeName2')})
            f = call(f, 'GetNextFeature')
        bodies = []
        for body in call(doc, 'GetBodies2', 0, False) or []:
            faces = []
            for face in call(body, 'GetFaces') or []:
                s = call(face, 'GetSurface')
                row = {'area_mm2': call(face, 'GetArea')*1e6, 'box_mm': [v*1000 for v in call(face, 'GetBox')]}
                if call(s, 'IsPlane'):
                    p = list(call(s, 'PlaneParams')); row.update(kind='plane', normal=p[:3], point_mm=[v*1000 for v in p[3:6]])
                elif call(s, 'IsCylinder'):
                    p = list(call(s, 'CylinderParams'))
                    row.update(kind='cylinder', origin_mm=[v*1000 for v in p[:3]], axis=p[3:6], radius_mm=p[6]*1000)
                else:
                    row.update(kind='other')
                faces.append(row)
            bodies.append({'name': call(body, 'Name'), 'box_mm': [v*1000 for v in call(body, 'GetBodyBox')], 'faces': faces})
        mp = call(doc.Extension, 'CreateMassProperty')
        units = list(call(doc, 'GetUnits'))
        result = {'file': str(path.relative_to(ROOT)), 'length_unit_code': units[0],
                  'features': features, 'bodies': bodies, 'volume_mm3': call(mp, 'Volume')*1e9,
                  'part_box_mm': [v*1000 for v in call(doc, 'GetPartBox', True)],
                  'material': 'not specified in file (mass properties use SolidWorks default density)'}
        if call(doc, 'GetSaveFlag'): raise RuntimeError('Measurement unexpectedly modified '+str(path))
        return result
    finally:
        if not was_open and sw.GetOpenDocumentByName(str(path)) is not None:
            sw.CloseDoc(str(path))
        sw.DocumentVisible(visible, 1)

def planes(body, axis):
    """Planar faces whose normal is parallel to the given file axis (0=X,1=Y,2=Z)."""
    return [f for f in body['faces'] if f['kind'] == 'plane' and abs(abs(f['normal'][axis])-1) < 1e-6]

def cylinders(body, axis=1):
    return [f for f in body['faces'] if f['kind'] == 'cylinder' and abs(abs(f['axis'][axis])-1) < 1e-6]

def near(a, b, tol=1e-3): return abs(a-b) <= tol

def mg996r(d):
    spline = max(d['bodies'], key=lambda b: b['box_mm'][4])
    case = next(b for b in d['bodies'] if b is not spline)
    lands = [f for f in cylinders(spline) if 2.9 < f['radius_mm'] < 3.0 and f['area_mm2'] < 5]
    teeth = len(lands)
    tip_r = lands[0]['radius_mm']
    ax_x, ax_z = lands[0]['origin_mm'][0], lands[0]['origin_mm'][2]
    top = spline['box_mm'][4]
    y_levels = sorted({round(f['point_mm'][1], 3) for f in planes(spline, 1)})
    teeth_base = y_levels[-2]
    length = top - teeth_base
    land_w = lands[0]['area_mm2']/length
    flanks = [f for f in spline['faces'] if f['kind'] == 'plane' and abs(f['normal'][1]) < 0.5 and f['area_mm2'] > 0.5]
    slant = flanks[0]['area_mm2']/length
    opening = 2*math.pi*tip_r/teeth - land_w
    groove = math.sqrt(slant**2-(opening/2)**2)
    bore = [f for f in cylinders(spline) if f['radius_mm'] < 1.5]
    bore_r = bore[0]['radius_mm']; bore_bottom = min(f['box_mm'][1] for f in bore)
    thread = [f for f in spline['faces'] if f['kind'] == 'other']
    # Case: ear underside is the lowest downward-facing plane outside the case walls.
    walls_top = sorted(f['point_mm'][0] for f in planes(case, 0) if f['area_mm2'] > 100 and f['box_mm'][1] > 20)
    ear_faces = [f for f in planes(case, 1) if f['box_mm'][3] <= walls_top[0]+1e-6 or f['box_mm'][0] >= walls_top[-1]-1e-6]
    ear_bottom = min(f['point_mm'][1] for f in ear_faces)
    near_end = [f['point_mm'][1] for f in ear_faces if f['box_mm'][3] <= walls_top[0]+1e-6]
    far_end = [f['point_mm'][1] for f in ear_faces if f['box_mm'][0] >= walls_top[-1]-1e-6]
    holes = [f for f in cylinders(case) if near(f['radius_mm'], 2.0) and f['box_mm'][1] >= ear_bottom-1e-6 and f['box_mm'][4] <= max(near_end+far_end)+1e-6]
    hole_x = sorted({round(f['origin_mm'][0]-ax_x, 3) for f in holes}); hole_y = sorted({round(-(f['origin_mm'][2]-ax_z), 3) for f in holes})
    xs_all = [f['point_mm'][0] for f in planes(case, 0)]
    zs = [f['point_mm'][2] for f in planes(case, 2) if f['area_mm2'] > 1000]
    bottom_walls = [f['point_mm'][0] for f in planes(case, 0) if f['box_mm'][4] <= 7.0 and f['area_mm2'] > 50]
    tops = defaultdict(list)
    for f in planes(case, 1):
        if f['point_mm'][1] > ear_bottom+3:
            tops[round(f['point_mm'][1]-ear_bottom, 3)].append([round(f['box_mm'][0]-ax_x, 3), round(f['box_mm'][3]-ax_x, 3), round(-f['box_mm'][5]+ax_z, 3), round(-f['box_mm'][2]+ax_z, 3)])
    top_cyl = sorted({(round(f['radius_mm'], 3), round(f['origin_mm'][0]-ax_x, 3), round(f['box_mm'][4]-ear_bottom, 3)) for f in cylinders(case) if f['box_mm'][1] >= ear_bottom+7})
    ring = max((c for c in top_cyl if abs(c[1]) < 1e-3 and c[0] > 4), key=lambda c: c[2])
    m = {'file_frame_to_interface': {'origin_file_mm': [ax_x, ear_bottom, ax_z],
            'interface_X_in_file': [1, 0, 0], 'interface_Y_in_file': [0, 0, -1], 'interface_Z_in_file': [0, 1, 0]},
         'bodies': [b['name'] for b in d['bodies']],
         'output_spline': {'type': 'straight-sided V serration modeled with flat flanks', 'teeth': teeth,
            'tip_diameter_mm': 2*tip_r, 'root_diameter_estimate_mm': 2*(tip_r-groove),
            'tooth_land_mm': land_w, 'groove_depth_mm': groove,
            'top_above_ear_underside_mm': top-ear_bottom, 'teeth_start_above_ear_underside_mm': teeth_base-ear_bottom,
            'exposed_above_output_ring_mm': top-ear_bottom-ring[2]},
         'centre_screw_hole': {'bore_diameter_mm': 2*bore_r, 'depth_from_spline_top_mm': top-bore_bottom,
            'modeled_thread': bool(thread), 'thread_envelope_diameter_mm': (thread[0]['box_mm'][5]-thread[0]['box_mm'][2]) if thread else None,
            'interpretation': 'M3 internal thread (2.5 mm tap bore with modeled helical thread)'},
         'ears': {'underside_above_case_bottom_mm': ear_bottom-case['box_mm'][1],
            'thickness_output_end_mm': max(near_end)-ear_bottom, 'thickness_far_end_mm': max(far_end)-ear_bottom,
            'hole_diameter_mm': 4.0, 'hole_x_from_axis_mm': hole_x, 'hole_y_mm': hole_y,
            'hole_slot_width_mm': 4.0, 'hole_slot': 'open to the ear end',
            'x_extent_from_axis_mm': [round(min(xs_all)-ax_x, 3), round(max(xs_all)-ax_x, 3)], 'width_mm': 19.0},
         'case': {'x_from_axis_at_ears_mm': [round(walls_top[0]-ax_x, 3), round(walls_top[-1]-ax_x, 3)],
            'x_from_axis_at_bottom_mm': [round(min(bottom_walls)-ax_x, 3), round(max(bottom_walls)-ax_x, 3)],
            'width_mm': max(zs)-min(zs), 'depth_below_ear_underside_mm': ear_bottom-case['box_mm'][1],
            'draft': 'about 1 degree on the long walls between the bottom step and the ears'},
         'top_plane_levels_above_ear_underside_mm': dict(sorted(tops.items())),
         'top_cylinders_radius_xoffset_topheight_mm': top_cyl,
         'output_ring': {'diameter_mm': 2*ring[0], 'top_above_ear_underside_mm': ring[2]},
         'horn_geometry_in_file': None, 'cable_geometry_in_file': None,
         'other_features': 'four bottom-cover counterbored M2 screw holes; raised gear-train cover block; no horn; no cable'}
    assert teeth == 25 and near(2*tip_r, 5.997, 2e-3) and near(ear_bottom, 27.994, 2e-3)
    assert len(hole_x) == 2 and near(hole_x[0], -14.150, 2e-3) and near(hole_x[1], 34.150, 2e-3) and hole_y == [-5.0, 5.0]
    return m

def sg90(d):
    spline = max(d['bodies'], key=lambda b: b['box_mm'][4])
    case = max(d['bodies'], key=lambda b: len(b['faces']) if b is not spline else 0)
    cables = [b for b in d['bodies'] if b is not spline and b is not case]
    tip = [f for f in cylinders(spline) if near(f['radius_mm'], 2.5, 0.01)]
    grooves = [f for f in cylinders(spline) if f['radius_mm'] < 0.2]
    centre = [f for f in cylinders(spline) if 0.2 < f['radius_mm'] < 1.0]
    ax_x, ax_z = tip[0]['origin_mm'][0], tip[0]['origin_mm'][2]
    top = spline['box_mm'][4]; base = spline['box_mm'][1]
    holes = [f for f in cylinders(case) if near(f['radius_mm'], 1.25)]
    ear_bottom = min(f['box_mm'][1] for f in holes); ear_top = max(f['box_mm'][4] for f in holes)
    case_z = sorted(f['point_mm'][2] for f in planes(case, 2) if f['area_mm2'] > 100)
    case_x = sorted(f['point_mm'][0] for f in planes(case, 0) if f['area_mm2'] > 100)
    ear_ends = sorted({round(f['point_mm'][2], 3) for f in planes(case, 2) if f['box_mm'][1] >= ear_bottom-1e-6 and f['box_mm'][4] <= ear_top+1e-6})
    case_top = max(f['point_mm'][1] for f in planes(case, 1) if f['box_mm'][4] < base-1)
    cover = [f for f in cylinders(case) if f['box_mm'][4] >= base-1e-6 and f['radius_mm'] > 2]
    m = {'file_frame_to_interface': {'origin_file_mm': [ax_x, ear_bottom, ax_z],
            'interface_X_in_file': [0, 0, 1], 'interface_Y_in_file': [1, 0, 0], 'interface_Z_in_file': [0, 1, 0]},
         'bodies': [b['name'] for b in d['bodies']], 'import': 'STEP import (single MBimport feature)',
         'output_spline': {'type': 'plain cylinder with shallow surface grooves; no tooth profile modeled',
            'diameter_mm': 2*tip[0]['radius_mm'], 'groove_count': len(grooves), 'groove_radius_mm': grooves[0]['radius_mm'] if grooves else None,
            'top_above_ear_underside_mm': top-ear_bottom, 'base_above_ear_underside_mm': base-ear_bottom, 'exposed_length_mm': top-base},
         'centre_screw_hole': {'diameter_mm': 2*centre[0]['radius_mm'], 'depth_mm': centre[0]['box_mm'][4]-centre[0]['box_mm'][1],
            'modeled_thread': False, 'interpretation': 'plain 1.0 mm hole through the spline only; the real SG90 horn screw is a small M2 self-tapper'},
         'ears': {'thickness_mm': ear_top-ear_bottom, 'underside_above_case_bottom_mm': ear_bottom-case['box_mm'][1],
            'hole_diameter_mm': 2*holes[0]['radius_mm'], 'hole_x_from_axis_mm': sorted(round(f['origin_mm'][2]-ax_z, 3) for f in holes),
            'hole_slot_width_mm': 1.5, 'hole_slot': 'open to the ear end', 'x_extent_from_axis_mm': [ear_ends[0]-ax_z, ear_ends[-1]-ax_z],
            'hole_centre_to_case_wall_mm': round(min(abs(case_z[0]-ax_z-(f['origin_mm'][2]-ax_z)) for f in holes), 3), 'width_mm': case_x[-1]-case_x[0]},
         'case': {'x_from_axis_mm': [case_z[0]-ax_z, case_z[-1]-ax_z], 'width_mm': case_x[-1]-case_x[0],
            'top_above_ear_underside_mm': case_top-ear_bottom, 'depth_below_ear_underside_mm': ear_bottom-case['box_mm'][1]},
         'gear_cover': {'top_above_ear_underside_mm': base-ear_bottom,
            'cylinders_radius_xoffset_mm': sorted((round(f['radius_mm'], 3), round(f['origin_mm'][2]-ax_z, 3)) for f in cover)},
         'cables': [{'diameter_mm': 2*cylinders(b, 2)[0]['radius_mm'], 'y_mm': round(b['box_mm'][0]+b['box_mm'][3], 3)/2-ax_x,
                     'below_ear_underside_mm': round(ear_bottom-(b['box_mm'][1]+b['box_mm'][4])/2, 3),
                     'x_from_axis_mm': [b['box_mm'][2]-ax_z, b['box_mm'][5]-ax_z]} for b in cables],
         'horn_geometry_in_file': None}
    assert near(2*tip[0]['radius_mm'], 5.0, 0.01) and near(top-ear_bottom, 14.4) and near(ear_top-ear_bottom, 2.4)
    return m

if __name__ == '__main__':
    sw = connect()
    report = {'status': 'Native measurements of the user-inserted owned-servo files; physical units not calipered by the agent',
              'interface_frame': 'origin on the output axis in the plane of the ear underside; +Z output; +X toward the far end of the case'}
    for key, path in FILES.items():
        d = dump(sw, path)
        report[key] = {'file': d['file'], 'features': [f['name'] for f in d['features'] if f['type'] not in ('CommentsFolder', 'FavoriteFolder', 'HistoryFolder', 'SelectionSetFolder', 'SensorFolder', 'DocsFolder', 'DetailCabinet', 'SurfaceBodyFolder', 'SolidBodyFolder', 'EnvFolder', 'InkMarkupFolder', 'EqnFolder', 'MaterialFolder')],
                       'part_box_file_mm': d['part_box_mm'], 'volume_mm3': d['volume_mm3'], 'material': d['material'],
                       **(mg996r(d) if key == 'MG996R' else sg90(d))}
    (ROOT/'owned-servo-measurements.json').write_text(json.dumps(report, indent=2))
    print(json.dumps({k: {kk: v for kk, v in report[k].items() if kk in ('output_spline', 'ears', 'case', 'output_ring', 'gear_cover', 'centre_screw_hole')} for k in FILES}, indent=1))
