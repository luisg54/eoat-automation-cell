"""Lightweight nominal fastener envelopes. Threads omitted; do not print these."""
import json
import math
from build_arm_parts import Part,ROOT,connect,round_feature

def screw(sw,d,L):
    p=Part(sw,f'HW-S_M{d}x{L}_socket_ENVELOPE')
    head_d,head_h={2:(3.8,2),2.5:(4.5,2.5),3:(5.5,3),4:(7,4)}[d]
    round_feature(p,'Shank_nominal_thread_envelope',0,0,d,L,offset=-L)
    round_feature(p,'Socket_head_envelope',0,0,head_d,head_h)
    return p.save(True)

def washer(sw,d):
    p=Part(sw,f'HW-W_M{d}_washer_0p5_ENVELOPE')
    round_feature(p,'Washer_M3_small_series_OD6' if d==3 else 'Washer',0,0,8 if d==4 else 6 if d==3 else 5,.5,d+.2)
    return p.save(True)

def low_head_screw(sw,L=10):
    p=Part(sw,f'HW-S_M2x{L}_LOW_HEAD_D4_H1p1_ENVELOPE')
    round_feature(p,'M2_thread_envelope',0,0,2,L,offset=-L)
    round_feature(p,'Verified_low_head_D4_H1p1',0,0,4,1.1)
    return p.save(True)

def nut(sw,d,nyloc=False):
    h=({2.5:3.5,3:4,4:5}[d] if nyloc else {2:1.6,2.5:2.,3:2.4,4:3.2}[d])
    af={2:4,2.5:5,3:5.5,4:7}[d]
    p=Part(sw,f'HW-N_M{d}_'+('nyloc' if nyloc else 'hex')+'_ENVELOPE')
    p.sketch('Across_flats_'+str(af))
    r=af/math.sqrt(3)
    pts=[(r*math.cos(i*math.pi/3),r*math.sin(i*math.pi/3)) for i in range(6)]
    for (x,y),(xx,yy) in zip(pts,pts[1:]+pts[:1]):
        p.sk.CreateLine(x/1000,y/1000,0.,xx/1000,yy/1000,0.)
    p.circle(0,0,d/2)
    p.extrude('Nut_thread_envelope_height_'+str(h),h)
    return p.save(True)

if __name__=='__main__':
    import sys
    sw=connect()
    old=sw.GetUserPreferenceToggle(16)
    try:
        sw.SetUserPreferenceToggle(16,False)
        rows=[]
        if '--revision-c-only' in sys.argv:
            rows=[low_head_screw(sw,10),screw(sw,2,30),screw(sw,3,45)]
            (ROOT/'build-fasteners-c.json').write_text(json.dumps(rows,indent=2))
            sys.exit(0)
        for d,L in [(2,8),(2,10),(2,14),(2,20),(2,25),(2,30),(2.5,14),(3,12),(3,16),(3,30),(3,40),(3,45),(3,50)]:
            rows.append(screw(sw,d,L))
        for d in (2,2.5,3):
            rows.append(washer(sw,d))
            rows.append(nut(sw,d))
        rows.append(low_head_screw(sw,10))
        rows.append(nut(sw,3,True))
        rows.append(nut(sw,2.5,True))
        (ROOT/'build-fasteners.json').write_text(json.dumps(rows,indent=2))
    finally:
        sw.SetUserPreferenceToggle(16,old)
