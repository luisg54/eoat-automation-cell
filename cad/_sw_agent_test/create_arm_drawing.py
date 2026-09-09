"""Add COTS hardware to the desk arm and create an assembly drawing.

Requires SolidWorks 2026 with agent_desk_arm open (or the files on disk).
"""

from __future__ import annotations

import importlib.util
import os
import traceback

import pythoncom
import win32com.client

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "arm_motion", os.path.join(HERE, "create_arm_motion.py")
)
arm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(arm)

DRAW_TEMPLATE = r"C:\ProgramData\SolidWorks\SOLIDWORKS 2024\templates\Drawing.DRWDOT"
SHEET_FORMAT = r"C:\ProgramData\SolidWorks\SOLIDWORKS 2024\lang\english\sheetformat\b - landscape.slddrt"
BOM_TEMPLATE = r"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS (2)\lang\english\bom-vendor.sldbomtbt"
WORK_DIR = os.path.join(os.environ.get("LOCALAPPDATA", r"C:\Temp"), "LuisSW", "arm_motion")

SW_DWG_PAPER_B = 2
SW_BOM_ANCHOR_TOP_RIGHT = 2
SW_BOM_TOP_LEVEL = 1
SW_CUSTOM_TEXT = 30


def set_props(model, props):
    cpm = None
    try:
        cpm = model.Extension.CustomPropertyManager("")
    except Exception:
        cpm = None
    for key, value in props.items():
        ok = False
        if cpm is not None:
            for overwrite in (1, 2, 0):
                try:
                    cpm.Add3(key, SW_CUSTOM_TEXT, value, overwrite)
                    ok = True
                    break
                except Exception:
                    continue
        if not ok:
            try:
                model.AddCustomInfo3("", key, SW_CUSTOM_TEXT, value)
            except Exception as exc:
                print(f"    property '{key}' skipped: {exc}")


def tube(model, plane, cx, cy, r_out, r_in, t1, depth, merge=True, flip=False):
    sk = arm.start_sketch(model, plane)
    arm.circle(sk, cx, cy, r_out)
    arm.circle(sk, cx, cy, r_in)
    arm.finish_sketch(sk)
    return arm.boss(model, t1, depth, merge=merge, flip=flip)


def build_shcs(sw, path):
    print("COTS: M6x25 SHCS (4 places) ...")
    model = arm.new_part(sw)
    sk = arm.start_sketch(model, arm.TOP)
    for x, z in ((-40, -40), (40, -40), (-40, 40), (40, 40)):
        arm.circle(sk, arm.mm(x), arm.mm(z), arm.mm(5.0))
    arm.finish_sketch(sk)
    arm.boss(model, arm.SW_END_BLIND, arm.mm(6), merge=True)
    sk = arm.start_sketch(model, arm.TOP)
    for x, z in ((-40, -40), (40, -40), (-40, 40), (40, 40)):
        arm.circle(sk, arm.mm(x), arm.mm(z), arm.mm(3.0))
    arm.finish_sketch(sk)
    arm.boss(model, arm.SW_END_BLIND, arm.mm(25), merge=True, flip=True)
    arm.set_color(model, (0.12, 0.12, 0.12))
    set_props(model, {
        "Description": "SHCS M6 x 25, ISO 4762 (4 places)",
        "Part Number": "ISO 4762-M6x25",
        "Vendor": "McMaster-Carr / Fastenal",
        "Material": "Alloy steel, black oxide",
    })
    model.EditRebuild3()
    return arm.save_part(sw, model, path)


def build_washers(sw, path):
    print("COTS: M6 washers (4 places) ...")
    model = arm.new_part(sw)
    sk = arm.start_sketch(model, arm.TOP)
    for x, z in ((-40, -40), (40, -40), (-40, 40), (40, 40)):
        arm.circle(sk, arm.mm(x), arm.mm(z), arm.mm(6.5))
        arm.circle(sk, arm.mm(x), arm.mm(z), arm.mm(3.2))
    arm.finish_sketch(sk)
    arm.boss(model, arm.SW_END_BLIND, arm.mm(1.6), merge=True)
    arm.set_color(model, (0.55, 0.55, 0.58))
    set_props(model, {
        "Description": "Washer M6, ISO 7089 200 HV (4 places)",
        "Part Number": "ISO 7089-6-200HV",
        "Vendor": "McMaster-Carr / Fastenal",
        "Material": "Steel, zinc plated",
    })
    model.EditRebuild3()
    return arm.save_part(sw, model, path)


