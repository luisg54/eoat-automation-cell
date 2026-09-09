import json
from build_fasteners import ROOT,connect,washer,screw
sw=connect()
old=sw.GetUserPreferenceToggle(16)
try:
    sw.SetUserPreferenceToggle(16,False)
    rows=[washer(sw,3),screw(sw,2,25)]
    (ROOT/'build-hardware-update.json').write_text(json.dumps(rows,indent=2))
finally:
    sw.SetUserPreferenceToggle(16,old)
