from build_native import ROOT,connect,call,integer_ref
sw=connect(); doc=call(sw,'ActiveDoc'); eq=call(doc,'GetEquationMgr')
print('Config',call(call(call(doc,'ConfigurationManager'),'ActiveConfiguration'),'Name'),flush=True)
print('Set',call(eq,'SetEquationAndConfigurationOption',0,'"Gripper_opening" = 22mm',1,None),flush=True)
for repeat in range(2):
    print('Evaluate',call(eq,'EvaluateAll'),flush=True)
    call(doc,'ForceRebuild3',False)
    for i in range(call(eq,'GetCount')):
        row={}
        for name in ('Equation','Value','GlobalVariable','Disabled'):
            try: row[name]=eq._oleobj_.Invoke(eq._oleobj_.GetIDsOfNames(name),0,2,True,i)
            except Exception as e: row[name]=str(e)[:90]
        print(i,row,flush=True)
    for side in ('right','left'): print(side,call(doc.Parameter('D1@jaw_'+side+'_half_opening'),'SystemValue'),flush=True)
call(eq,'SetEquationAndConfigurationOption',0,'"Gripper_opening" = 32mm',1,None)
call(eq,'EvaluateAll'); call(doc,'ForceRebuild3',False)
call(doc,'Save3',1,integer_ref(),integer_ref())
