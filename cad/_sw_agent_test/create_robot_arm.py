"""SolidWorks COM demo: L-shaped desktop robot arm.

Not EOAT cell CAD. Leaves SolidWorks open. Exports SLDPRT / STL / STEP.

Front view: base on the table, column up, forearm out to +X, parallel-jaw gripper.
"""

from __future__ import annotations

import os
import traceback

import pythoncom
import win32com.client

TEMPLATE = r"C:\ProgramData\SolidWorks\SOLIDWORKS 2024\templates\Part.PRTDOT"
TEMPLATE_FALLBACK = r"C:\ProgramData\SolidWorks\SOLIDWORKS 2026\templates\MBD\part 0011mm to 0050mm.prtdot"
PROGID = "SldWorks.Application"

SW_INPUT_DIM_VAL_ON_CREATE = 16
SW_SAVE_AS_CURRENT_VERSION = 0
SW_SAVE_AS_SILENT = 1
SW_END_BLIND = 0
SW_END_THROUGH_ALL = 1
SW_END_MIDPLANE = 6
DANG = 1.74532925199433e-2


def mm(v: float) -> float:
    return v * 0.001


def _byref_i4():
    return win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)


def _nothing():
    return win32com.client.VARIANT(pythoncom.VT_DISPATCH, None)


def _flag_methods(obj, names):
    for name in names:
        try:
            obj._FlagAsMethod(name)
        except Exception:
            pass


def connect():
    pythoncom.CoInitialize()
    try:
        sw = win32com.client.GetActiveObject(PROGID)
        print("Attached to a SolidWorks instance that was already open.")
    except Exception as exc:
        raise RuntimeError("Open SolidWorks 2026 first, then re-run.") from exc
    sw.Visible = True
    sw.UserControl = True
    try:
        sw.SetUserPreferenceToggle(SW_INPUT_DIM_VAL_ON_CREATE, False)
    except Exception:
        pass
    return sw


def save_as(model, path):
    err = _byref_i4()
    warn = _byref_i4()
    ok = model.Extension.SaveAs(
        path, SW_SAVE_AS_CURRENT_VERSION, SW_SAVE_AS_SILENT, _nothing(), err, warn
    )
    if not ok:
        raise RuntimeError(f"SaveAs failed for {path} (err={err.value}, warn={warn.value})")


def select_plane(model, names):
    model.ClearSelection2(True)
    nothing = _nothing()
    for name in names:
        if model.Extension.SelectByID2(name, "PLANE", 0.0, 0.0, 0.0, False, 0, nothing, 0):
            return name
    raise RuntimeError(f"Could not select a plane from {names}")


def start_sketch(model, plane_names):
    plane = select_plane(model, plane_names)
    sk = model.SketchManager
    sk.AddToDB = True
    sk.InsertSketch(True)
    model.ClearSelection2(True)
    return sk, plane


def finish_sketch(sk):
    sk.AddToDB = False


def boss(model, t1, d1, merge=True, flip=False):
    feat = model.FeatureManager.FeatureExtrusion2(
        True, False, flip, t1, 0, d1, 0.0,
        False, False, False, False, DANG, DANG,
        False, False, False, False,
        merge, True, True, 0, 0, False,
    )
    if feat is None:
        raise RuntimeError("FeatureExtrusion2 returned None")
    return feat


def cut(model, t1, d1, flip=False):
    feat = model.FeatureManager.FeatureCut3(
        True, False, flip, t1, 0, d1, 0.0,
        False, False, False, False, DANG, DANG,
        False, False, False, False, False,
        True, True, True, True, False, 0, 0, False,
    )
    if feat is None:
        raise RuntimeError("FeatureCut3 returned None")
    return feat


def circle(sk, cx, cy, radius):
    try:
        ent = sk.CreateCircleByRadius(cx, cy, 0.0, radius)
    except Exception:
        ent = None
    if ent is None:
        ent = sk.CreateCircle(cx, cy, 0.0, cx + radius, cy, 0.0)
    if ent is None:
        raise RuntimeError("CreateCircle failed")
    return ent