def build_j1_bearings(sw, path):
    print("COTS: 6001-2RS bearings (2) ...")
    model = arm.new_part(sw)
    # One 16 mm stack reads as two 8 mm races on the J1 pin.
    tube(model, arm.TOP, 0.0, 0.0, arm.mm(14.0), arm.mm(6.1), arm.SW_END_BLIND, arm.mm(16), merge=True)
    arm.set_color(model, (0.75, 0.78, 0.80))
    set_props(model, {
        "Description": "Radial ball bearing 6001-2RS, 12 x 28 x 8 mm (2 places)",
        "Part Number": "6001-2RS",
        "Vendor": "SKF / NTN / McMaster-Carr",
        "Material": "Chrome steel, RS seals",
    })
    model.EditRebuild3()
    return arm.save_part(sw, model, path)


def build_j2_sleeves(sw, path):
    print("COTS: J2 sleeve bearings (2) ...")
    model = arm.new_part(sw)
    sk = arm.start_sketch(model, arm.FRONT)
    arm.circle(sk, 0.0, arm.mm(76), arm.mm(11.0))
    arm.circle(sk, 0.0, arm.mm(76), arm.mm(8.1))
    arm.finish_sketch(sk)
    arm.boss(model, arm.SW_END_BLIND, arm.mm(36), merge=True, flip=False)
    sk = arm.start_sketch(model, arm.FRONT)
    arm.circle(sk, 0.0, arm.mm(76), arm.mm(11.0))
    arm.circle(sk, 0.0, arm.mm(76), arm.mm(8.1))
    arm.finish_sketch(sk)
    arm.boss(model, arm.SW_END_BLIND, arm.mm(36), merge=True, flip=True)
    arm.set_color(model, (0.72, 0.55, 0.28))
    set_props(model, {
        "Description": "Oil-embedded sleeve 16 x 22 x 12 mm (2 places, J2)",
        "Part Number": "SAE 841-16x22x12",
        "Vendor": "McMaster-Carr",
        "Material": "SAE 841 bronze",
    })
    model.EditRebuild3()
    return arm.save_part(sw, model, path)


def build_j3_sleeves(sw, path):
    print("COTS: J3 sleeve bearings (2) ...")
    model = arm.new_part(sw)
    sk = arm.start_sketch(model, arm.FRONT)
    arm.circle(sk, 0.0, arm.mm(198), arm.mm(10.0))
    arm.circle(sk, 0.0, arm.mm(198), arm.mm(7.1))
    arm.finish_sketch(sk)
    arm.boss(model, arm.SW_END_BLIND, arm.mm(22), merge=True, flip=False)
    sk = arm.start_sketch(model, arm.FRONT)
    arm.circle(sk, 0.0, arm.mm(198), arm.mm(10.0))
    arm.circle(sk, 0.0, arm.mm(198), arm.mm(7.1))
    arm.finish_sketch(sk)
    arm.boss(model, arm.SW_END_BLIND, arm.mm(22), merge=True, flip=True)
    arm.set_color(model, (0.72, 0.55, 0.28))
    set_props(model, {
        "Description": "Oil-embedded sleeve 14 x 20 x 10 mm (2 places, J3)",
        "Part Number": "SAE 841-14x20x10",
        "Vendor": "McMaster-Carr",
        "Material": "SAE 841 bronze",
    })
    model.EditRebuild3()
    return arm.save_part(sw, model, path)


