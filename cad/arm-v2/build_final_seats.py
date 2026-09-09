import json
from build_arm_parts import ROOT,connect,upper,keeper
from build_fasteners import screw,washer,nut
sw=connect(); old=sw.GetUserPreferenceToggle(16)
try:
    sw.SetUserPreferenceToggle(16,False)
    rows=[]
    for fn in [lambda:upper(sw),lambda:keeper(sw),lambda:screw(sw,2.5,14),
               lambda:washer(sw,2.5),lambda:nut(sw,2.5,True)]:
        rows.append(fn())
        (ROOT/'build-final-seats.json').write_text(json.dumps(rows,indent=2))
finally: sw.SetUserPreferenceToggle(16,old)
