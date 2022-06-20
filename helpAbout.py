import sys
import parameters
import os
from translation import tr, tr_en
import time

versionMajor = 1
versionMinor = 8
versionDev   = 1

date = "2022.06.20"

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
    py_version = sys.version_info
    return '''-----------------------------------------
<br>
<b>'''+tr("About")+''':</b>
<br><br>
'''+tr("Release with")+" Python" +str(py_version[0]+py_version[1]/10)+ ''' + PyQt5<br><br>
<div><div>'''+parameters.appName+" "+tr("is a Open source project created by")+''' </div><a style="vertical-align: middle;" href="http://www.sipeed.com"><img src="'''+strPath+"/"+parameters.appLogo2+'''" width=109 height=32></img></a><br></div>
''' +tr("Author")+":"+parameters.author+'''<br><br>

'''+tr("See more on")+''' <b><a href="https://github.com/Sipeed/kflash_gui.git">Github</a></b>,  '''+tr("Licensed with")+''' <a href="https://github.com/sipeed/kflash_gui/blob/master/LICENSE">LGPL3.0</a><br><br>


'''+tr("GUI dirived from")+''' <b><a href="https://github.com/Neutree/ComTool.git">ComTool</a></b>,  '''+tr("Licensed with")+''' <a href="https://github.com/Neutree/COMTool/blob/master/LICENSE">LGPL3.0</a>
<br>
-----------------------------------------
'''

