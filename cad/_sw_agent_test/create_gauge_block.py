"""SolidWorks COM smoke test.

Creates a 25 x 20 x 10 mm block in SolidWorks 2024, measures the bounding box,
and exports STL + STEP. Leaves SolidWorks open so the part can be inspected.

This is a connectivity test, not EOAT geometry.
"""

from __future__ import annotations

import os
import sys
import traceback

import pythoncom
import win32com.client

# 2026 is the registered COM server. Its default Part.PRTDOT is missing, so
# use the 2024 part template (SW will upgrade it on open).
TEMPLATE = r"C:\ProgramData\SolidWorks\SOLIDWORKS 2024\templates\Part.PRTDOT"
TEMPLATE_FALLBACK = r"C:\ProgramData\SolidWorks\SOLIDWORKS 2026\templates\MBD\part 0011mm to 0050mm.prtdot"
PROGID = "SldWorks.Application"  # SolidWorks 2026

# Meters (SolidWorks API units)
WIDTH = 0.025
HEIGHT = 0.020
THICKNESS = 0.010
TOL_M = 1e-6  # 0.001 mm

# swUserPreferenceToggle_e.swInputDimValOnCreate
SW_INPUT_DIM_VAL_ON_CREATE = 16
# swSaveAsVersion_e.swSaveAsCurrentVersion
SW_SAVE_AS_CURRENT_VERSION = 0
# swSaveAsOptions_e.swSaveAsOptions_Silent | Copy
SW_SAVE_AS_SILENT = 1
# swDocumentTypes_e.swDocPART
SW_DOC_PART = 1


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
    sw = None
    try:
        sw = win32com.client.GetActiveObject(PROGID)
        print("Attached to a SolidWorks instance that was already open.")
    except Exception:
        print("No running SolidWorks COM server. Open SolidWorks from the Start menu,")
        print("dismiss any activation dialog, then re-run this script.")
        raise RuntimeError(
            "SolidWorks is not available as a COM server. "
            "A Product Activation window is the usual cause."
        )
    sw.Visible = True
    sw.UserControl = True
    try:
        sw.SetUserPreferenceToggle(SW_INPUT_DIM_VAL_ON_CREATE, False)
    except Exception:
        pass
    return sw


def bbox_m(model):
    box = model.GetPartBox(True)
    # xmin, ymin, zmin, xmax, ymax, zmax (meters)
    return [float(v) for v in box]


def save_as(model, path):
    err = _byref_i4()
    warn = _byref_i4()
    ok = model.Extension.SaveAs(
        path, SW_SAVE_AS_CURRENT_VERSION, SW_SAVE_AS_SILENT, _nothing(), err, warn
    )
    if not ok:
        raise RuntimeError(f"SaveAs failed for {path} (err={err.value}, warn={warn.value})")


def main() -> int:
    out_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(out_dir, exist_ok=True)
    sldprt = os.path.join(out_dir, "agent_gauge_25x20x10.sldprt")
    stl = os.path.join(out_dir, "agent_gauge_25x20x10.stl")
    step = os.path.join(out_dir, "agent_gauge_25x20x10.step")

    print(f"Connecting to {PROGID} ...")
    sw = connect()
    rev = sw.RevisionNumber
    print(f"Connected. RevisionNumber = {rev}")

    template = TEMPLATE if os.path.isfile(TEMPLATE) else TEMPLATE_FALLBACK
    if not os.path.isfile(template):
        raise FileNotFoundError(template)

    print(f"New part from template:\n  {template}")
    model = sw.NewDocument(template, 0, 0, 0)
    if model is None:
        print("NewDocument returned None; trying NewPart() ...")
        model = sw.NewPart()
    if model is None:
        raise RuntimeError("Could not create a part. Check the SolidWorks license dialog.")

    _flag_methods(
        model,
        ("EditRebuild3", "ForceRebuild3", "GetPartBox", "ClearSelection2", "SaveAs3"),
    )
    _flag_methods(
        model.Extension,
        ("SelectByID2", "SaveAs", "CreateMassProperty2"),
    )
    _flag_methods(
        model.FeatureManager,
        ("FeatureExtrusion2", "FeatureExtrusion3"),
    )

    model.ClearSelection2(True)
    nothing = _nothing()
    selected = False
    for plane_name in ("Front Plane", "Front", "Plane1"):
        selected = model.Extension.SelectByID2(
            plane_name, "PLANE", 0.0, 0.0, 0.0, False, 0, nothing, 0
        )
        if selected:
            print(f"Selected plane: {plane_name}")
            break
    if not selected:
        raise RuntimeError("Could not select Front Plane (locale / template mismatch).")

    sk = model.SketchManager
    sk.AddToDB = True
    sk.InsertSketch(True)
    model.ClearSelection2(True)
    rect = sk.CreateCornerRectangle(0, 0, 0, WIDTH, HEIGHT, 0)
    if rect is None:
        raise RuntimeError("CreateCornerRectangle failed.")
    sk.AddToDB = False

    feat = model.FeatureManager.FeatureExtrusion2(
        True, False, False, 0, 0, THICKNESS, 0.0,
        False, False, False, False, 1.74532925199433e-2, 1.74532925199433e-2,
        False, False, False, False,
        True, True, True, 0, 0, False,
    )
    if feat is None:
        raise RuntimeError("FeatureExtrusion2 failed.")

    model.EditRebuild3()
    box = bbox_m(model)
    dx = box[3] - box[0]
    dy = box[4] - box[1]
    dz = box[5] - box[2]
    dims_mm = (dx * 1000, dy * 1000, dz * 1000)
    print(
        f"Bounding box mm: {dims_mm[0]:.4f} x {dims_mm[1]:.4f} x {dims_mm[2]:.4f}"
    )

    expected = sorted([WIDTH, HEIGHT, THICKNESS])
    measured = sorted([dx, dy, dz])
    ok = all(abs(a - b) < TOL_M for a, b in zip(expected, measured))
    print(f"Measure check vs 25 x 20 x 10 mm: {'PASS' if ok else 'FAIL'}")
    if not ok:
        print(f"  expected m {expected}")
        print(f"  measured m {measured}")

    print("Saving SLDPRT / STL / STEP ...")
    save_as(model, sldprt)
    save_as(model, stl)
    save_as(model, step)
    print(f"Wrote:\n  {sldprt}\n  {stl}\n  {step}")
    print("Leaving SolidWorks open.")
    return 0 if ok else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
