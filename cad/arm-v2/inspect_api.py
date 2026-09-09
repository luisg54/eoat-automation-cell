from build_native import pythoncom
import sys
tl = pythoncom.LoadTypeLib(r'C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS (2)\swconst.tlb')
for i in range(tl.GetTypeInfoCount()):
    info = tl.GetTypeInfo(i)
    name = info.GetDocumentation(-1)[0]
    if name in (sys.argv[1:] or ['swAddMateError_e', 'swMateType_e']):
        print(name)
        for n in range(100):
            try:
                desc = info.GetVarDesc(n)
            except pythoncom.com_error:
                break
            print(info.GetDocumentation(desc[0])[0], desc[1])
