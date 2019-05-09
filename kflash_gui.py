

import sys,os
import parameters,helpAbout,autoUpdate
from Combobox import ComboBox

# from COMTool.wave import Wave
from PyQt5.QtCore import pyqtSignal,Qt
from PyQt5.QtWidgets import (QApplication, QWidget,QToolTip,QPushButton,QMessageBox,QDesktopWidget,QMainWindow,
                             QVBoxLayout,QHBoxLayout,QGridLayout,QLabel,
                             QLineEdit,QGroupBox,QSplitter,QFileDialog)
from PyQt5.QtGui import QIcon,QFont,QTextCursor,QPixmap
import serial
import serial.tools.list_ports
import threading
import time
import binascii,re
try:
  import cPickle as pickle
except ImportError:
  import pickle
if sys.platform == "win32":
    import ctypes
from  kflash_py.kflash import KFlash

class MyClass(object):
    def __init__(self, arg):
        super(MyClass, self).__init__()
        self.arg = arg

class MainWindow(QMainWindow):
    errorSignal = pyqtSignal(str, str)
    updateProgressSignal = pyqtSignal(str, int, int, str)
    showSerialComboboxSignal = pyqtSignal()
    isDetectSerialPort = False
    DataPath = "./"
    app = None

    def __init__(self,app):
        super().__init__()
        self.app = app
        self.initVar()
        self.initWindow()
        self.initEvent()
        self.programStartGetSavedParameters()

    def __del__(self):
        pass

    def initVar(self):
        self.burning = False
        pathDirList = sys.argv[0].replace("\\", "/").split("/")
        pathDirList.pop()
        self.DataPath = os.path.abspath("/".join(str(i) for i in pathDirList))
        if not os.path.exists(self.DataPath + "/" + parameters.strDataDirName):
            pathDirList.pop()
            self.DataPath = os.path.abspath("/".join(str(i) for i in pathDirList))
        self.DataPath = (self.DataPath + "/" + parameters.strDataDirName).replace("\\", "/")

    def initWindow(self):
        QToolTip.setFont(QFont('SansSerif', 10))
        # main layout
        frameWidget = QWidget()
        mainWidget = QSplitter(Qt.Horizontal)
        frameLayout = QVBoxLayout()
        self.settingWidget = QWidget()
        settingLayout = QVBoxLayout()
        self.settingWidget.setProperty("class","settingWidget")
        mainLayout = QVBoxLayout()
        self.settingWidget.setLayout(settingLayout)
        mainLayout.addWidget(self.settingWidget)
        mainLayout.setStretch(0,2)
        menuLayout = QHBoxLayout()
        self.downloadWidget = QWidget()
        downloadLayout = QVBoxLayout()
        self.downloadWidget.setProperty("class","downloadWidget")
        self.downloadWidget.setLayout(downloadLayout)

        mainWidget.setLayout(mainLayout)
        # menu
        # -----
        # settings and others
        # -----
        # download button
        # -----
        # status bar
        frameLayout.addLayout(menuLayout)
        frameLayout.addWidget(mainWidget)
        frameLayout.addWidget(self.downloadWidget)
        frameWidget.setLayout(frameLayout)
        self.setCentralWidget(frameWidget)

        # option layout
        self.skinButton = QPushButton("")
        self.aboutButton = QPushButton()
        self.skinButton.setProperty("class", "menuItem2")
        self.aboutButton.setProperty("class", "menuItem3")
        self.skinButton.setObjectName("menuItem")
        self.aboutButton.setObjectName("menuItem")
        menuLayout.addWidget(self.skinButton)
        menuLayout.addWidget(self.aboutButton)
        menuLayout.addStretch(0)
        
        # widgets file select
        fileSelectGroupBox = QGroupBox(parameters.strSelectFile)
        settingLayout.addWidget(fileSelectGroupBox)
        fileSelectLayout = QHBoxLayout()
        fileSelectGroupBox.setLayout(fileSelectLayout)
        self.filePathWidget = QLineEdit()
        self.openFileButton = QPushButton(parameters.strOpenFile)
        fileSelectLayout.addWidget(self.filePathWidget)
        fileSelectLayout.addWidget(self.openFileButton)

        # widgets board select
        boardSettingsGroupBox = QGroupBox(parameters.strBoardSettings)
        settingLayout.addWidget(boardSettingsGroupBox)
        boardSettingsLayout = QGridLayout()
        boardSettingsGroupBox.setLayout(boardSettingsLayout)
        self.boardLabel = QLabel(parameters.strBoard)
        self.boardCombobox = ComboBox()
        self.boardCombobox.addItem(parameters.strSipeedMaixDock)
        self.boardCombobox.addItem(parameters.strSipeedMaixBit )
        self.boardCombobox.addItem(parameters.strSipeedMaixGoE )
        self.boardCombobox.addItem(parameters.strSipeedMaixGoD )
        self.boardCombobox.addItem(parameters.strKendriteKd233 )
        self.burnPositionLabel = QLabel(parameters.strBurnTo)
        self.burnPositionCombobox = ComboBox()
        self.burnPositionCombobox.addItem(parameters.strFlash)
        self.burnPositionCombobox.addItem(parameters.strSRAM)
        boardSettingsLayout.addWidget(self.boardLabel, 0, 0)
        boardSettingsLayout.addWidget(self.boardCombobox, 0, 1)
        boardSettingsLayout.addWidget(self.burnPositionLabel, 1, 0)
        boardSettingsLayout.addWidget(self.burnPositionCombobox, 1, 1)

        # widgets serial settings
        serialSettingsGroupBox = QGroupBox(parameters.strSerialSettings)
        serialSettingsLayout = QGridLayout()
        serialPortLabek = QLabel(parameters.strSerialPort)
        serailBaudrateLabel = QLabel(parameters.strSerialBaudrate)
        self.serialPortCombobox = ComboBox()
        self.serailBaudrateCombobox = ComboBox()
        self.serailBaudrateCombobox.addItem("115200")
        self.serailBaudrateCombobox.addItem("1500000")
        self.serailBaudrateCombobox.addItem("2000000")
        self.serailBaudrateCombobox.addItem("3500000")
        self.serailBaudrateCombobox.addItem("4000000")
        self.serailBaudrateCombobox.addItem("4500000")
        self.serailBaudrateCombobox.setCurrentIndex(1)
        self.serailBaudrateCombobox.setEditable(True)
        
        serialSettingsLayout.addWidget(serialPortLabek,0,0)
        serialSettingsLayout.addWidget(serailBaudrateLabel, 1, 0)
        serialSettingsLayout.addWidget(self.serialPortCombobox, 0, 1)
        serialSettingsLayout.addWidget(self.serailBaudrateCombobox, 1, 1)
        serialSettingsGroupBox.setLayout(serialSettingsLayout)
        settingLayout.addWidget(serialSettingsGroupBox)

        # set stretch
        settingLayout.setStretch(0,1)
        settingLayout.setStretch(1,1)
        settingLayout.setStretch(2,2)

        # widgets download area
        self.downloadButton = QPushButton(parameters.strDownload)
        downloadLayout.addWidget(self.downloadButton)

        # main window
        self.statusBarStauts = QLabel()
        self.statusBarStauts.setMinimumWidth(80)
        self.statusBarStauts.setText("<font color=%s>%s</font>" %("#008200", parameters.strReady))
        self.statusBar().addWidget(self.statusBarStauts)

        self.resize(400, 550)
        self.MoveToCenter()
        self.setWindowTitle(parameters.appName+" V"+str(helpAbout.versionMajor)+"."+str(helpAbout.versionMinor))
        icon = QIcon()
        print("icon path:"+self.DataPath+"/"+parameters.appIcon)
        icon.addPixmap(QPixmap(self.DataPath+"/"+parameters.appIcon), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        if sys.platform == "win32":
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(parameters.appName)
        self.show()
        print("config file path:",os.getcwd()+"/"+parameters.strConfigFilePath)

    def initEvent(self):
        self.serialPortCombobox.clicked.connect(self.portComboboxClicked)
        self.errorSignal.connect(self.errorHint)
        self.showSerialComboboxSignal.connect(self.showCombobox)
        self.updateProgressSignal.connect(self.updateProgress)
        self.skinButton.clicked.connect(self.skinChange)
        self.aboutButton.clicked.connect(self.showAbout)
        self.openFileButton.clicked.connect(self.selectFile)
        self.downloadButton.clicked.connect(self.download)

        self.myObject=MyClass(self)
        slotLambda = lambda: self.indexChanged_lambda(self.myObject)
        self.serialPortCombobox.currentIndexChanged.connect(slotLambda)


    # @QtCore.pyqtSlot(str)
    def indexChanged_lambda(self, obj):
        mainObj = obj.arg
        self.serialPortCombobox.setToolTip(mainObj.serialPortCombobox.currentText())

    def portComboboxClicked(self):
        self.detectSerialPort()

    def MoveToCenter(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def selectFile(self):
        oldPath = self.filePathWidget.text()
        if oldPath=="":
            oldPath = os.getcwd()
        fileName_choose, filetype = QFileDialog.getOpenFileName(self,  
                                    parameters.strSelectFile,  
                                    oldPath,
                                    "All Files (*);;bin Files (*.bin);;k210 packages (*.kfpkg)")   # 设置文件扩展名过滤,用双分号间隔

        if fileName_choose == "":
            return
        if not self.checkFileName(fileName_choose):
            self.errorSignal.emit("File Error", "file type error, only support *.bin and *.kfpkg")
            return
        self.filePathWidget.setText(fileName_choose)

    def errorHint(self, title, str):
        QMessageBox.information(self, title, str)

    def findSerialPort(self):
        self.port_list = list(serial.tools.list_ports.comports())
        return self.port_list

    def portChanged(self):
        self.serialPortCombobox.setCurrentIndex(0)
        self.serialPortCombobox.setToolTip(str(self.portList[0]))

    def detectSerialPort(self):
        if not self.isDetectSerialPort:
            self.isDetectSerialPort = True
            t = threading.Thread(target=self.detectSerialPortProcess)
            t.setDaemon(True)
            t.start()

    def showCombobox(self):
        self.serialPortCombobox.showPopup()

    def checkFileName(self, name):
        if not name.endswith(".bin") and not name.endswith(".kfpkg"):
            return False
        if not os.path.exists(name):
            return False
        return True

    def detectSerialPortProcess(self):
        while(1):
            portList = self.findSerialPort()
            if len(portList)>0:
                currText = self.serialPortCombobox.currentText()
                self.serialPortCombobox.clear()
                for i in portList:
                    showStr = str(i[0])+" "+str(i[1])
                    self.serialPortCombobox.addItem(showStr)    
                index = self.serialPortCombobox.findText(currText)
                if index>=0:
                    self.serialPortCombobox.setCurrentIndex(index)
                else:
                    self.serialPortCombobox.setCurrentIndex(0)
                break
            time.sleep(1)
        self.showSerialComboboxSignal.emit()
        self.isDetectSerialPort = False

    def programExitSaveParameters(self):
        paramObj = parameters.ParametersToSave()
        paramObj.filePath = self.filePathWidget.text()
        paramObj.board    = self.boardCombobox.currentText()
        paramObj.burnPosition = self.burnPositionCombobox.currentText()
        paramObj.baudRate = self.serailBaudrateCombobox.currentIndex()
        paramObj.skin = self.param.skin
        f = open(parameters.strConfigFilePath,"wb")
        f.truncate()
        pickle.dump(paramObj, f)
        f.close()

    def programStartGetSavedParameters(self):
        paramObj = parameters.ParametersToSave()
        try:
            f = open(parameters.strConfigFilePath, "rb")
            paramObj = pickle.load( f)
            f.close()
        except Exception as e:
            f = open(parameters.strConfigFilePath, "wb")
            f.close()
        self.filePathWidget.setText(paramObj.filePath)
        self.boardCombobox.setCurrentText(paramObj.board)
        self.burnPositionCombobox.setCurrentText(paramObj.burnPosition)
        self.serailBaudrateCombobox.setCurrentIndex(paramObj.baudRate)
        self.param = paramObj

    def closeEvent(self, event):
        self.programExitSaveParameters()

    def skinChange(self):
        if self.param.skin == 1: # light
            file = open(self.DataPath + '/assets/qss/style-dark.qss', "r")
            self.param.skin = 2
        else: # elif self.param.skin == 2: # dark
            file = open(self.DataPath + '/assets/qss/style.qss', "r")
            self.param.skin = 1
        self.app.setStyleSheet(file.read().replace("$DataPath", self.DataPath))

    def showAbout(self):
        QMessageBox.information(self, "About","<h1 style='color:#f75a5a';margin=10px;>"+parameters.appName+
                                '</h1><br><b style="color:#08c7a1;margin = 5px;">V'+str(helpAbout.versionMajor)+"."+
                                str(helpAbout.versionMinor)+"."+str(helpAbout.versionDev)+
                                "</b><br><br>"+helpAbout.date+"<br><br>"+helpAbout.strAbout())

    def autoUpdateDetect(self):
        auto = autoUpdate.AutoUpdate()
        if auto.detectNewVersion():
            auto.OpenBrowser()

    def openDevManagement(self):
        os.system('start devmgmt.msc')

    def updateProgress(self, fileTypeStr, current, total, speedStr):
        self.statusBarStauts.setText("<font color=%s>downloading %s: %.2f%% %s</font>" %("#008200", fileTypeStr, current/float(total)*100, speedStr))

    def progress(self, fileTypeStr, current, total, speedStr):
        self.updateProgressSignal.emit(fileTypeStr, current, total, speedStr)

    def download(self):
        if self.burning:
            self.errorSignal.emit("Error", "Busy...")
            return

        self.burning = True
        filename = self.filePathWidget.text()
        if not self.checkFileName(filename):
            self.errorSignal.emit("Error", "File path error!")
            self.burning = False
            return
        color = False
        board = "dan"
        if self.boardCombobox.currentText()==parameters.strSipeedMaixGoE:
            board = "goE"
        elif self.boardCombobox.currentText()==parameters.strSipeedMaixGoD:
            board = "goD"
        sram = False
        if self.burnPositionCombobox.currentText()==parameters.strSRAM:
            sram = True
        try:
            baud = int(self.serailBaudrateCombobox.currentText())
        except Exception:
            self.errorSignal.emit("Error", "baud rate error")
            self.burning = False
            return
        dev  = self.serialPortCombobox.currentText().split()[0]
        if dev=="":
            self.errorSignal.emit("Error", "please select serial port")
            self.burning = False
            return
        t = threading.Thread(target=self.flashBurnProcess, args=(dev, baud, board, sram, filename, self.progress, color,))
        t.setDaemon(True)
        t.start()

    def flashBurnProcess(self, dev, baud, board, sram, filename, callback, color):
        self.statusBarStauts.setText("<font color=%s>downloading start...</font>" %("#008200"))
        try:
            kflash = KFlash()
            kflash.process(terminal=False, dev=dev, baudrate=baud, board=board, sram = sram, file=filename, callback=callback, noansi=not color)
        except Exception as e:
            self.errorSignal.emit("Burn Error", str(e))
            self.statusBarStauts.setText("<font color=%s>download fail</font>" %("#ff1d1d"))
            self.burning = False
            return
        self.statusBarStauts.setText("<font color=%s>download success</font>" %("#008200"))
        self.burning = False



def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow(app)
    print("data path:"+mainWindow.DataPath)
    print(mainWindow.param.skin)
    if(mainWindow.param.skin == 1) :# light skin
        file = open(mainWindow.DataPath+'/assets/qss/style.qss',"r")
    else: #elif mainWindow.param == 2: # dark skin
        file = open(mainWindow.DataPath + '/assets/qss/style-dark.qss', "r")
    qss = file.read().replace("$DataPath",mainWindow.DataPath)
    app.setStyleSheet(qss)
    mainWindow.detectSerialPort()
    t = threading.Thread(target=mainWindow.autoUpdateDetect)
    t.setDaemon(True)
    t.start()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

