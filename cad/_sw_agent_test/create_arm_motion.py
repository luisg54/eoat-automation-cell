"""Rebuild the desk arm as a 4-part assembly, then run a Motion Study.

Not EOAT cell CAD. SolidWorks 2026 must already be open.
"""

from __future__ import annotations

import glob
import os
import time
import traceback

import pythoncom
import win32com.client

PART_TEMPLATE = r"C:\ProgramData\SolidWorks\SOLIDWORKS 2024\templates\Part.PRTDOT"
ASM_TEMPLATE = r"C:\ProgramData\SolidWorks\SOLIDWORKS 2024\templates\Assembly.ASMDOT"
PROGID = "SldWorks.Application"

SW_INPUT_DIM_VAL_ON_CREATE = 16
SW_SAVE_AS_CURRENT_VERSION = 0
SW_SAVE_AS_SILENT = 1
SW_END_BLIND = 0
SW_END_THROUGH_ALL = 1
SW_END_MIDPLANE = 6
SW_DOC_PART = 1
SW_DOC_ASSEMBLY = 2
SW_OPEN_SILENT = 1
SW_SOLID_BODY = 0
SW_MATE_COINCIDENT = 0
SW_MATE_CONCENTRIC = 1
SW_FM_AEM_ROTATIONAL_MOTOR = 78
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


def com(obj, name, *args):
    member = getattr(obj, name)
    if args:
        return member(*args) if callable(member) else (_ for _ in ()).throw(
            TypeError(f"{name} is not callable")
        )
    try:
        return member() if callable(member) else member
    except Exception:
        return member