def build_servos(sw, path):
    print("COTS: MG996R servos (3) ...")
    model = arm.new_part(sw)
    # J1 yaw servo beside the column
    sk = arm.start_sketch(model, arm.FRONT)
    arm.rect(sk, arm.mm(28), arm.mm(20), arm.mm(48), arm.mm(60))
    arm.finish_sketch(sk)
    arm.boss(model, arm.SW_END_MIDPLANE, arm.mm(20), merge=True)
    # J2 pitch servo
    sk = arm.start_sketch(model, arm.FRONT)
    arm.rect(sk, arm.mm(22), arm.mm(64), arm.mm(42), arm.mm(100))
    arm.finish_sketch(sk)
    arm.boss(model, arm.SW_END_BLIND, arm.mm(40), merge=True, flip=True)
    # J3 elbow servo
    sk = arm.start_sketch(model, arm.FRONT)
    arm.rect(sk, arm.mm(18), arm.mm(186), arm.mm(40), arm.mm(222))
    arm.finish_sketch(sk)
    arm.boss(model, arm.SW_END_BLIND, arm.mm(36), merge=True, flip=True)
    arm.set_color(model, (0.15, 0.45, 0.22))
    set_props(model, {
        "Description": "Digital servo MG996R metal gear, 4.8-7.2 V (3 places)",
        "Part Number": "MG996R",
        "Vendor": "TowerPro / HiTec equivalent",
        "Material": "Nylon case, metal gears",
    })
    model.EditRebuild3()
    return arm.save_part(sw, model, path)


def build_retaining_rings(sw, path):
    print("COTS: external retaining rings ...")
    model = arm.new_part(sw)
    sk = arm.start_sketch(model, arm.TOP)
    arm.circle(sk, 0.0, 0.0, arm.mm(8.5))
    arm.circle(sk, 0.0, 0.0, arm.mm(6.05))
    arm.finish_sketch(sk)
    arm.boss(model, arm.SW_END_BLIND, arm.mm(1.2), merge=True)
    sk = arm.start_sketch(model, arm.FRONT)
    arm.circle(sk, 0.0, arm.mm(76), arm.mm(10.5))
    arm.circle(sk, 0.0, arm.mm(76), arm.mm(8.05))
    arm.finish_sketch(sk)
    arm.boss(model, arm.SW_END_MIDPLANE, arm.mm(84), merge=True)
    arm.set_color(model, (0.35, 0.35, 0.38))
    set_props(model, {
        "Description": "External retaining rings DIN 471, 12 mm and 16 mm (4 places)",
        "Part Number": "DIN 471-12 / DIN 471-16",
        "Vendor": "McMaster-Carr",
        "Material": "Carbon spring steel",
    })
    model.EditRebuild3()
    return arm.save_part(sw, model, path)


def tag_custom_parts(sw):
    specs = {
        "01_base": {
            "Description": "Base, column, and J1 yaw pin — custom",
            "Part Number": "DA-001",
            "Vendor": "MAKE",
            "Material": "PLA / PETG print, or AL 6061",
        },
        "02_shoulder": {
            "Description": "Shoulder turret and J2 pitch pin — custom",
            "Part Number": "DA-002",
            "Vendor": "MAKE",
            "Material": "PLA / PETG print, or AL 6061",
        },
        "03_upper_arm": {
            "Description": "Upper arm with J2 bore and J3 pin — custom",
            "Part Number": "DA-003",
            "Vendor": "MAKE",
            "Material": "PLA / PETG print, or AL 6061",
        },
        "04_forearm": {
            "Description": "Forearm, wrist, parallel-jaw gripper — custom",
            "Part Number": "DA-004",
            "Vendor": "MAKE",
            "Material": "PLA / PETG print, or AL 6061",
        },
    }
    docs = arm.as_list(arm.com(sw, "GetDocuments"))
    for doc in docs:
        try:
            title = str(arm.com(doc, "GetTitle") or "")
        except Exception:
            continue
        for key, props in specs.items():
            if key in title.lower() or key in title:
                print(f"  tagging {title}")
                set_props(doc, props)


def find_assembly(sw):
    docs = arm.as_list(arm.com(sw, "GetDocuments"))
    for doc in docs:
        try:
            path = str(arm.com(doc, "GetPathName") or "")
            title = str(arm.com(doc, "GetTitle") or "")
        except Exception:
            continue
        if "agent_desk_arm" in path.lower() or "agent_desk_arm" in title.lower():
            if path.lower().endswith(".sldasm") or "sldasm" in title.lower() or "agent_desk_arm" in title.lower():
                if "drw" in title.lower():
                    continue
                return doc
    asm_path = os.path.join(WORK_DIR, "agent_desk_arm.sldasm")
    if os.path.isfile(asm_path):
        err, warn = arm._byref_i4(), arm._byref_i4()
        doc = sw.OpenDoc6(asm_path, arm.SW_DOC_ASSEMBLY, arm.SW_OPEN_SILENT, "", err, warn)
        if doc:
            return doc
    raise RuntimeError("Open agent_desk_arm.sldasm first.")


