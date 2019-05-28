import os, sys

appName = "kflash_gui"
author = "Neucrack"
strDataDirName = "kflash_gui_data"
strDataAssetsDirName = "kflash_gui_data/assets"
appIcon = "assets/logo.png"
appLogo = "assets/logo.png"
appLogo2 = "assets/logo2.png"
translationPath = "assets/translation"
configFilePath  = "kflash_gui.conf"

SipeedMaixDock = "Sipeed Maix Dock"
SipeedMaixBit  = "Sipeed Maix Bit"
SipeedMaixGo   = "Sipeed Maix Go"
SipeedMaixGoD  = "Sipeed Maix Go( Old CMSIS-DAP )"
SipeedMaixduino= "Sipeed Maixduino"
KendriteKd233  = "Kendryte KD233"

# get data path
pathDirList = sys.argv[0].replace("\\", "/").split("/")
pathDirList.pop()
dataPath = os.path.abspath("/".join(str(i) for i in pathDirList))
if not os.path.exists(dataPath + "/" + strDataDirName):
    pathDirList.pop()
    dataPath = os.path.abspath("/".join(str(i) for i in pathDirList))
dataPath = (dataPath + "/" + strDataDirName).replace("\\", "/")

translationPathAbs = dataPath+"/"+translationPath




