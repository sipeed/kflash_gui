

import sys,os
import parameters, helpAbout, autoUpdate, paremeters_save
import translation
from translation import tr, tr_en
from Combobox import ComboBox

# from COMTool.wave import Wave
from PyQt5.QtCore import pyqtSignal,Qt
from PyQt5.QtWidgets import (QApplication, QWidget,QToolTip,QPushButton,QMessageBox,QDesktopWidget,QMainWindow,
                             QVBoxLayout,QHBoxLayout,QGridLayout,QLabel,
                             QLineEdit,QGroupBox,QSplitter,QFileDialog,
                             QProgressBar)
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
    hintSignal = pyqtSignal(str, str)
    updateProgressSignal = pyqtSignal(str, int, int, str)
    updateProgressPrintSignal = pyqtSignal(str)
    showSerialComboboxSignal = pyqtSignal()
    downloadResultSignal = pyqtSignal(bool, str)
    DataPath = "./"
    app = None

    def __init__(self,app):
        super().__init__()
        self.app = app
        self.programStartGetSavedParameters()
        self.initVar()
        self.initWindow()
        self.updateFrameParams()
        self.initEvent()

    def __del__(self):
        pass

    def initVar(self):
        self.burning = False
        self.isDetectSerialPort = False
        self.DataPath = parameters.dataPath
        self.kflash = KFlash(print_callback=self.kflash_py_printCallback)

    def initWindow(self):
        QToolTip.setFont(QFont('SansSerif', 10))
        # main layout
        self.frameWidget = QWidget()
        mainWidget = QSplitter(Qt.Horizontal)
        self.frameLayout = QVBoxLayout()
        self.settingWidget = QWidget()
        settingLayout = QVBoxLayout()
        self.settingWidget.setProperty("class","settingWidget")
        mainLayout = QVBoxLayout()
        self.settingWidget.setLayout(settingLayout)
        mainLayout.addWidget(self.settingWidget)
        mainLayout.setStretch(0,2)
        menuLayout = QHBoxLayout()
        
        self.progressHint = QLabel()
        self.progressHint.hide()

        self.progressbarRootWidget = QWidget()
        progressbarLayout = QVBoxLayout()
        self.progressbarRootWidget.setProperty("class","progressbarWidget")
        self.progressbarRootWidget.setLayout(progressbarLayout)
        
        self.downloadWidget = QWidget()
        downloadLayout = QVBoxLayout()
        self.downloadWidget.setProperty("class","downloadWidget")
        self.downloadWidget.setLayout(downloadLayout)

        mainWidget.setLayout(mainLayout)
        # menu
        # -----
        # settings and others
        # -----
        # progress bar
        # -----
        # download button
        # -----
        # status bar
        self.frameLayout.addLayout(menuLayout)
        self.frameLayout.addWidget(mainWidget)
        self.frameLayout.addWidget(self.progressHint)
        self.frameLayout.addWidget(self.progressbarRootWidget)
        self.frameLayout.addWidget(self.downloadWidget)
        self.frameWidget.setLayout(self.frameLayout)
        self.setCentralWidget(self.frameWidget)
        self.setFrameStrentch(0)

        # option layout
        self.langButton = QPushButton()
        self.skinButton = QPushButton()
        self.aboutButton = QPushButton()
        self.langButton.setProperty("class", "menuItemLang")
        self.skinButton.setProperty("class", "menuItem2")
        self.aboutButton.setProperty("class", "menuItem3")
        self.langButton.setObjectName("menuItem")
        self.skinButton.setObjectName("menuItem")
        self.aboutButton.setObjectName("menuItem")
        menuLayout.addWidget(self.langButton)
        menuLayout.addWidget(self.skinButton)
        menuLayout.addWidget(self.aboutButton)
        menuLayout.addStretch(0)
        
        # widgets file select
        fileSelectGroupBox = QGroupBox(tr("SelectFile"))
        settingLayout.addWidget(fileSelectGroupBox)
        fileSelectLayout = QHBoxLayout()
        fileSelectGroupBox.setLayout(fileSelectLayout)
        self.filePathWidget = QLineEdit()
        self.openFileButton = QPushButton(tr("OpenFile"))
        fileSelectLayout.addWidget(self.filePathWidget)
        fileSelectLayout.addWidget(self.openFileButton)

        # widgets board select
        boardSettingsGroupBox = QGroupBox(tr("BoardSettings"))
        settingLayout.addWidget(boardSettingsGroupBox)
        boardSettingsLayout = QGridLayout()
        boardSettingsGroupBox.setLayout(boardSettingsLayout)
        self.boardLabel = QLabel(tr("Board"))
        self.boardCombobox = ComboBox()
        self.boardCombobox.addItem(parameters.SipeedMaixDock)
        self.boardCombobox.addItem(parameters.SipeedMaixBit)
        self.boardCombobox.addItem(parameters.SipeedMaixGoE)
        self.boardCombobox.addItem(parameters.SipeedMaixGoD)
        self.boardCombobox.addItem(parameters.KendriteKd233)
        self.burnPositionLabel = QLabel(tr("BurnTo"))
        self.burnPositionCombobox = ComboBox()
        self.burnPositionCombobox.addItem(tr("Flash"))
        self.burnPositionCombobox.addItem(tr("SRAM"))
        boardSettingsLayout.addWidget(self.boardLabel, 0, 0)
        boardSettingsLayout.addWidget(self.boardCombobox, 0, 1)
        boardSettingsLayout.addWidget(self.burnPositionLabel, 1, 0)
        boardSettingsLayout.addWidget(self.burnPositionCombobox, 1, 1)

        # widgets serial settings
        serialSettingsGroupBox = QGroupBox(tr("SerialSettings"))
        serialSettingsLayout = QGridLayout()
        serialPortLabek = QLabel(tr("SerialPort"))
        serailBaudrateLabel = QLabel(tr("SerialBaudrate"))
        self.serialPortCombobox = ComboBox()
        self.serailBaudrateCombobox = ComboBox()
        self.serailBaudrateCombobox.addItem("115200")
        self.serailBaudrateCombobox.addItem("921600")
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

        # widgets progress bar
        
        self.progressbar = QProgressBar(self.progressbarRootWidget)
        self.progressbar.setGeometry(10, 0, 360, 40)
        self.progressbar.setValue(0)
        self.progressbarRootWidget.hide()

        # widgets download area
        self.downloadButton = QPushButton(tr("Download"))
        downloadLayout.addWidget(self.downloadButton)

        # main window
        self.statusBarStauts = QLabel()
        self.statusBarStauts.setMinimumWidth(80)
        self.statusBarStauts.setText("<font color=%s>%s</font>" %("#1aac2d", tr("DownloadHint")))
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
        print("config file path:",os.getcwd()+"/"+parameters.configFilePath)

    def initEvent(self):
        self.serialPortCombobox.clicked.connect(self.portComboboxClicked)
        self.errorSignal.connect(self.errorHint)
        self.hintSignal.connect(self.hint)
        self.downloadResultSignal.connect(self.downloadResult)
        self.showSerialComboboxSignal.connect(self.showCombobox)
        self.updateProgressSignal.connect(self.updateProgress)
        self.updateProgressPrintSignal.connect(self.updateProgressPrint)
        self.langButton.clicked.connect(self.langChange)
        self.skinButton.clicked.connect(self.skinChange)
        self.aboutButton.clicked.connect(self.showAbout)
        self.openFileButton.clicked.connect(self.selectFile)
        self.downloadButton.clicked.connect(self.download)

        self.myObject=MyClass(self)
        slotLambda = lambda: self.indexChanged_lambda(self.myObject)
        self.serialPortCombobox.currentIndexChanged.connect(slotLambda)

    def setFrameStrentch(self, mode):
        if mode == 0:
            self.frameLayout.setStretch(0,1)
            self.frameLayout.setStretch(1,3)
            self.frameLayout.setStretch(2,3)
            self.frameLayout.setStretch(3,1)
            self.frameLayout.setStretch(4,1)
            self.frameLayout.setStretch(5,1)
        else:
            self.frameLayout.setStretch(0,0)
            self.frameLayout.setStretch(1,0)
            self.frameLayout.setStretch(2,1)
            self.frameLayout.setStretch(3,1)
            self.frameLayout.setStretch(4,1)
            self.frameLayout.setStretch(5,1)

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
                                    tr("SelectFile"),  
                                    oldPath,
                                    "All Files (*);;bin Files (*.bin);;k210 packages (*.kfpkg)")   # 设置文件扩展名过滤,用双分号间隔

        if fileName_choose == "":
            return
        if not self.checkFileName(fileName_choose):
            self.errorSignal.emit(tr("Error"), tr("FileTypeError"))
            return
        self.filePathWidget.setText(fileName_choose)

    def errorHint(self, title, str):
        QMessageBox.critical(self, title, str)
    
    def hint(self, title, str):
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
                    showStr = str(i[0])+" ("+str(i[1])+")"
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
        paramObj = paremeters_save.ParametersToSave()
        paramObj.filePath = self.filePathWidget.text()
        paramObj.board    = self.boardCombobox.currentText()
        paramObj.burnPosition = self.burnPositionCombobox.currentText()
        paramObj.baudRate = self.serailBaudrateCombobox.currentIndex()
        paramObj.skin = self.param.skin
        paramObj.language = translation.current_lang
        f = open(parameters.configFilePath,"wb")
        f.truncate()
        pickle.dump(paramObj, f)
        f.close()

    def programStartGetSavedParameters(self):
        paramObj = paremeters_save.ParametersToSave()
        try:
            f = open(parameters.configFilePath, "rb")
            paramObj = pickle.load( f)
            f.close()
        except Exception as e:
            f = open(parameters.configFilePath, "wb")
            f.close()
        translation.setLanguage(paramObj.language)
        self.param = paramObj

    def updateFrameParams(self):
        self.filePathWidget.setText(self.param.filePath)
        self.boardCombobox.setCurrentText(self.param.board)
        self.burnPositionCombobox.setCurrentText(self.param.burnPosition)
        self.serailBaudrateCombobox.setCurrentIndex(self.param.baudRate)

    def closeEvent(self, event):
        self.programExitSaveParameters()

    def langChange(self):
        if self.param.language == translation.language_en:
            translation.setLanguage(translation.language_zh)
        else:
            translation.setLanguage(translation.language_en)
        self.hint(tr("Hint"), tr("Success") +"\n"+ tr("Reboot to take effect"))
        self.frameWidget.style().unpolish(self.downloadButton)
        self.frameWidget.style().polish(self.downloadButton)
        self.frameWidget.update()

    def skinChange(self):
        if self.param.skin == 1: # light
            file = open(self.DataPath + '/assets/qss/style-dark.qss', "r")
            self.param.skin = 2
        else: # elif self.param.skin == 2: # dark
            file = open(self.DataPath + '/assets/qss/style.qss', "r")
            self.param.skin = 1
        self.app.setStyleSheet(file.read().replace("$DataPath", self.DataPath))

    def showAbout(self):
        QMessageBox.information(self, tr("About"),"<h1 style='color:#f75a5a';margin=10px;>"+parameters.appName+
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
        currBurnPos = self.burnPositionCombobox.currentText()
        if currBurnPos == tr("SRAM") or currBurnPos == tr_en("SRAM"):
            fileTypeStr = tr("ToSRAM")
        percent = current/float(total)*100
        hint = "<font color=%s>%s %s:</font>   <font color=%s> %.2f%%</font>   <font color=%s> %s</font>" %("#ff7575", tr("Downloading"), fileTypeStr, "#2985ff", percent, "#1aac2d", speedStr)
        self.progressHint.setText(hint)
        self.progressbar.setValue(percent)
    
    def updateProgressPrint(self, str):
        self.statusBarStauts.setText(str)

    def kflash_py_printCallback(self, *args, end = "\n"):
        msg = ""
        for i in args:
            msg += str(i)
        msg.replace("\n", " ")
        self.updateProgressPrintSignal.emit(msg)

    def progress(self, fileTypeStr, current, total, speedStr):
        self.updateProgressSignal.emit(fileTypeStr, current, total, speedStr)

    def download(self):
        if self.burning:
            self.terminateBurn()
            return

        self.burning = True
        filename = self.filePathWidget.text()
        if not self.checkFileName(filename):
            self.errorSignal.emit(tr("Error"), tr("FilePathError"))
            self.burning = False
            return
        color = False
        board = "dan"
        boardText = self.boardCombobox.currentText()
        if boardText == parameters.SipeedMaixGoE:
            board = "goE"
        elif boardText == parameters.SipeedMaixGoD:
            board = "goD"
        elif boardText == parameters.SipeedMaixBit:
            board = "bit"
        elif boardText == parameters.KendriteKd233:
            board = "kd233"


        sram = False
        if self.burnPositionCombobox.currentText()==tr("SRAM") or \
            self.burnPositionCombobox.currentText()==tr_en("SRAM"):
            sram = True
        try:
            baud = int(self.serailBaudrateCombobox.currentText())
        except Exception:
            self.errorSignal.emit(tr("Error"), tr("BaudrateError"))
            self.burning = False
            return
        dev  = self.serialPortCombobox.currentText().split()[0]
        if dev=="":
            self.errorSignal.emit(tr("Error"), tr("PleaseSelectSerialPort"))
            self.burning = False
            return
        # hide setting widgets
        self.setFrameStrentch(1)
        self.settingWidget.hide()
        self.progressbar.setValue(0)
        self.progressbarRootWidget.show()
        self.progressHint.show()
        self.downloadButton.setText(tr("Cancel"))
        self.downloadButton.setProperty("class", "redbutton")
        self.downloadButton.style().unpolish(self.downloadButton)
        self.downloadButton.style().polish(self.downloadButton)
        self.downloadButton.update()
        self.statusBarStauts.setText("<font color=%s>%s ...</font>" %("#1aac2d", tr("Downloading")))
        hint = "<font color=%s>%s</font>" %("#ff0d0d", tr("DownloadStart"))
        self.progressHint.setText(hint)
        # download
        self.burnThread = threading.Thread(target=self.flashBurnProcess, args=(dev, baud, board, sram, filename, self.progress, color,))
        self.burnThread.setDaemon(True)
        self.burnThread.start()

    def flashBurnProcess(self, dev, baud, board, sram, filename, callback, color):
        success = True
        errMsg = ""
        try:
            self.kflash.process(terminal=False, dev=dev, baudrate=baud, board=board, sram = sram, file=filename, callback=callback, noansi=not color)
        except Exception as e:
            errMsg = str(e)
            if str(e) != "Burn SRAM OK":
                success = False
        if success:
            self.downloadResultSignal.emit(True, errMsg)
        else:
            self.downloadResultSignal.emit(False, errMsg)
            

    def downloadResult(self, success, msg):
        if success:
            self.hintSignal.emit(tr("Success"), tr("DownloadSuccess"))
            self.statusBarStauts.setText("<font color=%s>%s</font>" %("#1aac2d", tr("DownloadSuccess")))
        else:
            if msg == "Cancel":
                self.statusBarStauts.setText("<font color=%s>%s</font>" %("#ff1d1d", tr("DownloadCanceled")))
            else:
                msg = tr("ErrorSettingHint") + "\n\n"+msg
                self.errorSignal.emit(tr("Error"), msg)
                self.statusBarStauts.setText("<font color=%s>%s</font>" %("#ff1d1d", tr("DownloadFail")))
            self.progressHint.setText("")
        self.downloadButton.setText(tr("Download"))
        self.downloadButton.setProperty("class", "normalbutton")
        self.downloadButton.style().unpolish(self.downloadButton)
        self.downloadButton.style().polish(self.downloadButton)
        self.downloadButton.update()
        self.setFrameStrentch(0)
        self.progressbarRootWidget.hide()
        self.progressHint.hide()
        self.settingWidget.show()
        self.burning = False

    def terminateBurn(self):
        hint = "<font color=%s>%s</font>" %("#ff0d0d", tr("DownloadCanceling"))
        self.progressHint.setText(hint)
        self.kflash.kill()


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