def already_inserted(asm, stem):
    try:
        names = arm.as_list(arm.com(asm, "GetComponents", False))
    except Exception:
        names = []
    for comp in names:
        try:
            n = str(arm.com(comp, "Name2") or "")
        except Exception:
            continue
        if stem.lower() in n.lower():
            return True
    return False


def add_cots(sw, asm, paths):
    added = []
    for stem, path in paths.items():
        if already_inserted(asm, stem):
            print(f"  already in assembly: {stem}")
            continue
        try:
            arm.add_component(sw, asm, path)
            added.append(stem)
        except Exception as exc:
            print(f"  insert failed {stem}: {exc}")
    return added


def insert_note(draw_model, text, x, y, height=0.003):
    try:
        draw_model.FontSize = height
    except Exception:
        pass
    note = None
    try:
        note = draw_model.InsertNote(text)
    except Exception:
        try:
            note = draw_model.Extension.InsertNote(text)
        except Exception as exc:
            print(f"  note skipped: {exc}")
            return None
    if note is None:
        return None
    try:
        ann = note.GetAnnotation()
        if callable(ann):
            ann = ann()
        ann.SetPosition2(x, y, 0)
    except Exception:
        pass
    return note


def create_drawing(sw, asm):
    asm_path = arm.com(asm, "GetPathName")
    if not asm_path:
        raise RuntimeError("Assembly has no path; save it first.")
    print("Creating B-size drawing ...")
    draw = sw.NewDocument(DRAW_TEMPLATE, SW_DWG_PAPER_B, 0.4318, 0.2794)
    if draw is None:
        raise RuntimeError("New drawing failed")
    arm._flag_methods(
        draw,
        (
            "CreateDrawViewFromModelView3",
            "Create3rdAngleViews2",
            "CreateUnfoldedViewAt3",
            "SetupSheet5",
            "AutoBalloon5",
            "ActivateView",
            "InsertNote",
        ),
    )
    try:
        draw.SetupSheet5(
            "Sheet1", SW_DWG_PAPER_B, SHEET_FORMAT, 1, 2, False, 0.4318, 0.2794, "", True
        )
    except Exception as exc:
        print(f"  SetupSheet5: {exc}")

    print("  3rd-angle views ...")
    try:
        draw.Create3rdAngleViews2(asm_path)
    except Exception as exc:
        print(f"  Create3rdAngleViews2: {exc}")
        draw.CreateDrawViewFromModelView3(asm_path, "*Front", 0.12, 0.16, 0)

    print("  isometric ...")
    iso = draw.CreateDrawViewFromModelView3(asm_path, "*Isometric", 0.30, 0.15, 0)
    try:
        if iso:
            iso.ScaleDecimal = 0.45
    except Exception:
        pass

    print("  BOM ...")
    bom_template = BOM_TEMPLATE
    if not os.path.isfile(bom_template):
        bom_template = r"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\lang\english\bom-standard.sldbomtbt"
    view = iso
    if view is None:
        try:
            view = draw.GetFirstView().GetNextView
        except Exception:
            view = None
    if view is not None:
        try:
            bom = view.InsertBomTable3(
                False, 0.355, 0.250, SW_BOM_ANCHOR_TOP_RIGHT,
                SW_BOM_TOP_LEVEL, "", bom_template, False,
            )
            print(f"  BOM inserted: {bom is not None}")
        except Exception as exc:
            print(f"  InsertBomTable3: {exc}")
            try:
                bom = view.InsertBomTable2(
                    False, 0.355, 0.250, SW_BOM_ANCHOR_TOP_RIGHT,
                    SW_BOM_TOP_LEVEL, "", bom_template,
                )
                print(f"  BOM InsertBomTable2: {bom is not None}")
            except Exception as exc2:
                print(f"  BOM failed: {exc2}")

    print("  balloons ...")
    try:
        draw.ClearSelection2(True)
        nothing = arm._nothing()
        draw.Extension.SelectByID2("Drawing View1", "DRAWINGVIEW", 0, 0, 0, False, 0, nothing, 0)
        if iso:
            try:
                iso.Select(False)
            except Exception:
                pass
        draw.AutoBalloon5(1, False, False, False, 1, 1, 0, 1, 2, 1, "", 0, "", "", 0)
        print("  AutoBalloon5 done")
    except Exception as exc:
        print(f"  AutoBalloon5: {exc}")

    notes = (
        "DESK ARM ASSEMBLY\n"
        "Drawn: L. Garcia Rivera   2026-09-04\n"
        "Scale 1:2   3rd angle   B-size\n"
        "Demo CAD — not EOAT cell.\n"
        "\n"
        "MAKE: DA-001 base, DA-002 shoulder,\n"
        "DA-003 upper arm, DA-004 forearm.\n"
        "\n"
        "COTS (or equivalent):\n"
        "4x SHCS M6x25 ISO 4762\n"
        "4x washer M6 ISO 7089\n"
        "2x bearing 6001-2RS (J1)\n"
        "2x sleeve 16x22x12 SAE 841 (J2)\n"
        "2x sleeve 14x20x10 SAE 841 (J3)\n"
        "4x retaining ring DIN 471-12/16\n"
        "3x servo MG996R\n"
        "Loctite 243 on M6 threads.\n"
        "Print infill 30% gyroid or machine 6061."
    )
    insert_note(draw, notes, 0.018, 0.095, 0.0028)

    set_props(draw, {
        "Title": "Desk Arm Assembly",
        "DrawnBy": "L. Garcia Rivera",
        "Date": "2026-09-04",
        "Revision": "A",
    })
    try:
        draw.ForceRebuild3(False)
    except Exception:
        pass
    return draw


