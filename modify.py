import os
from tkinter import filedialog

header="""G04 Layer: TopLayer*
G04 EasyEDA v6.5.9, 2022-08-01 21:18:00*
G04 ac5e******************************************aa,10*
G04 Gerber Generator version 0.2*
G04 Scale: 100 percent, Rotated: No, Reflected: No *
G04 Dimensions in millimeters *
G04 leading zeros omitted , absolute positions ,4 integer and 5 decimal *\n"""
path = r"C:/Users/lol/Desktop/xxxxxx"
textFile="""如何进行PCB下单

请查看：
https://docs.lceda.cn/cn/PCB/Order-PCB"""
textFileName="PCB下单必读.txt"

currentDir=os.listdir(path)
for file in currentDir:
    if os.path.splitext(file)[-1][1:].lower() == "gbl":
        os.rename(os.path.join(path,file),os.path.join(path,"Gerber_BottomLayer.GBL"))
    if os.path.splitext(file)[-1][1:].lower() == "gko":
        os.rename(os.path.join(path,file),os.path.join(path,"Gerber_BoardOutlineLayer.GKO"))
    if os.path.splitext(file)[-1][1:].lower() == "gbp":
        os.rename(os.path.join(path,file),os.path.join(path,"Gerber_BottomPasteMaskLayer.GBP"))
    if os.path.splitext(file)[-1][1:].lower() == "gbo":
        os.rename(os.path.join(path,file),os.path.join(path,"Gerber_BottomSilkscreenLayer.GBO"))
    if os.path.splitext(file)[-1][1:].lower() == "gbs":
        os.rename(os.path.join(path,file),os.path.join(path,"Gerber_BottomSolderMaskLayer.GBS"))
    if os.path.splitext(file)[-1][1:].lower() == "gtl":
        os.rename(os.path.join(path,file),os.path.join(path,"Gerber_TopLayer.GTL"))
    if os.path.splitext(file)[-1][1:].lower() == "gtp":
        os.rename(os.path.join(path,file),os.path.join(path,"Gerber_TopPasteMaskLayer.GTP"))
    if os.path.splitext(file)[-1][1:].lower() == "gto":
        os.rename(os.path.join(path,file),os.path.join(path,"Gerber_TopSilkscreenLayer.GTO"))
    if os.path.splitext(file)[-1][1:].lower() == "gts":
        os.rename(os.path.join(path,file),os.path.join(path,"Gerber_TopSolderMaskLayer.GTS"))

    if file.find("_PCB-PTH")!=-1 or file.find("_PCB-PTH")!=-1:
        os.rename(os.path.join(path,file),os.path.join(path,"Drill_PTH_Through.DRL"))
    if file.find("_PCB-NPTH")!=-1 or file.find("_PCB-NPTH")!=-1:
        os.rename(os.path.join(path,file),os.path.join(path,"Drill_NPTH_Through.DRL"))
    if file.find("_PCB-In1_Cu")!=-1 or file.find("_PCB-In1_Cu")!=-1:
        os.rename(os.path.join(path,file),os.path.join(path,"Gerber_InnerLayer1.G1"))
    if file.find("_PCB-In2_Cu")!=-1 or file.find("_PCB-In2_Cu")!=-1:
        os.rename(os.path.join(path,file),os.path.join(path,"Gerber_InnerLayer2.G2"))
    if file.find("_PCB-Edge_Cuts")!=-1 or file.find("_PCB-Edge_Cuts")!=-1:
        os.rename(os.path.join(path,file),os.path.join(path,"Gerber_BoardOutlineLayer.GKO"))

currentDir=os.listdir(path)
for file in currentDir:
    fileType=os.path.splitext(file)[-1][1:].lower()
    if fileType!="txt" and fileType!="py":
        f=open(os.path.join(path,file),"r")
        fileData=f.read()
        f.close()
        f=open(os.path.join(path,file),"w")
        print(fileData)
        f.write(header)
        f.write(fileData)
        f.close()

file=open(textFileName,"w")
file.write(textFile)
file.close()



    
