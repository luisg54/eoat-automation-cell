"""Read-only SolidWorks connection and installed API inspection."""
import os
import sys
from pathlib import Path

bridge = Path(os.environ['TEMP']) / 'eoat-cad-python'
sys.path[:0] = [str(bridge), str(bridge / 'win32'), str(bridge / 'win32/lib')]
dll_directory = os.add_dll_directory(str(bridge / 'pywin32_system32'))
import pythoncom
import win32com.client

def connect():
    pythoncom.CoInitialize()
    return win32com.client.GetActiveObject('SldWorks.Application')

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
