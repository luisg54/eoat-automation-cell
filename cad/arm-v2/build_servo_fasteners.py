import json
from build_fasteners import ROOT,connect,washer,screw,nut
sw=connect(); old=sw.GetUserPreferenceToggle(16)
try:
    sw.SetUserPreferenceToggle(16,False)
    rows=[screw(sw,2.5,14),washer(sw,2.5),nut(sw,2.5,True)]
    (ROOT/'build-servo-fasteners.json').write_text(json.dumps(rows,indent=2))
finally: sw.SetUserPreferenceToggle(16,old)
