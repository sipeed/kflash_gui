import os, sys

appName = "kflash_gui"
author = "Neucrack"
strDataDirName = "kflash_gui_data"
strDataAssetsDirName = "kflash_gui_data/assets"
appIcon = "assets/logo.png"
appLogo = "assets/logo.png"
appLogo2 = "assets/logo2.png"
translationPath = "assets/translation"
configFileName  = "kflash_gui.conf"
configFilePath  = ""

if sys.platform.startswith('linux') or sys.platform.startswith('darwin') or sys.platform.startswith('freebsd'):
    configFileDir = os.path.join(os.getenv("HOME"), ".config/kflash_gui")
    try:
        configFilePath = os.path.join(configFileDir, configFileName)
        if not os.path.exists(configFileDir):
            os.makedirs(configFileDir)
    except:
        pass
else:
    configFilePath  = os.path.join(os.getcwd(), configFileName)



# get data path
pathDirList = sys.argv[0].replace("\\", "/").split("/")
pathDirList.pop()
dataPath = os.path.abspath("/".join(str(i) for i in pathDirList))
if not os.path.exists(dataPath + "/" + strDataDirName):
    pathDirList.pop()
    dataPath = os.path.abspath("/".join(str(i) for i in pathDirList))
dataPath = getattr(sys, '_MEIPASS', dataPath)
dataPath = (dataPath + "/" + strDataDirName).replace("\\", "/")

translationPathAbs = dataPath+"/"+translationPath




