from build_native import ROOT,connect,call,integer_ref
sw=connect(); doc=sw.OpenDoc6(str(ROOT/'ARM-B_Articulated_prototype_DEVELOPMENT.SLDASM'),2,1,'',integer_ref(),integer_ref())
for name in ['Mount_elbow_servo','Mount_shoulder_horn','Mount_elbow_sleeve_0','J2_shoulder_axis','J2_shoulder_axial']:
    f=doc.FeatureByName(name)
    print(name,call(f,'GetTypeName2'),flush=True)
    specific=call(f,'GetSpecificFeature2')
    print('Type',call(specific,'Type'),flush=True)
    for i in range(2):
        e=call(specific,'MateEntity',i)
        print('ref',call(call(e,'ReferenceComponent'),'Name2'),flush=True)