def rect(sk, x1, y1, x2, y2):
    ent = sk.CreateCornerRectangle(x1, y1, 0.0, x2, y2, 0.0)
    if ent is None:
        raise RuntimeError("CreateCornerRectangle failed")
    return ent


def feature(model, label, builder):
    print(f"  {label} ...")
    feat = builder()
    name = getattr(feat, "Name", "?")
    print(f"    -> {name}")
    return feat


def bbox_mm(model):
    box = [float(v) for v in model.GetPartBox(True)]
    return (
        (box[3] - box[0]) * 1000,
        (box[4] - box[1]) * 1000,
        (box[5] - box[2]) * 1000,
        [v * 1000 for v in box],
    )


def new_part(sw):
    template = TEMPLATE if os.path.isfile(TEMPLATE) else TEMPLATE_FALLBACK
    if not os.path.isfile(template):
        raise FileNotFoundError(template)
    print(f"New part from template:\n  {template}")
    model = sw.NewDocument(template, 0, 0, 0)
    if model is None:
        model = sw.NewPart()
    if model is None:
        raise RuntimeError("Could not create a part.")
    _flag_methods(model, ("EditRebuild3", "ForceRebuild3", "GetPartBox", "ClearSelection2"))
    _flag_methods(model.Extension, ("SelectByID2", "SaveAs", "CreateMassProperty2"))
    _flag_methods(
        model.FeatureManager,
        ("FeatureExtrusion2", "FeatureExtrusion3", "FeatureCut3", "FeatureCut4"),
    )
    return model


