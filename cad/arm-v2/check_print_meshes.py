"""Check each individual binary STL without a large mesh dependency."""
import json, struct, math
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def inspect(path):
    data=path.read_bytes()
    count=struct.unpack_from('<I',data,80)[0]
    if len(data)!=84+50*count:
        raise ValueError('Not a complete binary STL: '+str(path))
    edges=Counter()
    lo=[math.inf]*3; hi=[-math.inf]*3
    volume=0.
    for i in range(count):
        f=struct.unpack_from('<12fH',data,84+i*50)
        v=[tuple(round(x,5) for x in f[j:j+3]) for j in (3,6,9)]
        for p in v:
            for k in range(3):
                lo[k]=min(lo[k],p[k]); hi[k]=max(hi[k],p[k])
        for a,b in ((0,1),(1,2),(2,0)):
            edges[tuple(sorted((v[a],v[b])))]+=1
        a,b,c=v
        volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
    return {'file':str(path.relative_to(ROOT)), 'triangles':count,
        'dimensions_in_file_units':[round(hi[i]-lo[i],4) for i in range(3)],
        'signed_volume_in_file_units_cubed':volume,
        'boundary_edges':sum(n==1 for n in edges.values()),
        'nonmanifold_edges':sum(n>2 for n in edges.values())}

if __name__=='__main__':
    rows=[]
    for path in sorted((ROOT/'parts').glob('*.STL')):
        if ' - ' not in path.name:
            rows.append(inspect(path))
    (ROOT/'mesh-inspection.json').write_text(json.dumps(rows,indent=2))
    for row in rows: print(row)
