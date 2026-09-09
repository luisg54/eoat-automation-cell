"""Add native sketch constraints, preserving a backup and checking solid geometry."""
import json,shutil,sys
from datetime import datetime
from build_native import ROOT,connect,call,integer_ref,nothing
sw=connect()
backup=ROOT/'development-debug'/('before-sketch-constraints-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir(parents=True)
pattern=sys.argv[1] if len(sys.argv)>1 else 'ARM-*.SLDPRT'
report_path=ROOT/'sketch-constraint-report.json'
rows=json.loads(report_path.read_text()) if report_path.exists() else []
old=sw.GetUserPreferenceToggle(16)
try:
    sw.SetUserPreferenceToggle(16,False)
    for path in sorted((ROOT/'parts').glob(pattern)):
        if path.suffix.lower()!='.sldprt': continue
        shutil.copy2(path,backup/path.name)
        doc=sw.OpenDoc6(str(path),1,1,'',integer_ref(),integer_ref())
        if doc is None: raise RuntimeError('Could not open '+str(path))
        sw.ActivateDoc3(str(path),True,0,integer_ref())
        mp=call(doc.Extension,'CreateMassProperty')
        before_volume=call(mp,'Volume')
        before_box=list(call(doc,'GetPartBox',True))
        sketches={}
        def collect(feature):
            while feature:
                if call(feature,'GetTypeName2')=='ProfileFeature':
                    sketches[call(feature,'Name')]=feature
                sub=call(feature,'GetFirstSubFeature')
                if sub: collect_sub(sub)
                feature=call(feature,'GetNextFeature')
        def collect_sub(feature):
            while feature:
                if call(feature,'GetTypeName2')=='ProfileFeature':
                    sketches[call(feature,'Name')]=feature
                feature=call(feature,'GetNextSubFeature')
        collect(call(doc,'FirstFeature'))
        row={'file':path.name,'sketches':[]}
        for name,feature in sketches.items():
            sketch=call(feature,'GetSpecificFeature2')
            initial=call(sketch,'GetConstrainedStatus')
            if initial!=3:
                call(doc,'ClearSelection2',True)
                if not feature.Select2(False,0): raise RuntimeError('Cannot select '+name)
                call(doc,'EditSketch')
                call(doc,'ClearSelection2',True)
                if not doc.Extension.SelectByID2('Point1@Origin','EXTSKETCHPOINT',0.,0.,0.,False,6,nothing(),0):
                    raise RuntimeError('Sketch origin selection failed')
                origin=call(doc.SelectionManager,'GetSelectedObject6',1,6)
                call(doc.SketchManager,'FullyDefineSketch',True,True,518,True,1,origin,1,origin,1,1)
                doc.SketchManager.InsertSketch(True)
            status=call(sketch,'GetConstrainedStatus')
            row['sketches'].append({'name':name,'before':initial,'after':status})
            print(path.stem,name,initial,'->',status,flush=True)
            if status!=3: raise RuntimeError('Sketch not fully constrained: '+name)
        call(doc,'EditRebuild3')
        after=call(doc.Extension,'CreateMassProperty')
        volume=call(after,'Volume')
        box=list(call(doc,'GetPartBox',True))
        if abs(volume-before_volume)>max(1e-12,before_volume*1e-6) or max(abs(a-b) for a,b in zip(box,before_box))>1e-6:
            raise RuntimeError('Geometry changed while constraining '+path.name)
        if not call(doc,'Save3',1,integer_ref(),integer_ref()): raise RuntimeError('Save failed')
        row['solid_geometry_unchanged']=True
        rows=[r for r in rows if r['file']!=row['file']]+[row]
        (ROOT/'sketch-constraint-report.json').write_text(json.dumps(rows,indent=2))
        sw.CloseDoc(str(path))
finally:
    sw.SetUserPreferenceToggle(16,old)