def as_list(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


def connect():
    pythoncom.CoInitialize()
    sw = win32com.client.GetActiveObject(PROGID)
    sw.Visible = True
    sw.UserControl = True
    try:
        sw.SetUserPreferenceToggle(SW_INPUT_DIM_VAL_ON_CREATE, False)
    except Exception:
        pass
    print("Attached to SolidWorks.")
    print(f"RevisionNumber = {com(sw, 'RevisionNumber')}")
    try:
        sw.DisplayAlerts = False
    except Exception:
        pass
    return sw


def close_prior_arm_docs(sw):
    markers = ("01_base", "02_shoulder", "03_upper_arm", "04_forearm", "agent_desk_arm", "arm_motion")
    docs = as_list(com(sw, "GetDocuments"))
    titles = []
    for doc in docs:
        try:
            title = str(com(doc, "GetTitle") or "")
            path = str(com(doc, "GetPathName") or "")
        except Exception:
            continue
        blob = f"{title} {path}".lower()
        if any(m.lower() in blob for m in markers):
            titles.append(title)
    for title in sorted(titles, key=lambda t: 0 if t.lower().endswith(".sldasm") or "agent_desk_arm" in t.lower() else 1):
        try:
            sw.CloseDoc(title)
            print(f"  closed {title}")
        except Exception as exc:
            print(f"  close skip {title}: {exc}")


def save_as(model, path):
    try:
        model.EditRebuild3()
    except Exception:
        pass
    if os.path.isfile(path):
        try:
            os.remove(path)
        except Exception as exc:
            print(f"  could not replace {os.path.basename(path)}: {exc}")
    err = _byref_i4()
    warn = _byref_i4()
    ok = model.Extension.SaveAs(
        path, SW_SAVE_AS_CURRENT_VERSION, SW_SAVE_AS_SILENT, _nothing(), err, warn
    )
    if not ok:
        try:
            ok = bool(model.SaveAs3(path, 0, 0))
        except Exception:
            ok = False
    if not ok:
        raise RuntimeError(f"SaveAs failed for {path} (err={err.value})")


def select_plane(model, names):
    model.ClearSelection2(True)
    nothing = _nothing()
    for name in names:
        if model.Extension.SelectByID2(name, "PLANE", 0.0, 0.0, 0.0, False, 0, nothing, 0):
            return name
    raise RuntimeError(f"Could not select plane {names}")


def start_sketch(model, plane_names):
    select_plane(model, plane_names)
    sk = model.SketchManager
    sk.AddToDB = True
    sk.InsertSketch(True)
    model.ClearSelection2(True)
    return sk


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
        raise RuntimeError("FeatureExtrusion2 failed")
    return feat


def cut(model, t1, d1, flip=False):
    try:
        feat = model.FeatureManager.FeatureCut3(
            True, False, flip, t1, 0, d1, 0.0,
            False, False, False, False, DANG, DANG,
            False, False, False, False, False,
            True, True, True, True, False, 0, 0, False,
        )
    except Exception as exc:
        print(f"    FeatureCut3 exception: {exc}")
        feat = None
    if feat is None:
        raise RuntimeError("FeatureCut3 failed")
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


def new_part(sw):
    if not os.path.isfile(PART_TEMPLATE):
        raise FileNotFoundError(PART_TEMPLATE)
    model = sw.NewDocument(PART_TEMPLATE, 0, 0, 0)
    if model is None:
        model = sw.NewPart()
    if model is None:
        raise RuntimeError("New part failed")
    _flag_methods(model, ("EditRebuild3", "ForceRebuild3", "GetPartBox", "ClearSelection2", "FeatureByName"))
    _flag_methods(model.Extension, ("SelectByID2", "SaveAs"))
    _flag_methods(model.FeatureManager, ("FeatureExtrusion2", "FeatureCut3"))
    return model


def set_color(model, rgb):
    r, g, b = rgb
    try:
        model.MaterialPropertyValues = [r, g, b, 1.0, 1.0, 0.5, 0.4, 0.0, 0.0]
    except Exception:
        pass


def save_part(sw, model, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    save_as(model, path)
    print(f"  saved {os.path.basename(path)}")
    return path


TOP = ("Top Plane", "Top")
FRONT = ("Front Plane", "Front")
RIGHT = ("Right Plane", "Right")


def build_base(sw, path):
    print("Building base ...")
    model = new_part(sw)
    sk = start_sketch(model, TOP)
    circle(sk, 0.0, 0.0, mm(58))
    finish_sketch(sk)
    boss(model, SW_END_BLIND, mm(14), merge=True)

    sk = start_sketch(model, TOP)
    for x, z in ((-36, -36), (36, -36), (-36, 36), (36, 36)):
        circle(sk, mm(x), mm(z), mm(8))
    finish_sketch(sk)
    boss(model, SW_END_BLIND, mm(6), merge=True, flip=True)

    sk = start_sketch(model, TOP)
    circle(sk, 0.0, 0.0, mm(26))
    finish_sketch(sk)
    boss(model, SW_END_BLIND, mm(58), merge=True)

    # J1 pin Ø12 — unique r=6.00
    sk = start_sketch(model, TOP)
    circle(sk, 0.0, 0.0, mm(6.0))
    finish_sketch(sk)
    boss(model, SW_END_BLIND, mm(72), merge=True)

    sk = start_sketch(model, TOP)
    for x, z in ((-40, -40), (40, -40), (-40, 40), (40, 40)):
        circle(sk, mm(x), mm(z), mm(3.4))
    finish_sketch(sk)
    cut(model, SW_END_THROUGH_ALL, mm(1))

    set_color(model, (0.18, 0.20, 0.22))
    model.EditRebuild3()
    return save_part(sw, model, path)


def build_shoulder(sw, path):
    print("Building shoulder ...")
    model = new_part(sw)
    # Tube hub: two concentric circles extrude as a bore, no cut needed.
    sk = start_sketch(model, TOP)
    circle(sk, 0.0, 0.0, mm(16))
    circle(sk, 0.0, 0.0, mm(6.25))
    finish_sketch(sk)
    boss(model, SW_END_BLIND, mm(100), merge=True)

    # Chop the unused stalk below the column top (Front sketch intersects the solid).
    sk = start_sketch(model, FRONT)
    rect(sk, mm(-20), mm(-2), mm(20), mm(53))
    finish_sketch(sk)
    cut(model, SW_END_MIDPLANE, mm(40))

    # Pitch housing
    sk = start_sketch(model, FRONT)
    rect(sk, mm(-28), mm(54), mm(28), mm(100))
    finish_sketch(sk)
    boss(model, SW_END_MIDPLANE, mm(56), merge=True)

    # J2 pin Ø16 — boss both ways so it cannot disappear inside the housing
    sk = start_sketch(model, FRONT)
    circle(sk, 0.0, mm(76), mm(8.0))
    finish_sketch(sk)
    boss(model, SW_END_BLIND, mm(42), merge=True, flip=False)
    sk = start_sketch(model, FRONT)
    circle(sk, 0.0, mm(76), mm(8.0))
    finish_sketch(sk)
    boss(model, SW_END_BLIND, mm(42), merge=True, flip=True)

    set_color(model, (0.15, 0.38, 0.62))
    model.EditRebuild3()
    return save_part(sw, model, path)


def build_upper_arm(sw, path):
    print("Building upper arm ...")
    model = new_part(sw)
    sk = start_sketch(model, FRONT)
    rect(sk, mm(-16), mm(64), mm(16), mm(208))
    finish_sketch(sk)
    boss(model, SW_END_MIDPLANE, mm(30), merge=True)

    # J2 hub
    sk = start_sketch(model, FRONT)
    circle(sk, 0.0, mm(76), mm(18))
    finish_sketch(sk)
    boss(model, SW_END_MIDPLANE, mm(28), merge=True)

    # J3 hub
    sk = start_sketch(model, FRONT)
    circle(sk, 0.0, mm(198), mm(16))
    finish_sketch(sk)
    boss(model, SW_END_MIDPLANE, mm(28), merge=True)

    # J2 bore Ø16.5 — unique r=8.25
    sk = start_sketch(model, FRONT)
    circle(sk, 0.0, mm(76), mm(8.25))
    finish_sketch(sk)
    cut(model, SW_END_THROUGH_ALL, mm(1))

    # J3 pin Ø14 — unique r=7.00
    sk = start_sketch(model, FRONT)
    circle(sk, 0.0, mm(198), mm(7.0))
    finish_sketch(sk)
    boss(model, SW_END_MIDPLANE, mm(40), merge=True)

    # Lightening holes r=10 — keep clear of joint radii
    sk = start_sketch(model, FRONT)
    circle(sk, 0.0, mm(118), mm(10))
    circle(sk, 0.0, mm(155), mm(10))
    finish_sketch(sk)
    cut(model, SW_END_THROUGH_ALL, mm(1))

    set_color(model, (0.72, 0.74, 0.76))
    model.EditRebuild3()
    return save_part(sw, model, path)


def build_forearm(sw, path):
    print("Building forearm + gripper ...")
    model = new_part(sw)
    sk = start_sketch(model, FRONT)
    rect(sk, mm(-20), mm(182), mm(52), mm(218))
    finish_sketch(sk)
    boss(model, SW_END_MIDPLANE, mm(34), merge=True)

    sk = start_sketch(model, FRONT)
    rect(sk, mm(48), mm(190), mm(172), mm(214))
    finish_sketch(sk)
    boss(model, SW_END_MIDPLANE, mm(24), merge=True)

    sk = start_sketch(model, FRONT)
    rect(sk, mm(168), mm(184), mm(198), mm(222))
    finish_sketch(sk)
    boss(model, SW_END_MIDPLANE, mm(30), merge=True)

    sk = start_sketch(model, FRONT)
    rect(sk, mm(192), mm(186), mm(248), mm(220))
    finish_sketch(sk)
    boss(model, SW_END_MIDPLANE, mm(34), merge=True)

    # Parallel jaws: open slot
    sk = start_sketch(model, FRONT)
    rect(sk, mm(214), mm(194), mm(252), mm(212))
    finish_sketch(sk)
    cut(model, SW_END_MIDPLANE, mm(20))

    # J3 bore Ø14.5 — unique r=7.25
    sk = start_sketch(model, FRONT)
    circle(sk, 0.0, mm(198), mm(7.25))
    finish_sketch(sk)
    cut(model, SW_END_THROUGH_ALL, mm(1))

    sk = start_sketch(model, FRONT)
    circle(sk, mm(110), mm(202), mm(7.5))
    finish_sketch(sk)
    cut(model, SW_END_THROUGH_ALL, mm(1))

    set_color(model, (0.92, 0.45, 0.12))
    model.EditRebuild3()
    return save_part(sw, model, path)


def new_assembly(sw):
    if not os.path.isfile(ASM_TEMPLATE):
        raise FileNotFoundError(ASM_TEMPLATE)
    model = sw.NewDocument(ASM_TEMPLATE, 0, 0, 0)
    if model is None:
        raise RuntimeError("New assembly failed")
    _flag_methods(
        model,
        ("AddComponent5", "AddMate5", "FixComponent", "ForceRebuild3", "ClearSelection2", "EditRebuild3"),
    )
    _flag_methods(model.Extension, ("SelectByID2", "SaveAs", "GetMotionStudyManager"))
    return model


def activate(sw, model):
    err = _byref_i4()
    title = com(model, "GetTitle")
    sw.ActivateDoc3(title, True, 0, err)
    return model


def identity_transform(sw):
    mu = com(sw, "GetMathUtility")
    data = (
        1.0, 0.0, 0.0,
        0.0, 1.0, 0.0,
        0.0, 0.0, 1.0,
        0.0, 0.0, 0.0,
        1.0, 0.0, 0.0, 0.0,
    )
    return mu.CreateTransform(data)


def add_component(sw, asm, path):
    activate(sw, asm)
    comp = asm.AddComponent5(path, 0, "", False, "", 0.0, 0.0, 0.0)
    if comp is None:
        err = _byref_i4()
        warn = _byref_i4()
        sw.DocumentVisible(False, SW_DOC_PART)
        opened = sw.OpenDoc6(path, SW_DOC_PART, SW_OPEN_SILENT, "", err, warn)
        sw.DocumentVisible(True, SW_DOC_PART)
        if opened is None:
            raise RuntimeError(f"AddComponent5/OpenDoc6 failed: {path} err={err.value} warn={warn.value}")
        activate(sw, asm)
        comp = asm.AddComponent5(path, 0, "", False, "", 0.0, 0.0, 0.0)
    if comp is None:
        raise RuntimeError(f"AddComponent5 failed: {path}")
    try:
        comp.Transform2 = identity_transform(sw)
    except Exception as exc:
        print(f"  Transform2 skipped: {exc}")
    try:
        comp.SetSuppression2(2)
    except Exception:
        pass
    print(f"  inserted {os.path.basename(path)} as {com(comp, 'Name2')}")
    return comp


def get_part(comp):
    try:
        comp.SetSuppression2(2)
    except Exception:
        pass
    part = com(comp, "GetModelDoc2")
    if part is None:
        raise RuntimeError(f"GetModelDoc2 failed for {com(comp, 'Name2')}")
    return part


def find_cylinder(comp, rmin, rmax):
    part = get_part(comp)
    best = None
    best_area = -1.0
    bodies = as_list(com(part, "GetBodies2", SW_SOLID_BODY, False))
    found = []
    for body in bodies:
        for face in as_list(com(body, "GetFaces")):
            surface = com(face, "GetSurface")
            if surface is None:
                continue
            try:
                if not com(surface, "IsCylinder"):
                    continue
                params = com(surface, "CylinderParams")
                radius = float(params[6])
                found.append(radius)
                if radius < rmin or radius > rmax:
                    continue
                area = float(com(face, "GetArea"))
                if area > best_area:
                    best_area = area
                    best = face
            except Exception:
                continue
    if best is None:
        radii = ", ".join(f"{r*1000:.2f}" for r in sorted(set(found)))
        raise RuntimeError(
            f"No cylinder on {com(comp, 'Name2')} in r=[{rmin*1000:.2f},{rmax*1000:.2f}] mm "
            f"(found: {radii or 'none'})"
        )
    mapped = comp.GetCorresponding(best)
    if mapped is None:
        raise RuntimeError(f"GetCorresponding failed for {com(comp, 'Name2')}")
    print(f"    cylinder r={best_area and (rmin+rmax)/2*1000:.2f}mm-ish on {com(comp, 'Name2')}")
    return mapped


def plane_entity(comp, names):
    part = get_part(comp)
    feat = None
    for name in names:
        try:
            feat = part.FeatureByName(name)
        except Exception:
            feat = None
        if feat:
            break
    if feat is None:
        raise RuntimeError(f"Plane {names} missing on {com(comp, 'Name2')}")
    mapped = comp.GetCorresponding(feat)
    if mapped is None:
        raise RuntimeError("GetCorresponding plane failed")
    return mapped


def select_two(model, a, b, mark=1):
    model.ClearSelection2(True)
    if not a.Select2(False, mark):
        raise RuntimeError("Select entity 1 failed")
    if not b.Select2(True, mark):
        raise RuntimeError("Select entity 2 failed")


def add_mate(asm, mate_type, lock_rotation=False, name=None, align=2):
    err = _byref_i4()
    mate = asm.AddMate5(
        int(mate_type), int(align), False,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        False, bool(lock_rotation), 0, err,
    )
    if mate is None and err.value not in (0, 1):
        raise RuntimeError(f"AddMate5 failed type={mate_type} err={err.value}")
    if mate is None:
        raise RuntimeError(f"AddMate5 returned None type={mate_type} err={err.value}")
    if name:
        try:
            mate.Name = name
        except Exception:
            pass
    asm.ClearSelection2(True)
    print(f"  mate {name or mate_type} err={err.value}")
    return mate


def concentric(asm, a, b, ra, rb, name, lock=False):
    fa = find_cylinder(a, ra[0], ra[1])
    fb = find_cylinder(b, rb[0], rb[1])
    select_two(asm, fa, fb)
    return add_mate(asm, SW_MATE_CONCENTRIC, lock_rotation=lock, name=name)


def coincident_planes(asm, a, b, names, mate_name):
    ea = plane_entity(a, names)
    eb = plane_entity(b, names)
    select_two(asm, ea, eb)
    return add_mate(asm, SW_MATE_COINCIDENT, name=mate_name, align=0)


def fix_component(asm, comp):
    asm.ClearSelection2(True)
    nothing = _nothing()
    name = com(comp, "Name2")
    ok = asm.Extension.SelectByID2(name, "COMPONENT", 0, 0, 0, False, 0, nothing, 0)
    if not ok:
        ok = bool(comp.Select4(False, nothing, False))
    if not ok:
        raise RuntimeError(f"Could not select {name}")
    _flag_methods(asm, ("FixComponent",))
    com(asm, "FixComponent")
    asm.ClearSelection2(True)
    print(f"  fixed {name}")


def load_motion_tlb():
    for path in glob.glob(r"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS*\swmotionstudy.tlb"):
        try:
            tlb = pythoncom.LoadTypeLib(path)
            guid, lcid, _sk, major, minor, _flags = tlb.GetLibAttr()
            win32com.client.gencache.EnsureModule(guid, lcid, major, minor)
            print(f"Loaded motion typelib: {path}")
            return path
        except Exception as exc:
            print(f"  typelib skip {path}: {exc}")
    print("WARNING: swmotionstudy.tlb not loaded; Motion API may be flaky.")
    return None


def motion_call(obj, name, *args):
    member = getattr(obj, name)
    if args:
        if callable(member):
            return member(*args)
        raise TypeError(name)
    try:
        return member() if callable(member) else member
    except Exception as exc:
        if "Member not found" in str(exc) or "-2147352573" in str(exc):
            return member
        raise


def add_rotary_motor(study, direction_ref, load_ref, rpm, relative, name, reverse=False):
    motor = motion_call(study, "CreateDefinition", SW_FM_AEM_ROTATIONAL_MOTOR)
    if motor is None:
        raise RuntimeError("CreateDefinition motor failed")
    motor.DirectionReference = direction_ref
    motion_call(motor, "ConstantSpeedMotor", float(rpm))
    motor.ReverseDirection = bool(reverse)
    if relative is not None:
        motor.RelativeComponent = relative
    try:
        motor.Location = load_ref
    except Exception:
        pass
    refs_ok = False
    for refs in (
        (load_ref,),
        [load_ref],
        win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, [load_ref]),
    ):
        try:
            motor.LoadReferences = refs
            refs_ok = True
            break
        except Exception:
            continue
    if not refs_ok:
        raise RuntimeError("LoadReferences failed")
    feat = motion_call(study, "CreateFeature", motor)
    if feat is None:
        raise RuntimeError("CreateFeature motor failed")
    try:
        feat.Name = name
    except Exception:
        pass
    print(f"  motor {name} @ {rpm} rpm")
    return feat


def main() -> int:
    work_dir = os.path.join(os.environ.get("LOCALAPPDATA", r"C:\Temp"), "LuisSW", "arm_motion")
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arm_motion")
    os.makedirs(work_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)
    print(f"Working files: {work_dir}")

    sw = connect()
    print("Closing leftover arm documents from the last run ...")
    close_prior_arm_docs(sw)
    time.sleep(1.5)
    paths = {
        "base": os.path.join(work_dir, "01_base.sldprt"),
        "shoulder": os.path.join(work_dir, "02_shoulder.sldprt"),
        "upper": os.path.join(work_dir, "03_upper_arm.sldprt"),
        "forearm": os.path.join(work_dir, "04_forearm.sldprt"),
    }
    build_base(sw, paths["base"])
    build_shoulder(sw, paths["shoulder"])
    build_upper_arm(sw, paths["upper"])
    build_forearm(sw, paths["forearm"])

    print("Creating assembly ...")
    asm = new_assembly(sw)
    base = add_component(sw, asm, paths["base"])
    shoulder = add_component(sw, asm, paths["shoulder"])
    upper = add_component(sw, asm, paths["upper"])
    forearm = add_component(sw, asm, paths["forearm"])

    print("Mates ...")
    coincident_planes(asm, base, shoulder, TOP, "J1_axial_top")
    concentric(asm, base, shoulder, (mm(5.7), mm(6.3)), (mm(6.0), mm(6.5)), "J1_yaw", lock=False)
    coincident_planes(asm, shoulder, upper, FRONT, "J2_axial_front")
    concentric(asm, shoulder, upper, (mm(7.7), mm(8.3)), (mm(8.0), mm(8.5)), "J2_pitch", lock=False)
    coincident_planes(asm, upper, forearm, FRONT, "J3_axial_front")
    concentric(asm, upper, forearm, (mm(6.7), mm(7.3)), (mm(7.0), mm(7.5)), "J3_elbow", lock=False)

    fix_component(asm, base)
    try:
        asm.EditRebuild3()
    except Exception:
        pass

    print("Motion study ...")
    load_motion_tlb()
    mgr = com(asm.Extension, "GetMotionStudyManager")
    if mgr is None:
        raise RuntimeError("GetMotionStudyManager returned None")
    study = motion_call(mgr, "CreateMotionStudy")
    if study is None:
        raise RuntimeError("CreateMotionStudy failed")
    try:
        study.Name = "desk_arm_wave"
    except Exception:
        pass
    motion_call(study, "Activate")
    try:
        motion_call(study, "SetDuration", 6.0)
    except Exception:
        pass

    j1_dir = find_cylinder(base, mm(5.7), mm(6.3))
    j1_load = find_cylinder(shoulder, mm(6.0), mm(6.5))
    j2_dir = find_cylinder(shoulder, mm(7.7), mm(8.3))
    j2_load = find_cylinder(upper, mm(8.0), mm(8.5))
    j3_dir = find_cylinder(upper, mm(6.7), mm(7.3))
    j3_load = find_cylinder(forearm, mm(7.0), mm(7.5))

    add_rotary_motor(study, j1_dir, j1_load, 8.0, base, "J1_yaw_8rpm")
    add_rotary_motor(study, j2_dir, j2_load, 6.0, shoulder, "J2_pitch_6rpm", reverse=True)
    add_rotary_motor(study, j3_dir, j3_load, 10.0, upper, "J3_elbow_10rpm")

    try:
        sw.DisplayAlerts = True
    except Exception:
        pass
    calculated = bool(motion_call(study, "Calculate"))
    print(f"Motion Calculate = {calculated}")
    if calculated:
        try:
            motion_call(study, "Play")
            print("Motion Play started — watch the timeline at the bottom of SolidWorks.")
        except Exception as exc:
            print(f"Play skipped: {exc}")

    try:
        asm.ShowNamedView2("*Isometric", 7)
        asm.ViewZoomtofit2()
    except Exception:
        pass

    asm_path = os.path.join(work_dir, "agent_desk_arm.sldasm")
    save_as(asm, asm_path)
    print(f"Wrote {asm_path}")
    try:
        import shutil
        for name in os.listdir(work_dir):
            src = os.path.join(work_dir, name)
            if os.path.isfile(src):
                shutil.copy2(src, os.path.join(out_dir, name))
        print(f"Copied to {out_dir}")
    except Exception as exc:
        print(f"Copy to OneDrive folder skipped: {exc}")
    print("Leaving SolidWorks open.")
    return 0 if calculated else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
