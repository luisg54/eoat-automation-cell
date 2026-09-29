"""Read-only SolidWorks connection and installed API inspection."""
import os
import sys
from pathlib import Path

bridge = Path(os.environ['TEMP']) / 'eoat-cad-python'
if bridge.is_dir():
    # Temporary pywin32 bridge used by earlier sessions; an installed pywin32 also works.
    sys.path[:0] = [str(bridge), str(bridge / 'win32'), str(bridge / 'win32/lib')]
    dll_directory = os.add_dll_directory(str(bridge / 'pywin32_system32'))
import pythoncom
import win32com.client
import win32com.client.dynamic

def connect():
    pythoncom.CoInitialize()
    # Late binding keeps VARIANT by-reference arguments working even when a
    # generated SolidWorks type-library cache exists for this Python install.
    active = pythoncom.GetActiveObject('SldWorks.Application')
    return win32com.client.dynamic.Dispatch(active.QueryInterface(pythoncom.IID_IDispatch))

def call(obj, name, *args):
    if args:
        try:
            obj._FlagAsMethod(name)
        except AttributeError:
            pass
    member = getattr(obj, name)
    if hasattr(member, '_oleobj_'):
        return member
    return member(*args) if callable(member) else member

if __name__ == '__main__':
    sw = connect()
    print('Revision:', call(sw, 'RevisionNumber'), flush=True)
    doc = call(sw, 'GetFirstDocument')
    while doc:
        print('Document:', call(doc, 'GetTitle'), 'path:', call(doc, 'GetPathName'),
              'unsaved:', call(doc, 'GetSaveFlag'), flush=True)
        doc = call(doc, 'GetNext')
