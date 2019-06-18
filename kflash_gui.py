

import sys,os
import parameters, helpAbout, autoUpdate, paremeters_save
import translation
from translation import tr, tr_en
from Combobox import ComboBox
import json, zipfile

# from COMTool.wave import Wave
from PyQt5.QtCore import pyqtSignal,Qt
from PyQt5.QtWidgets import (QApplication, QWidget,QToolTip,QPushButton,QMessageBox,QDesktopWidget,QMainWindow,
                             QVBoxLayout,QHBoxLayout,QGridLayout,QLabel,
                             QLineEdit,QGroupBox,QSplitter,QFileDialog,QCheckBox,
                             QProgressBar)
from PyQt5.QtGui import QIcon,QFont,QTextCursor,QPixmap
import serial
import serial.tools.list_ports
import threading
import time
import binascii,re
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
        self.initEvent()
        self.updateFrameParams()

    def __del__(self):
        pass

    def initVar(self):
        self.burning = False
        self.isDetectSerialPort = False
        self.DataPath = parameters.dataPath
        self.kflash = KFlash(print_callback=self.kflash_py_printCallback)
        self.saveKfpkDir = ""

    def setWindowSize(self, w=520, h=550):
        self.resize(w, h)

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
        self.setFrameStrentch(1)

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
        self.fileSelectGroupBox = QGroupBox(tr("SelectFile"))
        settingLayout.addWidget(self.fileSelectGroupBox)
        self.fileSelectLayout = QVBoxLayout()
        self.fileSelectGroupBox.setLayout(self.fileSelectLayout)
        oneFilePathWidget = QWidget()
        oneFilePathWidgetLayout = QHBoxLayout()
        oneFilePathWidget.setLayout(oneFilePathWidgetLayout)
        filePathWidget = QLineEdit()
        openFileButton = QPushButton(tr("OpenFile"))
        oneFilePathWidgetLayout.addWidget(filePathWidget)
        oneFilePathWidgetLayout.addWidget(openFileButton)
        oneFilePathWidgetLayout.setStretch(0, 3)
        oneFilePathWidgetLayout.setStretch(1, 1)
        self.fileSelectLayout.addWidget(oneFilePathWidget)
        self.fileSelectWidgets = [["kfpkg", oneFilePathWidget, oneFilePathWidgetLayout, filePathWidget, None, openFileButton]]
                  # for "button": ["button", addoneWidget, addoneWidgetLayout, addFileButton, packFileButton]
                  # for "bin":    ["bin", oneFilePathWidget, oneFilePathWidgetLayout, filePathWidget, fileBurnAddrWidget, openFileButton, fileBurnEncCheckbox]
        # widgets board select
        boardSettingsGroupBox = QGroupBox(tr("BoardSettings"))
        settingLayout.addWidget(boardSettingsGroupBox)
        boardSettingsLayout = QGridLayout()
        boardSettingsGroupBox.setLayout(boardSettingsLayout)
        self.boardLabel = QLabel(tr("Board"))
        self.boardCombobox = ComboBox()
        self.boardCombobox.addItem(parameters.SipeedMaixDock)
        self.boardCombobox.addItem(parameters.SipeedMaixBit)
        self.boardCombobox.addItem(parameters.SipeedMaixBitMic)
        self.boardCombobox.addItem(parameters.SipeedMaixduino)
        self.boardCombobox.addItem(parameters.SipeedMaixGo)
        self.boardCombobox.addItem(parameters.SipeedMaixGoD)
        self.boardCombobox.addItem(parameters.KendryteKd233)
        self.boardCombobox.addItem(parameters.kendryteTrainer)
        self.boardCombobox.addItem(parameters.Auto)
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

        self.setWindowSize()
        self.MoveToCenter()
        self.setWindowTitle(parameters.appName+" V"+str(helpAbout.versionMajor)+"."+str(helpAbout.versionMinor))
        icon = QIcon()
        print("icon path:"+self.DataPath+"/"+parameters.appIcon)
        icon.addPixmap(QPixmap(self.DataPath+"/"+parameters.appIcon), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        if sys.platform == "win32":
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(parameters.appName)
        
        self.show()
        self.progressbar.setGeometry(10, 0, self.downloadWidget.width()-25, 40)
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
        self.downloadButton.clicked.connect(self.download)
        self.fileSelectWidget_Button(0).clicked.connect(lambda:self.selectFile(self.fileSelectWidget_Path(0)))

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
    
    def fileSelectWidget_Type(self, index):
        return self.fileSelectWidgets[index][0]

    def fileSelectWidget_Widget(self, index):
        return self.fileSelectWidgets[index][1]
    
    def fileSelectWidget_Layout(self, index):
        return self.fileSelectWidgets[index][2]

    def fileSelectWidget_Path(self, index):
        return self.fileSelectWidgets[index][3]

    def fileSelectWidget_Addr(self, index):
        return self.fileSelectWidgets[index][4]
    
    def fileSelectWidget_Button(self, index):
        return self.fileSelectWidgets[index][5]
    
    def fileSelectWidget_Prefix(self, index):
        return self.fileSelectWidgets[index][6]
    
    def fileSelectWidget_Close(self, index):
        return self.fileSelectWidgets[index][7]

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
    def removeFileSelection(self, button):
        index = -1
        for i in range(len(self.fileSelectWidgets)):
            if len(self.fileSelectWidgets[i]) >= 8:
                if self.fileSelectWidget_Close(i) == button:
                    index = i
        print(index)
        if index == -1:
            return
        if len(self.fileSelectWidgets) > 2:
            self.fileSelectWidget_Button(index).clicked.disconnect()
            self.fileSelectWidget_Close(index).clicked.disconnect()
            self.fileSelectWidget_Widget(index).setParent(None)
            self.fileSelectWidgets.remove(self.fileSelectWidgets[index])
        if len(self.fileSelectWidgets) == 2:
            self.fileSelectWidget_Close(0).clicked.disconnect()
            self.fileSelectWidget_Close(0).setParent(None)
            self.fileSelectWidgets[0].remove(self.fileSelectWidget_Close(0))
        self.downloadWidget.resize(self.downloadWidget.width(), 58)
        self.setWindowSize()

    def addAddFileWidget(self):
        if len(self.fileSelectWidgets) == 2:
            removeButton0 = QPushButton()
            removeButton0.setProperty("class", "remove_file_selection")
            self.fileSelectWidgets[0][2].addWidget(removeButton0)
            self.fileSelectWidgets[0].append(removeButton0)
            removeButton0.clicked.connect(lambda:self.removeFileSelection(removeButton0))
        oneFilePathWidget = QWidget()
        oneFilePathWidgetLayout = QHBoxLayout()
        oneFilePathWidget.setLayout(oneFilePathWidgetLayout)
        filePathWidget = QLineEdit()
        fileBurnAddrWidget = QLineEdit("0x00000")
        fileBurnEncCheckbox = QCheckBox(tr("Prefix"))
        openFileButton = QPushButton(tr("OpenFile"))
        removeButton = QPushButton()
        removeButton.setProperty("class", "remove_file_selection")
        oneFilePathWidgetLayout.addWidget(filePathWidget)
        oneFilePathWidgetLayout.addWidget(fileBurnAddrWidget)
        oneFilePathWidgetLayout.addWidget(fileBurnEncCheckbox)
        oneFilePathWidgetLayout.addWidget(openFileButton)
        oneFilePathWidgetLayout.addWidget(removeButton)
        oneFilePathWidgetLayout.setStretch(0, 4)
        oneFilePathWidgetLayout.setStretch(1, 2)
        oneFilePathWidgetLayout.setStretch(2, 1)
        oneFilePathWidgetLayout.setStretch(3, 2)
        # oneFilePathWidgetLayout.setStretch(4, 1)
        index = len(self.fileSelectWidgets)-1
        self.fileSelectWidgets.insert(index, ["bin", oneFilePathWidget, oneFilePathWidgetLayout, filePathWidget, fileBurnAddrWidget, openFileButton, fileBurnEncCheckbox, removeButton])
        self.fileSelectLayout.insertWidget(index, oneFilePathWidget)
        openFileButton.clicked.connect(lambda:self.selectFile(filePathWidget))
        removeButton.clicked.connect(lambda:self.removeFileSelection(removeButton))

    def fileSelectShowKfpkg(self, index, name):
        if index==0 and self.fileSelectWidget_Type(0) == "kfpkg": #only one kgpkg before
            self.fileSelectWidget_Path(index).setText(name)
        else:# have bin file before, remove all and add one for kfpkg
            for i in range(len(self.fileSelectWidgets)):
                if self.fileSelectWidget_Type(i)=="button":
                    self.fileSelectWidgets[i][3].clicked.disconnect()
                    self.fileSelectWidgets[i][4].clicked.disconnect()
                else:
                    self.fileSelectWidget_Button(i).clicked.disconnect()
                # self.fileSelectLayout.removeWidget(self.fileSelectWidget_Widget(i))
                self.fileSelectWidget_Widget(i).setParent(None)
            self.fileSelectWidgets.clear()
            oneFilePathWidget = QWidget()
            oneFilePathWidgetLayout = QHBoxLayout()
            oneFilePathWidget.setLayout(oneFilePathWidgetLayout)
            filePathWidget = QLineEdit()
            openFileButton = QPushButton(tr("OpenFile"))
            oneFilePathWidgetLayout.addWidget(filePathWidget)
            oneFilePathWidgetLayout.addWidget(openFileButton)
            oneFilePathWidgetLayout.setStretch(0, 3)
            oneFilePathWidgetLayout.setStretch(1, 1)
            self.fileSelectLayout.addWidget(oneFilePathWidget)
            self.fileSelectWidgets.append(["kfpkg", oneFilePathWidget, oneFilePathWidgetLayout, filePathWidget, None, openFileButton])
            openFileButton.clicked.connect(lambda:self.selectFile(filePathWidget))
            filePathWidget.setText(name)
            # TODO: resize window

    def fileSelectShowBin(self, index, name, addr=None, prefix=None, prefixAuto=False, closeButton=False ):
        if index==0 and self.fileSelectWidget_Type(0) == "kfpkg": #only one kgpkg before
            self.fileSelectWidget_Button(index).clicked.disconnect()
            # self.fileSelectLayout.removeWidget(self.fileSelectWidget_Widget(index))
            self.fileSelectWidget_Widget(index).setParent(None)
            self.fileSelectWidgets.clear()
            oneFilePathWidget = QWidget()
            oneFilePathWidgetLayout = QHBoxLayout()
            oneFilePathWidget.setLayout(oneFilePathWidgetLayout)
            filePathWidget = QLineEdit()
            fileBurnAddrWidget = QLineEdit("0x00000")
            fileBurnEncCheckbox = QCheckBox(tr("Prefix"))
            openFileButton = QPushButton(tr("OpenFile"))
            if closeButton:
                removeButton = QPushButton()
                removeButton.setProperty("class", "remove_file_selection")
            oneFilePathWidgetLayout.addWidget(filePathWidget)
            oneFilePathWidgetLayout.addWidget(fileBurnAddrWidget)
            oneFilePathWidgetLayout.addWidget(fileBurnEncCheckbox)
            oneFilePathWidgetLayout.addWidget(openFileButton)
            if closeButton:
                oneFilePathWidgetLayout.addWidget(removeButton)
            oneFilePathWidgetLayout.setStretch(0, 4)
            oneFilePathWidgetLayout.setStretch(1, 2)
            oneFilePathWidgetLayout.setStretch(2, 1)
            oneFilePathWidgetLayout.setStretch(3, 2)
            # oneFilePathWidgetLayout.setStretch(4, 1)
            self.fileSelectLayout.addWidget(oneFilePathWidget)
            openFileButton.clicked.connect(lambda:self.selectFile(filePathWidget))
            if closeButton:
                self.fileSelectWidgets.append(["bin", oneFilePathWidget, oneFilePathWidgetLayout, filePathWidget, fileBurnAddrWidget, openFileButton, fileBurnEncCheckbox, removeButton])
                removeButton.clicked.connect(lambda:self.removeFileSelection(removeButton))
                print(removeButton)
            else:
                self.fileSelectWidgets.append(["bin", oneFilePathWidget, oneFilePathWidgetLayout, filePathWidget, fileBurnAddrWidget, openFileButton, fileBurnEncCheckbox])
            # add ADD button
            addoneWidget = QWidget()
            addoneWidgetLayout = QHBoxLayout()
            addoneWidget.setLayout(addoneWidgetLayout)
            addFileButton = QPushButton(tr("Add File"))
            packFileButton = QPushButton(tr("Pack to kfpkg"))
            addoneWidgetLayout.addWidget(addFileButton)
            addoneWidgetLayout.addWidget(packFileButton)
            self.fileSelectLayout.addWidget(addoneWidget)
            self.fileSelectWidgets.append(["button", addoneWidget, addoneWidgetLayout, addFileButton, packFileButton])
            addFileButton.clicked.connect(self.addAddFileWidget)
            packFileButton.clicked.connect(self.packFile)

        self.fileSelectWidget_Path(index).setText(name)

        if prefixAuto:
            if name.endswith(".bin"):
                self.fileSelectWidget_Prefix(index).setChecked(True)
            else:
                self.fileSelectWidget_Prefix(index).setChecked(False)
        elif prefix:
            self.fileSelectWidget_Prefix(index).setChecked(True)
        if addr:
                self.fileSelectWidget_Addr(index).setText("0x%06x" %(addr))

    # return: ("kfpkg", [(file path, burn addr, add prefix),...])
    #      or ("bin", file path)
    #      or (None, None)
    def getBurnFilesInfo(self):
        files = []
        if self.fileSelectWidgets[0][0] == "kfpkg":
            path = self.fileSelectWidget_Path(0).text().strip()
            if path=="" or not os.path.exists(path):
                self.errorSignal.emit(tr("Error"), tr("Line {}: ").format(i+1)+tr("File path error")+":"+path)
                return (None, None)
            return ("kfpkg", path)
        for i in range(len(self.fileSelectWidgets)):
            if self.fileSelectWidgets[i][0] == "bin":
                path = self.fileSelectWidget_Path(i).text().strip()
                if path=="":
                    continue
                if not os.path.exists(path):
                    self.errorSignal.emit(tr("Error"), tr("Line {}: ").format(i+1)+tr("File path error")+":"+path)
                    return (None, None)
                try:
                    addr = int(self.fileSelectWidgets[i][4].text(), 16)
                except Exception:
                    self.errorSignal.emit(tr("Error"), tr("Line {}: ").format(i+1)+tr("Address error")+self.fileSelectWidgets[i][4].text())
                    return (None, None)
                files.append( (path, addr, self.fileSelectWidgets[i][6].isChecked()) )
        return ("bin", files)

    class KFPKG():
        def __init__(self):
            self.fileInfo = {"version": "0.1.0", "files": []}
            self.filePath = {}
            self.burnAddr = []
        
        def addFile(self, addr, path, prefix=False):
            if not os.path.exists(path):
                raise ValueError(tr("FilePathError"))
            if addr in self.burnAddr:
                raise ValueError(tr("Burn dddr duplicate")+":0x%06x" %(addr))
            f = {}
            f_name = os.path.split(path)[1]
            f["address"] = addr
            f["bin"] = f_name
            f["sha256Prefix"] = prefix
            self.fileInfo["files"].append(f)
            self.filePath[f_name] = path
            self.burnAddr.append(addr)

        def listDumps(self):
            kfpkg_json = json.dumps(self.fileInfo, indent=4)
            return kfpkg_json

        def listDump(self, path):
            with open(path, "w") as f:
                f.write(json.dumps(self.fileInfo, indent=4))

        def listLoads(self, kfpkgJson):
            self.fileInfo = json.loads(kfpkgJson)

        def listLload(self, path):
            with open(path) as f:
                self.fileInfo = json.load(f)

        def save(self, path):
            listName = "kflash_gui_tmp_list.json"
            self.listDump(listName)
            try:
                with zipfile.ZipFile(path, "w") as zip:
                    for name,path in self.filePath.items():
                        zip.write(path, arcname=name, compress_type=zipfile.ZIP_LZMA)
                    zip.write(listName, arcname="flash-list.json", compress_type=zipfile.ZIP_LZMA)
                    zip.close()
            except Exception as e:
                os.remove(listName)
                raise e
            os.remove(listName)
        

    def packFile(self):
        # generate flash-list.json
        fileType, files = self.getBurnFilesInfo()
        if not fileType or not files or fileType=="kfpkg":
            self.errorSignal.emit(tr("Error"), tr("File path error"))
            return
        kfpkg = self.KFPKG()
        try:
            for path, addr, prefix in files:
                kfpkg.addFile(addr, path, prefix)
        except Exception as e:
            self.errorSignal.emit(tr("Error"), tr("Pack kfpkg fail")+":"+str(e))
            return
        # select saving path
        if not os.path.exists(self.saveKfpkDir):
            self.saveKfpkDir = os.getcwd()
        fileName_choose, filetype = QFileDialog.getSaveFileName(self,  
                                    tr("Save File"),  
                                    self.saveKfpkDir,
                                    "k210 packages (*.kfpkg)")

        if fileName_choose == "":
            self.errorSignal.emit(tr("Error"), tr("File path error"))
            return
        if not fileName_choose.endswith(".kfpkg"):
            fileName_choose += ".kfpkg"
        self.saveKfpkDir = os.path.split(fileName_choose)[0]
        # print("save to ", fileName_choose)
        
        # write kfpkg file
        try:
            kfpkg.save(fileName_choose)
        except Exception as e:
            self.errorSignal.emit(tr("Error"), tr("Pack kfpkg fail")+":"+str(e))
            return
        self.hintSignal.emit(tr("Success"), tr("Save kfpkg success"))

    def selectFile(self, pathobj):
        index = -1
        for i in range(len(self.fileSelectWidgets)):
            if len(self.fileSelectWidgets[i]) >= 4:
                if pathobj == self.fileSelectWidget_Path(i):
                    index = i
        if index == -1:
            return
        tmp = index
        while tmp>=0:
            oldPath = self.fileSelectWidget_Path(tmp).text()
            if oldPath != "":
                break
            tmp -= 1
        if oldPath=="":
            oldPath = os.getcwd()
        fileName_choose, filetype = QFileDialog.getOpenFileName(self,  
                                    tr("SelectFile"),  
                                    oldPath,
                                    "All Files (*);;bin Files (*.bin);;k210 packages (*.kfpkg);;kmodel (*.kmodel);;encrypted kmodle(*.smodel)")   # 设置文件扩展名过滤,用双分号间隔

        if fileName_choose == "":
            return
        if not self.isFileValid(fileName_choose):
            self.errorSignal.emit(tr("Error"), tr("File path error"))
            return
        if self.isKfpkg(fileName_choose):
            self.fileSelectShowKfpkg(index, fileName_choose)
        else:
            self.fileSelectShowBin(index, fileName_choose, prefixAuto=True, closeButton=False)

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

    def isKfpkg(self, name):
        if name.endswith(".kfpkg"):
            return True
        return False

    def isFileValid(self, name):
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
        paramObj.board    = self.boardCombobox.currentText()
        paramObj.burnPosition = self.burnPositionCombobox.currentText()
        paramObj.baudRate = self.serailBaudrateCombobox.currentIndex()
        paramObj.skin = self.param.skin
        paramObj.language = translation.current_lang
        path = self.fileSelectWidget_Path(0).text()
        if path.endswith(".kfpkg"):
            paramObj.files.append(path)
        else:
            for i in range(len(self.fileSelectWidgets)):
                try:
                    addr = int(self.fileSelectWidget_Addr(i).text(),16)
                except Exception:
                    continue
                paramObj.files.append( (self.fileSelectWidget_Path(i).text(), addr, self.fileSelectWidget_Prefix(i).isChecked()) )
        paramObj.save(parameters.configFilePath)

    def programStartGetSavedParameters(self):
        paramObj = paremeters_save.ParametersToSave()
        paramObj.load(parameters.configFilePath)
        translation.setLanguage(paramObj.language)
        self.param = paramObj

    def updateFrameParams(self):
        pathLen = len(self.param.files)
        if pathLen == 1 and type(self.param.files[0])==str and self.param.files[0].endswith(".kfpkg"):
            self.fileSelectWidget_Path(0).setText(self.param.files[0])
        elif pathLen != 0:
            index = 0
            for path, addr, prefix  in self.param.files:
                prefix = None if (not prefix) else True
                if index!=0:
                    self.addAddFileWidget()
                if pathLen > 1 and index != 0:
                    closeButton = True
                else:
                    closeButton = False
                self.fileSelectShowBin(index, path, addr, prefix, closeButton=closeButton)
                index += 1
        self.boardCombobox.setCurrentText(self.param.board)
        self.burnPositionCombobox.setCurrentText(self.param.burnPosition)
        self.serailBaudrateCombobox.setCurrentIndex(self.param.baudRate)

    def closeEvent(self, event):
        self.programExitSaveParameters()

    def langChange(self):
        if self.param.language == translation.language_en:
            translation.setLanguage(translation.language_zh)
            lang = tr("Chinese language")
        else:
            translation.setLanguage(translation.language_en)
            lang = tr("English language")
        
        self.hint(tr("Hint"), tr("Language Changed to ") + lang + "\n"+ tr("Reboot to take effect"))
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
        tmpFile = ""
        fileType, filesInfo = self.getBurnFilesInfo()
        if not fileType or not filesInfo:
            self.errorSignal.emit(tr("Error"), tr("File path error"))
            return
        if fileType == "kfpkg":
            filename = filesInfo
        else:#generate kfpkg
            tmpFile = "kflash_gui_tmp.kfpkg"
            kfpkg = self.KFPKG()
            try:
                for path, addr, prefix in filesInfo:
                    kfpkg.addFile(addr, path, prefix)
                kfpkg.save(tmpFile)
            except Exception as e:
                self.errorSignal.emit(tr("Error"), tr("Pack kfpkg fail")+":"+str(e))
                return
            filename = os.path.abspath(tmpFile)
        
        self.burning = True
        # if not self.checkFileName(filename):
        #     self.errorSignal.emit(tr("Error"), tr("FilePathError"))
        #     self.burning = False
        #     return
        color = False
        board = "dan"
        boardText = self.boardCombobox.currentText()
        if boardText == parameters.SipeedMaixGo:
            board = "goE"
        elif boardText == parameters.SipeedMaixGoD:
            board = "goD"
        elif boardText == parameters.SipeedMaixduino:
            board = "maixduino"
        elif boardText == parameters.SipeedMaixBit:
            board = "bit"
        elif boardText == parameters.SipeedMaixBitMic:
            board = "bit_mic"
        elif boardText == parameters.KendryteKd233:
            board = "kd233"
        elif boardText == parameters.kendryteTrainer:
            board = "trainer"
        elif boardText == parameters.Auto:
            board = None

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
        dev = ""
        try:
            dev  = self.serialPortCombobox.currentText().split()[0]
        except Exception:
            pass
        if dev=="":
            self.errorSignal.emit(tr("Error"), tr("PleaseSelectSerialPort"))
            self.burning = False
            return
        # hide setting widgets
        self.setFrameStrentch(1)
        self.settingWidget.hide()
        self.progressbar.setValue(0)
        self.progressbar.setGeometry(10, 0, self.downloadWidget.width()-25, 40)
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
        self.burnThread = threading.Thread(target=self.flashBurnProcess, args=(dev, baud, board, sram, filename, self.progress, tmpFile!="", color,))
        self.burnThread.setDaemon(True)
        self.burnThread.start()

    def flashBurnProcess(self, dev, baud, board, sram, filename, callback, cleanFile, color):
        success = True
        errMsg = ""
        try:
            if board:
                self.kflash.process(terminal=False, dev=dev, baudrate=baud, board=board, sram = sram, file=filename, callback=callback, noansi=not color)
            else:
                self.kflash.process(terminal=False, dev=dev, baudrate=baud, sram = sram, file=filename, callback=callback, noansi=not color)
        except Exception as e:
            errMsg = str(e)
            if str(e) != "Burn SRAM OK":
                success = False
        if cleanFile:
            os.remove(filename)
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