def main() -> int:
    os.makedirs(WORK_DIR, exist_ok=True)
    sw = arm.connect()
    try:
        sw.DisplayAlerts = False
    except Exception:
        pass

    asm = find_assembly(sw)
    arm.activate(sw, asm)
    print(f"Assembly: {arm.com(asm, 'GetTitle')}")

    tag_custom_parts(sw)
    arm.activate(sw, asm)

    cots = {
        "cots_shcs_m6x25": os.path.join(WORK_DIR, "cots_shcs_m6x25.sldprt"),
        "cots_washer_m6": os.path.join(WORK_DIR, "cots_washer_m6.sldprt"),
        "cots_bearing_6001": os.path.join(WORK_DIR, "cots_bearing_6001.sldprt"),
        "cots_sleeve_j2": os.path.join(WORK_DIR, "cots_sleeve_j2.sldprt"),
        "cots_sleeve_j3": os.path.join(WORK_DIR, "cots_sleeve_j3.sldprt"),
        "cots_servo_mg996": os.path.join(WORK_DIR, "cots_servo_mg996.sldprt"),
        "cots_retaining_rings": os.path.join(WORK_DIR, "cots_retaining_rings.sldprt"),
    }
    builders = {
        "cots_shcs_m6x25": build_shcs,
        "cots_washer_m6": build_washers,
        "cots_bearing_6001": build_j1_bearings,
        "cots_sleeve_j2": build_j2_sleeves,
        "cots_sleeve_j3": build_j3_sleeves,
        "cots_servo_mg996": build_servos,
        "cots_retaining_rings": build_retaining_rings,
    }
    for stem, path in cots.items():
        if os.path.isfile(path) and already_inserted(asm, stem):
            print(f"  skip rebuild {stem}")
            continue
        builders[stem](sw, path)
        arm.activate(sw, asm)

    print("Inserting COTS into assembly ...")
    add_cots(sw, asm, cots)
    arm.activate(sw, asm)
    try:
        asm.EditRebuild3()
    except Exception:
        pass
    arm.save_as(asm, os.path.join(WORK_DIR, "agent_desk_arm.sldasm"))

    draw = create_drawing(sw, asm)
    drw_path = os.path.join(WORK_DIR, "agent_desk_arm.slddrw")
    pdf_path = os.path.join(WORK_DIR, "agent_desk_arm.pdf")
    arm.save_as(draw, drw_path)
    try:
        arm.save_as(draw, pdf_path)
        print(f"PDF: {pdf_path}")
    except Exception as exc:
        print(f"PDF export skipped: {exc}")

    try:
        sw.DisplayAlerts = True
    except Exception:
        pass
    print(f"Drawing: {drw_path}")
    print("Leaving SolidWorks open on the drawing.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
