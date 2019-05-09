import sys, os, parameters

pathDirList = sys.argv[0].replace("\\", "/").split("/")
pathDirList.pop()
DataPath = os.path.abspath("/".join(str(i) for i in pathDirList))
if not os.path.exists(DataPath + "/" + parameters.strDataDirName):
    pathDirList.pop()
    DataPath = os.path.abspath("/".join(str(i) for i in pathDirList))
DataPath = (DataPath + "/" + parameters.strDataDirName).replace("\\", "/")

print(DataPath)