def build_arm(model):
    top = ("Top Plane", "Top")
    front = ("Front Plane", "Front")
    right = ("Right Plane", "Right")

    # 1. Base plate 110 x 110 x 12 mm
    def base_plate():
        sk, _ = start_sketch(model, top)
        rect(sk, mm(-55), mm(-55), mm(55), mm(55))
        finish_sketch(sk)
        return boss(model, SW_END_BLIND, mm(12), merge=True)

    feature(model, "base plate", base_plate)

    # 2. Four rubber-foot bosses, 8 mm down
    def feet():
        sk, _ = start_sketch(model, top)
        for x, z in ((-40, -40), (40, -40), (-40, 40), (40, 40)):
            circle(sk, mm(x), mm(z), mm(9))
        finish_sketch(sk)
        return boss(model, SW_END_BLIND, mm(8), merge=True, flip=True)

    feature(model, "feet", feet)

    # 3. Column Ø56 x 60 mm from the top plane (48 mm above the plate)
    def column():
        sk, _ = start_sketch(model, top)
        circle(sk, 0.0, 0.0, mm(28))
        finish_sketch(sk)
        return boss(model, SW_END_BLIND, mm(60), merge=True)

    feature(model, "column", column)

    # 4. Shoulder housing
    def shoulder():
        sk, _ = start_sketch(model, front)
        rect(sk, mm(-30), mm(50), mm(30), mm(102))
        finish_sketch(sk)
        return boss(model, SW_END_MIDPLANE, mm(50), merge=True)

    feature(model, "shoulder", shoulder)

    # 5. Upper arm (vertical)
    def upper_arm():
        sk, _ = start_sketch(model, front)
        rect(sk, mm(-16), mm(98), mm(16), mm(205))
        finish_sketch(sk)
        return boss(model, SW_END_MIDPLANE, mm(32), merge=True)

    feature(model, "upper arm", upper_arm)

    # 6. Elbow block (turns into +X)
    def elbow():
        sk, _ = start_sketch(model, front)
        rect(sk, mm(-22), mm(192), mm(50), mm(242))
        finish_sketch(sk)
        return boss(model, SW_END_MIDPLANE, mm(42), merge=True)

    feature(model, "elbow", elbow)

    # 7. Elbow "servo" disk
    def elbow_disk():
        sk, _ = start_sketch(model, front)
        circle(sk, mm(14), mm(217), mm(18))
        finish_sketch(sk)
        return boss(model, SW_END_MIDPLANE, mm(12), merge=True)

    feature(model, "elbow disk", elbow_disk)

    # 8. Forearm (horizontal)
    def forearm():
        sk, _ = start_sketch(model, front)
        rect(sk, mm(45), mm(208), mm(160), mm(236))
        finish_sketch(sk)
        return boss(model, SW_END_MIDPLANE, mm(28), merge=True)

    feature(model, "forearm", forearm)

    # 9. Wrist
    def wrist():
        sk, _ = start_sketch(model, front)
        rect(sk, mm(152), mm(200), mm(186), mm(244))
        finish_sketch(sk)
        return boss(model, SW_END_MIDPLANE, mm(34), merge=True)

    feature(model, "wrist", wrist)

    # 10. Wrist roll cylinder
    def wrist_roll_front():
        sk, _ = start_sketch(model, front)
        circle(sk, mm(186), mm(222), mm(13))
        finish_sketch(sk)
        return boss(model, SW_END_MIDPLANE, mm(30), merge=True)

    feature(model, "wrist roll", wrist_roll_front)

    # 11. Gripper body
    def gripper_body():
        sk, _ = start_sketch(model, front)
        rect(sk, mm(178), mm(206), mm(228), mm(240))
        finish_sketch(sk)
        return boss(model, SW_END_MIDPLANE, mm(36), merge=True)

    feature(model, "gripper body", gripper_body)

    # 12. Parallel-jaw slot
    def jaw_slot():
        sk, _ = start_sketch(model, front)
        rect(sk, mm(196), mm(214), mm(232), mm(232))
        finish_sketch(sk)
        return cut(model, SW_END_MIDPLANE, mm(22))

    feature(model, "jaw slot", jaw_slot)

    # 13. Shoulder axle bore
    def shoulder_bore():
        sk, _ = start_sketch(model, right)
        circle(sk, 0.0, mm(76), mm(6))
        finish_sketch(sk)
        return cut(model, SW_END_THROUGH_ALL, mm(1))

    feature(model, "shoulder bore", shoulder_bore)

    # 14. Elbow axle bore
    def elbow_bore():
        sk, _ = start_sketch(model, front)
        circle(sk, mm(14), mm(217), mm(5))
        finish_sketch(sk)
        return cut(model, SW_END_THROUGH_ALL, mm(1))

    feature(model, "elbow bore", elbow_bore)

    # 15. Wrist axle bore
    def wrist_bore():
        sk, _ = start_sketch(model, front)
        circle(sk, mm(169), mm(222), mm(4))
        finish_sketch(sk)
        return cut(model, SW_END_THROUGH_ALL, mm(1))

    feature(model, "wrist bore", wrist_bore)

    # 16. Base mounting holes (4x)
    def base_holes():
        sk, _ = start_sketch(model, top)
        for x, z in ((-42, -42), (42, -42), (-42, 42), (42, 42)):
            circle(sk, mm(x), mm(z), mm(3.5))
        finish_sketch(sk)
        return cut(model, SW_END_THROUGH_ALL, mm(1))

    feature(model, "base holes", base_holes)


def main() -> int:
    out_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.join(out_dir, "agent_desk_arm")

    print(f"Connecting to {PROGID} ...")
    sw = connect()
    print(f"Connected. RevisionNumber = {sw.RevisionNumber}")

    model = new_part(sw)
    print("Building L-shaped desk arm:")
    build_arm(model)
    model.EditRebuild3()

    dx, dy, dz, box = bbox_mm(model)
    print(f"Bounding box mm: {dx:.2f} x {dy:.2f} x {dz:.2f}")
    print(f"  extents mm: {['%.2f' % v for v in box]}")

    # Reach should be well past a cube: X span > 200 mm, Y span > 200 mm.
    ok = dx > 200 and dy > 200 and dz > 40
    print(f"Complexity check (reach > 200 mm, thickness > 40 mm): {'PASS' if ok else 'FAIL'}")

    print("Saving SLDPRT / STL / STEP ...")
    save_as(model, stem + ".sldprt")
    save_as(model, stem + ".stl")
    save_as(model, stem + ".step")
    print(f"Wrote:\n  {stem}.sldprt\n  {stem}.stl\n  {stem}.step")
    print("Leaving SolidWorks open. Iso-view the new part — ignore leftover empty parts.")
    return 0 if ok else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
