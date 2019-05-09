import sys
try:
    import parameters
except ImportError:
    from COMTool import parameters
import os

versionMajor = 0
versionMinor = 1
versionDev   = 0
date = "2019.5.09"

def strAbout():
    pathDirList = sys.argv[0].replace("\\", "/").split("/")
    pathDirList.pop()
    strPath = os.path.abspath("/".join(str(i) for i in pathDirList))
    if not os.path.exists(strPath + "/" + parameters.strDataDirName):
        pathDirList.pop()
        strPath = os.path.abspath("/".join(str(i) for i in pathDirList))
    strPath = (strPath + "/" + parameters.strDataDirName).replace("\\", "/")
    print(strPath)
    a =strPath+"/"+parameters.appLogo2
    print(a)
    return '''\
Python 3 + PyQt5<br><br>
<div><div>'''+parameters.appName+''' is a Open source project create by </div><a style="vertical-align: middle;" href="http://www.sipeed.com"><img src="'''+strPath+"/"+parameters.appLogo2+'''" width=109 height=32></img></a><br></div>
author: '''+parameters.author+'''<br><br>

See more on <b><a href="https://github.com/Sipeed/kflash_gui.git">Github</a></b>, Licensed with <a href="https://github.com/sipeed/kflash_gui/blob/master/LICENSE">LGPL3.0</a><br><br>


GUI dirived from <b><a href="https://github.com/Neutree/ComTool.git">ComTool</a></b>, Licensed with <a href="https://github.com/Neutree/COMTool/blob/master/LICENSE">LGPL3.0</a>

'''

