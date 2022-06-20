

import sys, os
import math
import tempfile
import parameters, helpAbout, autoUpdate, paremeters_save
import translation
from translation import tr, tr_en, tr2, getCurrentLanguage
from Combobox import ComboBox
import json, zipfile, struct, hashlib

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
    eraseResultSignal = pyqtSignal(bool, str, bool)
    eraseStatusSignal = pyqtSignal(str)
    DataPath = "./"
    app = None
    firmware_start_bytes = [b'\x21\xa8', b'\xef\xbe', b'\xad\xde']

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
        self.erasing = False
        self.erasingCanCancel = True
        self.packing = False
        self.isDetectSerialPort = False
        self.DataPath = parameters.dataPath
        self.kflash = KFlash(print_callback=self.kflash_py_printCallback)
        self.saveKfpkDir = ""
        self.zipTempFiles = []
        self.fileSelectWidgets = []
        self.units = ["KiB", "B", "MiB"]
        # load erase template
        self.eraseTemplateConfigs = {}
        eraseConfigPath = os.path.join(self.DataPath, "erase_config.json")
        if os.path.exists(eraseConfigPath):
            with open(eraseConfigPath, encoding='utf-8') as f:
                self.eraseTemplateConfigs = json.load(f)
        # convert language to local
        config = {}
        current_lang = getCurrentLanguage()
        for key in self.eraseTemplateConfigs:
            config[self.eraseTemplateConfigs[key]["lang"][current_lang]] = self.eraseTemplateConfigs[key]["config"]
        self.eraseTemplateConfigs = config
        # load boards info
        self.boardsInfo = {}
        boardsInfoPath = os.path.join(self.DataPath, "boards_info.json")
        if os.path.exists(boardsInfoPath):
            with open(boardsInfoPath, encoding='utf-8') as f:
                self.boardsInfo = json.load(f)
        # convert language to local
        boards = {}
        for key in self.boardsInfo:
            boards[self.boardsInfo[key]['lang'][current_lang]] = self.boardsInfo[key]['type']
        self.boardsInfo = boards

    def setWindowSize(self, w=520, h=550):
        self.resize(w, h)

    def setFileSelectItemLayout(self, item, isKfpkg):
        if isKfpkg:
            item[4].hide()
            item[2].setStretch(0, 1)
            item[2].setStretch(1, 12)
            item[2].setStretch(3, 4)
            item[2].setStretch(4, 1)
        else:
            item[4].show()
            item[2].setStretch(0, 1)
            item[2].setStretch(1, 8)
            item[2].setStretch(2, 4)
            item[2].setStretch(3, 4)
            item[2].setStretch(4, 1)

    def addFileSelectionItem(self):
        enableCheckbox = QCheckBox()
        filePathWidget = QLineEdit()
        fileBurnAddrWidget = QLineEdit("0x00000")
        openFileButton = QPushButton(tr("OpenFile"))
        removeButton = QPushButton()
        removeButton.setProperty("class", "remove_file_selection")
        oneFilePathWidget = QWidget()
        oneFilePathWidgetLayout = QHBoxLayout()
        oneFilePathWidget.setLayout(oneFilePathWidgetLayout)
        oneFilePathWidgetLayout.addWidget(enableCheckbox)
        oneFilePathWidgetLayout.addWidget(filePathWidget)
        oneFilePathWidgetLayout.addWidget(fileBurnAddrWidget)
        oneFilePathWidgetLayout.addWidget(openFileButton)
        oneFilePathWidgetLayout.addWidget(removeButton)        

        filesItemLen = len(self.fileSelectWidgets)
        hideAddrWidget = True
        if filesItemLen != 0 and not self.fileSelectWidgets[filesItemLen-1][4].isHidden():
            hideAddrWidget = False
        if filesItemLen == 0:
            removeButton.hide()
        elif filesItemLen == 1:
            self.fileSelectWidgets[0][7].show()
        #                0        1                   2                       3               4                   5               6           7             8             
        item =          ["kfpkg", oneFilePathWidget, oneFilePathWidgetLayout, filePathWidget, fileBurnAddrWidget, openFileButton, False,      removeButton, enableCheckbox]
        # for "bin":    ["bin", oneFilePathWidget,   oneFilePathWidgetLayout, filePathWidget, fileBurnAddrWidget, openFileButton, isFirmware, removeButton, enableCheckbox]
        self.fileSelectWidgets.append(item)

        self.setFileSelectItemLayout(item, hideAddrWidget)

        openFileButton.clicked.connect(lambda:self.selectFile(item))
        removeButton.clicked.connect(lambda:self.removeFileSelectionItem(item))
        self.fileSelectLayout.addWidget(oneFilePathWidget)
        return item

    def removeFileSelectionItem(self, item):
        if self.packing:
            self.hintSignal.emit(tr("Busy"), tr("Please wait, packing ..."))
            return
        if len(self.fileSelectWidgets) <= 1:
            return
        item[5].clicked.disconnect()
        item[7].clicked.disconnect()
        item[1].setParent(None)
        self.fileSelectWidgets.remove(item)
        if len(self.fileSelectWidgets) == 1:
            self.fileSelectWidgets[0][7].hide()
        self.downloadWidget.resize(self.downloadWidget.width(), 58)
        self.setWindowSize(self.width())

    def initWindow(self):
        QToolTip.setFont(QFont('SansSerif', 10))
        # main layout
        self.frameWidget = QWidget()
        mainWidget = QWidget()
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
        self.FuncCombobox = ComboBox()
        self.FuncCombobox.addItem(tr("Firmware"))
        self.FuncCombobox.addItem(tr("Erase"))
        self.langButton.setProperty("class", "menuItemLang")
        self.skinButton.setProperty("class", "menuItem2")
        self.aboutButton.setProperty("class", "menuItem3")
        self.langButton.setObjectName("menuItem")
        self.skinButton.setObjectName("menuItem")
        self.aboutButton.setObjectName("menuItem")
        self.FuncCombobox.setObjectName("funcSelect")
        menuLayout.addWidget(self.langButton)
        menuLayout.addWidget(self.skinButton)
        menuLayout.addWidget(self.aboutButton)
        menuLayout.addStretch(0)
        menuLayout.addWidget(self.FuncCombobox)

        # widgets erase configuration
        self.eraseGroupBox = QGroupBox(tr("Erase settings"))
        self.eraseGroupBox.hide()
        settingLayout.addWidget(self.eraseGroupBox)
        eraseLayout = QGridLayout()
        self.eraseGroupBox.setLayout(eraseLayout)
        self.eraseModeCombobox = ComboBox()
        self.eraseModeCombobox.addItem(tr("Partial erase"))
        self.eraseModeCombobox.addItem(tr("Chip erase"))
        self.eraseAddr = QLineEdit("0x00000")
        self.eraseLen = QLineEdit("1")
        self.eraseLenUnit = ComboBox()
        self.eraseLenUnit.addItem("MiB")
        self.eraseLenUnit.addItem("KiB")
        self.eraseLenUnit.addItem("B")
        self.eraseLoadConfigCombobox = ComboBox()
        for key in self.eraseTemplateConfigs:
            self.eraseLoadConfigCombobox.addItem(key)
        self.eraseLoadButton = QPushButton(tr("Load"))
        eraseLayout.addWidget(QLabel(tr("Mode")), 0, 0, 1, 1)
        eraseLayout.addWidget(QLabel(tr("Address")), 1, 0, 1, 1)
        eraseLayout.addWidget(QLabel(tr("Length")), 2, 0, 1, 1)
        eraseLayout.addWidget(QLabel(tr("Load Template")), 3, 0, 1, 1)
        eraseLayout.addWidget(self.eraseModeCombobox, 0, 1, 1, 2)
        eraseLayout.addWidget(self.eraseAddr, 1, 1, 1, 2)
        eraseLayout.addWidget(self.eraseLen, 2, 1, 1, 1)
        eraseLayout.addWidget(self.eraseLenUnit, 2, 2, 1, 1)
        eraseLayout.addWidget(self.eraseLoadConfigCombobox, 3, 1, 1, 1)
        eraseLayout.addWidget(self.eraseLoadButton, 3, 2, 1, 1)
        
        # widgets file select
        self.fileSelectGroupBox = QGroupBox(tr("SelectFile"))
        # container
        settingLayout.addWidget(self.fileSelectGroupBox)
        self.fileSelectContainerLayout = QVBoxLayout()
        self.fileSelectGroupBox.setLayout(self.fileSelectContainerLayout)
        # file selection
        self.fileSelecWidget = QWidget()
        self.fileSelectLayout = QVBoxLayout()
        self.fileSelecWidget.setLayout(self.fileSelectLayout)
        self.fileSelectContainerLayout.addWidget(self.fileSelecWidget)
        
        # add file selection item
        self.addFileSelectionItem()
        
        # add fileselection functions
        mergeBinWidget = QWidget()
        mergeBinWidgetLayout = QHBoxLayout()
        mergeBinWidget.setLayout(mergeBinWidgetLayout)
        self.addFileButton = QPushButton(tr("Add File"))
        self.packFilesButton = QPushButton(tr("Pack to kfpkg"))
        self.mergeBinButton = QPushButton(tr("Merge to .bin"))
        mergeBinWidgetLayout.addWidget(self.addFileButton)
        mergeBinWidgetLayout.addWidget(self.packFilesButton)
        mergeBinWidgetLayout.addWidget(self.mergeBinButton)
        self.fileSelectContainerLayout.addWidget(mergeBinWidget)

        # widgets board select
        boardSettingsGroupBox = QGroupBox(tr("BoardSettings"))
        settingLayout.addWidget(boardSettingsGroupBox)
        boardSettingsLayout = QGridLayout()
        boardSettingsGroupBox.setLayout(boardSettingsLayout)
        self.boardLabel = QLabel(tr("Board"))
        self.boardCombobox = ComboBox()
        for key in self.boardsInfo:
            self.boardCombobox.addItem(key)
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
        serialPortLabel = QLabel(tr("SerialPort"))
        serailBaudrateLabel = QLabel(tr("SerialBaudrate"))
        slowModeLabel = QLabel(tr("Speed mode"))
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
        self.slowModeCombobox = ComboBox()
        self.slowModeCombobox.addItem(tr("Slow mode"))
        self.slowModeCombobox.addItem(tr("Fast mode"))
        slowModeLabel.setToolTip(tr("slow mode tips"))
        self.slowModeCombobox.setToolTip(tr("slow mode tips"))

        serialSettingsLayout.addWidget(serialPortLabel,0,0)
        serialSettingsLayout.addWidget(serailBaudrateLabel, 1, 0)
        serialSettingsLayout.addWidget(slowModeLabel, 2, 0)
        serialSettingsLayout.addWidget(self.serialPortCombobox, 0, 1)
        serialSettingsLayout.addWidget(self.serailBaudrateCombobox, 1, 1)
        serialSettingsLayout.addWidget(self.slowModeCombobox, 2, 1)
        serialSettingsGroupBox.setLayout(serialSettingsLayout)
        settingLayout.addWidget(serialSettingsGroupBox)

        # widgets SPI flash settings
        spiFlashSettingsGroupBox = QGroupBox(tr("SpiFlashSettings"))
        spiFlashSettingsLayout = QGridLayout()
        spiFlashIoModeLabel = QLabel(tr("IO mode"))
        spiFlashIoModeLabel.setToolTip(tr("flash io mode tips"))
        self.spiFlashIoModeCombobox = ComboBox()
        self.spiFlashIoModeCombobox.addItem(tr("DIO mode"))
        self.spiFlashIoModeCombobox.addItem(tr("QIO mode"))
        self.spiFlashIoModeCombobox.setToolTip(tr("flash io mode tips"))
        spiFlashSettingsLayout.addWidget(spiFlashIoModeLabel,0,0)
        spiFlashSettingsLayout.addWidget(self.spiFlashIoModeCombobox, 0, 1)
        spiFlashSettingsGroupBox.setLayout(spiFlashSettingsLayout)
        settingLayout.addWidget(spiFlashSettingsGroupBox)

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
        # widgets erase area
        self.eraseButton = QPushButton(tr("Erase"))
        downloadLayout.addWidget(self.eraseButton)
        self.eraseButton.hide()
        self.eraseStatus = QLabel()
        self.eraseStatus.hide()
        downloadLayout.addWidget(self.eraseStatus)

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
        print("config file path:", parameters.configFilePath)

    def initEvent(self):
        self.serialPortCombobox.clicked.connect(self.portComboboxClicked)
        self.errorSignal.connect(self.errorHint)
        self.hintSignal.connect(self.hint)
        self.downloadResultSignal.connect(self.downloadResult)
        self.eraseResultSignal.connect(self.eraseResult)
        self.eraseStatusSignal.connect(self.setEraseStatus)
        self.showSerialComboboxSignal.connect(self.showCombobox)
        self.updateProgressSignal.connect(self.updateProgress)
        self.updateProgressPrintSignal.connect(self.updateProgressPrint)
        self.langButton.clicked.connect(self.langChange)
        self.skinButton.clicked.connect(self.skinChange)
        self.aboutButton.clicked.connect(self.showAbout)
        self.FuncCombobox.currentIndexChanged.connect(self.changeFunc)
        self.downloadButton.clicked.connect(self.download)
        self.eraseButton.clicked.connect(self.erase)
        self.eraseLoadButton.clicked.connect(self.eraseLoadConfig)

        self.eraseModeCombobox.currentIndexChanged.connect(self.eraseModechange)

        self.addFileButton.clicked.connect(lambda: self.fileSelectLayout.addWidget(self.addFileSelectionItem()[1]))
        self.packFilesButton.clicked.connect(self.packFiles)
        self.mergeBinButton.clicked.connect(self.mergeBin)

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
    
    def changeFunc(self):
        if self.burning or self.packing or self.erasing:
            self.hintSignal.emit(tr("Busy"), tr("Busy"))
            return
        func = self.FuncCombobox.currentText()
        if func == tr("Erase"):
            self.funcSwitch("Erase")
        elif func == tr("Firmware"):
            self.funcSwitch("Firmware")
        self.setWindowSize()
    
    def funcSwitch(self, func):
        # erase mode
        if func == "Erase":
            self.fileSelectGroupBox.hide()
            self.downloadButton.hide()
            self.burnPositionCombobox.hide()
            self.burnPositionLabel.hide()
            self.eraseButton.show()
            self.eraseGroupBox.show()
            self.eraseStatus.show()
            self.statusBarStauts.setText("<font color=%s>%s</font>" %("#1aac2d", tr("EraseHint")))
        # firmware download mode
        elif func == "Firmware":
            self.eraseButton.hide()
            self.eraseGroupBox.hide()
            self.eraseStatus.hide()
            self.burnPositionLabel.show()
            self.burnPositionCombobox.show()
            self.fileSelectGroupBox.show()
            self.downloadButton.show()
            self.statusBarStauts.setText("<font color=%s>%s</font>" %("#1aac2d", tr("DownloadHint")))

    def highlightFirmwarePath(self, item, firmware):
        if firmware:
            item[3].setProperty("class", "qLineEditHighlight")
            # item[4].setText("0x00000")
        else:
            item[3].setProperty("class", "qLineEditNormal")
        self.frameWidget.style().unpolish(item[3])
        self.frameWidget.style().polish(item[3])
        self.frameWidget.update()

    def eraseModechange(self):
        if self.eraseModeCombobox.currentText() == tr("Chip erase"):
            self.eraseAddr.setText("0x00000")
            self.eraseLen.setText(tr("Full chip"))
            self.eraseAddr.setDisabled(True)
            self.eraseLen.setDisabled(True)
            self.eraseLenUnit.setDisabled(True)
        else:
            self.eraseAddr.setText("0x00000")
            self.eraseLen.setText("0")
            self.eraseAddr.setDisabled(False)
            self.eraseLen.setDisabled(False)
            self.eraseLenUnit.setDisabled(False)

    def erase(self):
        if self.erasing:
            if self.erasingCanCancel:
                hint = "<font color=%s>%s</font>" %("#ff0d0d", tr("Erase Canceling"))
                self.eraseStatus.setText(hint)
                self.kflash.kill()
                return
            self.errorSignal.emit(tr("Busy"), tr("Busy"))
            return
        self.erasing = True
        self.erasingCanCancel = True
        self.setEraseButton(True) # show cancel button
        self.eraseResultSignal.emit(False, "", True)
        isChipeErase = False
        if self.eraseModeCombobox.currentText() == tr("Chip erase"):
            isChipeErase = True
        if not isChipeErase:
            try:
                addr = self.eraseAddr.text()
                if addr.startswith("0x"):
                    addr = int(addr, 16)
                else:
                    addr = int(addr, 10)
            except Exception:
                self.errorSignal.emit(tr("Address error"), tr("Address error"))
                self.erasing = False
                self.setEraseButton(False)
                return
            try:
                length_text = self.eraseLen.text()
                if length_text.startswith("0x"):
                    length = int(length_text, 16)
                else:
                    length = int(length_text)
                unit = self.eraseLenUnit.currentText()
                if unit == "MiB":
                    length *= 1024 * 1024
                elif unit == "KiB":
                    length *= 1024
            except Exception:
                self.errorSignal.emit(tr("Length error"), tr("Length error"))
                self.erasing = False
                self.setEraseButton(False)
                return
            if (addr ==0 and length == 0) or (addr != 0 and length == 0) or addr < 0 or length < 0:
                self.errorSignal.emit(tr("Address and length error"), tr("Address and length error"))
                self.erasing = False
                self.setEraseButton(False)
                return
            if addr + length > 16 * 1024 * 1024: # limit 16MiB
                reply = QMessageBox.question(self, tr("Continue") + " ?",
                                     f'{addr + length} > 16MiB, ' + tr("Continue") + " ?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply != QMessageBox.Yes:
                    self.erasing = False
                    self.setEraseButton(False)
                    return
            eraseTimeEstimate = math.ceil(length/65536*0.2) # 0.16s~0.3s every block(64K), full chip ~50s, 0.07s every sector(4K)
        else: # full chip erase
            addr = 0
            length = "all"
            eraseTimeEstimate = math.ceil(50) # 16MiB Flash full chip erase time
            length_text = "16"
            unit = "MiB"

        config, err, msg = self.getSerialSettings()
        if not config:
            self.errorSignal.emit(err, msg)
            self.erasing = False
            self.setEraseButton(False)
            return
        
        self.eraseStatus.setText("<font color=%s>%s</font>" %("#0eb40e", tr("Preparing Erase") ))
        eraseThread = threading.Thread(target=self.eraseProcess, args=(addr, length, config['dev'], config['baud'], config['board'], config['color'], config['slow']))
        eraseThread.setDaemon(True)
        eraseThread.start()
        eraseStatusThread = threading.Thread(target=self.updateEraseStatus, args=(length_text, unit, eraseTimeEstimate))
        eraseStatusThread.setDaemon(True)
        eraseStatusThread.start()
    
    def setEraseButton(self, cancel):
        self.eraseButton.setEnabled(True)
        if cancel:
            self.eraseButton.setText(tr("Cancel"))
            self.eraseButton.setProperty("class", "redbutton")
            self.eraseButton.style().unpolish(self.eraseButton)
            self.eraseButton.style().polish(self.eraseButton)
            self.eraseButton.update()
        else:
            self.eraseButton.setText(tr("Erase"))
            self.eraseButton.setProperty("class", "normalbutton")
            self.eraseButton.style().unpolish(self.eraseButton)
            self.eraseButton.style().polish(self.eraseButton)
            self.eraseButton.update()
    
    def setEraseStatus(self, msg):
        self.eraseStatus.setText(msg)
    
    def eraseLoadConfig(self):
        configName = self.eraseLoadConfigCombobox.currentText()
        config = self.eraseTemplateConfigs
        if configName in config and config[configName][2] in self.units:
            self.eraseModeCombobox.setCurrentText(tr("Partial erase"))
            self.eraseAddr.setDisabled(False)
            self.eraseLen.setDisabled(False)
            self.eraseLenUnit.setDisabled(False)
            self.eraseAddr.setText(config[configName][0])
            self.eraseLen.setText(config[configName][1])
            self.eraseLenUnit.setCurrentText(config[configName][2])
        else:
            self.errorSignal.emit(tr("Error"), tr("Load erase config file error"))

    def onEraseProgress(self, fileTypeStr, current, total, speedStr):
        if current >= total:
            self.erasingCanCancel = False
            self.eraseButton.setDisabled(True)

    def updateEraseStatus(self, length_text, unit, timeEstimate):
        timeElapsed = 0
        while self.erasing:
            if self.erasingCanCancel:
                time.sleep(0.1)
                continue
            timeLast = timeEstimate - timeElapsed
            if timeLast < 0:
                timeLast = 0
            msg = "<font color=%s>%s</font>" %("#0eb40e", 
                    tr("Erase")+" {}{}, wait about {} S".format(length_text, unit, timeLast) )
            self.eraseStatusSignal.emit(msg)
            timeElapsed += 1
            time.sleep(1)

    def eraseProcess(self, addr, length, dev, baud, board, color, slow):
        errMsg = ""
        success = True
        try:
            self.kflash.process(addr=str(addr), length=str(length), terminal=False, dev=dev, baudrate=baud, board=board, file="erase", noansi=not color, slow_mode=slow, callback=self.onEraseProgress)
        except Exception as e:
            errMsg = tr2(str(e))
            if str(e) != "Burn SRAM OK":
                success = False
        if success:
            self.eraseResultSignal.emit(True, errMsg, False)
        else:
            self.eraseResultSignal.emit(False, errMsg, False)

    def eraseResult(self, success, msg, clear):
        if clear:
            self.statusBarStauts.setText("")
            return
        if success:
            self.hintSignal.emit(tr("Success"), tr("Erase success"))
            self.erasing = False # set here for updateEraseStatus
            self.statusBarStauts.setText("<font color=%s>%s</font>" %("#1aac2d", tr("Erase success")))
        else:
            if msg == tr("Cancel"):
                self.statusBarStauts.setText("<font color=%s>%s</font>" %("#ff1d1d", tr("Erase Canceled")))
                self.erasing = False # set here for updateEraseStatus
            else:
                msg = tr("ErrorSettingHint") + "\n\n"+msg
                self.errorSignal.emit(tr("Error"), msg)
                self.erasing = False # set here for updateEraseStatus
                self.statusBarStauts.setText("<font color=%s>%s</font>" %("#ff1d1d", tr("Erase fail")))
        self.eraseStatus.setText('')
        self.setEraseButton(False)

    def fileSelectShow(self, item, name, addr=None, firmware=None, enable=True, loadFirst = False):
        isKfpkg = False
        if self.isKfpkg(name):
            isKfpkg = True 
        if not item: # add item from param
            if loadFirst:
                item = self.fileSelectWidgets[0]
            else:
                item = self.addFileSelectionItem()
            if isKfpkg:
                self.highlightFirmwarePath(item, False)
                self.setFileSelectItemLayout(item, True)
            else:
                item[4].setText("0x%06x" %(addr))
                self.setFileSelectItemLayout(item, False)
                if self.isFileFirmware(name):
                    self.highlightFirmwarePath(item, True)
                    item[6] = True
                else:
                    self.highlightFirmwarePath(item, False)
                    item[6] = False
            item[3].setText(name)
            item[8].setChecked(enable)
            return

        if isKfpkg:
            self.setFileSelectItemLayout(item, True)
            self.highlightFirmwarePath(item, False)
            # disable other items
            for i in self.fileSelectWidgets:
                i[8].setChecked(False)
            # only enable this kfpkg
            item[8].setChecked(True)
        else:
            self.setFileSelectItemLayout(item, False)
            if self.isFileFirmware(name):
                self.highlightFirmwarePath(item, True)
                item[4].setText("0x00000")
            else:
                self.highlightFirmwarePath(item, False)
            # disable kfpkg file
            for i in self.fileSelectWidgets:
                if self.isKfpkg(i[3].text()):
                    i[8].setChecked(False)
            # enable this bin file
            item[8].setChecked(True)
            if self.isFileFirmware(name):
                item[6] = True
        item[3].setText(name)

    # return: ("bin", [(file path, burn addr, add prefix, enable),...])
    #      or ("kfpkg", file path)
    #      or (None, msg)
    def getBurnFilesInfo(self):
        files = []
        fileType = ""
        for item in self.fileSelectWidgets:
            path = item[3].text().strip()
            enable = item[8].isChecked()
            if self.isFileFirmware(path):
                item[6] = True
                self.highlightFirmwarePath(item, True)
            else:
                item[6] = False
                self.highlightFirmwarePath(item, False)
            try:
                addr = int(item[4].text(),16)
                if enable:
                    if addr%(0x1000) != 0: # 4KiB align
                        return (None, tr("Adress must align with 4KiB(0x1000)"))
            except Exception:
                addr = 0
            if not enable:
                continue
            if path=="" or not os.path.exists(path):
                    return (None, tr("Line {}: ").format(self.fileSelectWidgets.index(item)+1)+tr("File path error")+":"+path)
            if self.isKfpkg(path):
                if fileType == "bin":
                    return (None, tr("Can not select kfpkg and bin files at the time"))
                fileType = "kfpkg"
                if len(files) != 0:
                    return (None, tr("Only support one kfpkg file"))
                files = path
            else:
                if fileType == "kfpkg":
                    return (None, tr("Can not select kfpkg and bin files at the time"))
                fileType = "bin"
                prefix = item[6]
                files.append( (path, addr, prefix, enable) )
        if len(files) == 0:
            return (None, tr("Please select file"))
        return (fileType, files)

    class KFPKG():
        def __init__(self):
            self.fileInfo = {"": "0.1.0", "files": []}
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
            listName = os.path.join(tempfile.gettempdir(), "kflash_gui_tmp_list.json")
            self.listDump(listName)
            try:
                with zipfile.ZipFile(path, "w") as zip:
                    for name,path in self.filePath.items():
                        zip.write(path, arcname=name, compress_type=zipfile.ZIP_DEFLATED)
                    zip.write(listName, arcname="flash-list.json", compress_type=zipfile.ZIP_DEFLATED)
                    zip.close()
            except Exception as e:
                os.remove(listName)
                raise e
            os.remove(listName)

    def checkFilesAddrValid(self, fileType, files):
        if fileType == "bin":
            files.sort(key=lambda file:file[1])
            startAddr = -1
            fileSize  = 0
            fileShortLast = ""
            count = 0
            for file, addr, firmware, enable in files:
                if not enable:
                    continue
                fileShort = ".../"+"/".join(file.split("/")[-2:])
                if startAddr + fileSize > addr:
                    return (False, tr("File address error")+": {} {} 0x{:X}, {} {} {} [0x{:X},0x{:X}]".format(fileShort, tr("start from"), addr, tr("but file"), fileShortLast, tr("address range is"), startAddr, startAddr+fileSize) )
                fileSize = os.path.getsize(file)
                startAddr = addr
                fileShortLast = fileShort
                count += 1
            if count == 0:
                return (False, tr("No file selected"))
        return (True, "")

    def packFiles(self):
        if self.packing:
            self.hintSignal.emit(tr("Busy"), tr("Please wait, packing ..."))
            return
        self.packing = True

        fileType, files = self.getBurnFilesInfo()
        if not fileType:
            self.errorSignal.emit(tr("Error"), files)
            self.packing = False
            return
        
        if fileType=="kfpkg":
            self.errorSignal.emit(tr("Error"), tr("Can not pack kfpkg"))
            self.packing = False
            return

        ok, msg = self.checkFilesAddrValid(fileType, files)
        if not ok:
            self.errorSignal.emit(tr("Error"), msg)
            self.packing = False
            return

        # select saving path
        if not os.path.exists(self.saveKfpkDir):
            self.saveKfpkDir = os.getcwd()
        fileName_choose, filetype = QFileDialog.getSaveFileName(self,  
                                    tr("Save File"),  
                                    self.saveKfpkDir,
                                    "k210 packages (*.kfpkg)")
        if fileName_choose == "":
            # self.errorSignal.emit(tr("Error"), tr("File path error"))
            self.packing = False
            return
        if not self.isKfpkg(fileName_choose):
            fileName_choose += ".kfpkg"
        self.saveKfpkDir = os.path.split(fileName_choose)[0]

        # pack and save
        t = threading.Thread(target=self.packFileProccess, args=(files, fileName_choose,))
        t.setDaemon(True)
        t.start()
    
    def packFileProccess(self, files, fileSaveName):
        # generate flash-list.json
        kfpkg = self.KFPKG()
        try:
            for path, addr, prefix, enable in files:
                if enable:
                    kfpkg.addFile(addr, path, prefix)
        except Exception as e:
            self.errorSignal.emit(tr("Error"), tr("Pack kfpkg fail")+":"+str(e))
            self.packing = False
            return

        # write kfpkg file
        try:
            kfpkg.save(fileSaveName)
        except Exception as e:
            self.errorSignal.emit(tr("Error"), tr("Pack kfpkg fail")+":"+str(e))
            self.packing = False
            return
        self.hintSignal.emit(tr("Success"), tr("Save kfpkg success"))
        self.packing = False

    def getBurnFilesInfoFromKfpkg(self, kfpkg):
        tempDir = tempfile.gettempdir()
        listFileName = "flash-list.json"
        try:
            zip = zipfile.ZipFile(kfpkg, mode="r")
            zip.extract(listFileName, tempDir)
            with open(os.path.join(tempDir, listFileName)) as f:
                info = json.load(f)
            filesInfo = {}
            for fileInfo in info["files"]:
                filesInfo[fileInfo["bin"]] = [fileInfo["address"], fileInfo["sha256Prefix"]]
            print(filesInfo, zip.namelist())
            binFiles = zip.namelist()
            binFiles.remove(listFileName)
            for file in binFiles:
                zip.extract(file, tempDir)
                self.zipTempFiles.append( (tempDir + "/" + file, filesInfo[file][0], filesInfo[file][1], True ) )
            zip.close()
        except Exception as e:
            return (None, str(e))
        return (self.zipTempFiles,"")

    def cleanKfpkgTempFiles(self):
        tempDir = tempfile.gettempdir()
        try:
            for file in self.zipTempFiles:
                os.remove(file[0])
        except Exception:
            pass
        self.zipTempFiles = []

    def mergeBin(self):
        if self.packing:
            self.hintSignal.emit(tr("Busy"), tr("Please wait, packing ..."))
            return
        self.packing = True
        fileType, files = self.getBurnFilesInfo()
        if not fileType:
            self.errorSignal.emit(tr("Error"), files)
            self.cleanKfpkgTempFiles()
            self.packing = False
            return
        if fileType == "kfpkg":
            files, msg = self.getBurnFilesInfoFromKfpkg(files)
            fileType = "bin"
            if not files:
                self.errorSignal.emit(tr("Error"), msg)
                self.cleanKfpkgTempFiles()
                self.packing = False
                return
        
        ok, msg = self.checkFilesAddrValid(fileType, files)
        if not ok:
            self.errorSignal.emit(tr("Error"), msg)
            self.packing = False
            self.cleanKfpkgTempFiles()
            return

        # select saving path
        if not os.path.exists(self.saveKfpkDir):
            self.saveKfpkDir = os.getcwd()
        fileName_choose, filetype = QFileDialog.getSaveFileName(self,  
                                    tr("Save File"),  
                                    self.saveKfpkDir,
                                    "Binary file (*.bin)")
        if fileName_choose == "":
            # self.errorSignal.emit(tr("Error"), tr("File path error"))
            self.packing = False
            self.cleanKfpkgTempFiles()
            return
        if not fileName_choose.endswith(".bin"):
            fileName_choose += ".bin"
        self.saveKfpkDir = os.path.split(fileName_choose)[0]

        # pack and save
        t = threading.Thread(target=self.mergeBinProccess, args=(files, fileName_choose,))
        t.setDaemon(True)
        t.start()
    
    def mergeBinProccess(self, files, fileSaveName):
        self.updateProgressPrintSignal.emit(tr("Merging, please wait ..."))
        files.sort(key=lambda file:file[1])
        bin = b''
        aesFlag = b'\x00'
        startAddrLast = files[0][1]
        fileSizeLast  = 0
        if files[0][2]: # firmware
            name = files[0][0]
            size = os.path.getsize(name)
            f = open(name, "rb")
            firmware = f.read()
            f.close()

            bin += aesFlag                # add aes key flag
            bin += struct.pack('I', size) # add firmware length
            bin += firmware               # add firmware content
            sha256Hash = hashlib.sha256(bin).digest()
            bin += sha256Hash             # add parity

            startAddrLast = 0
            fileSizeLast = len(bin)
            files.remove(files[0])

        for file, addr, firmware, enable in files:
            if not enable:
                continue
            fillLen = addr - (startAddrLast + fileSizeLast)
            if fillLen > 0:               # fill 0xFF
                fill = bytearray([0xFF for i in range(fillLen)])
                bin += fill
            with open(file, "rb") as f:   # add bin file content
                bin += f.read()
            startAddrLast = addr
            fileSizeLast = os.path.getsize(file)
        with open(fileSaveName, "wb") as f:
            f.write(bin)
        self.updateProgressPrintSignal.emit(tr("Save merged bin file success"))
        self.hintSignal.emit(tr("Success"), tr("Save merged bin file success"))
        self.packing = False
        self.cleanKfpkgTempFiles()

    def selectFile(self, item):
        if self.packing:
            self.hintSignal.emit(tr("Busy"), tr("Please wait, packing ..."))
            return
        index = self.fileSelectWidgets.index(item)
        oldPath = item[3].text()
        if oldPath=="" and index > 0:
            oldPath = self.fileSelectWidgets[index - 1][3].text()
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
        self.fileSelectShow(item, fileName_choose)

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
    
    def isFileFirmware(self, name):
        isFirmware = False
        if not os.path.exists(name):
            return False
        if name.endswith(".bin"):
            f = open(name, "rb")
            start_bytes = f.read(6)
            f.close()                
            for flags in self.firmware_start_bytes:
                if flags in start_bytes:
                    isFirmware = True
                    break
        return isFirmware     

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
        paramObj.board    = self.boardCombobox.currentIndex()
        paramObj.burnPosition = self.burnPositionCombobox.currentText()
        paramObj.baudRate = self.serailBaudrateCombobox.currentIndex()
        paramObj.skin = self.param.skin
        paramObj.language = translation.current_lang
        for item in self.fileSelectWidgets:
            path = item[3].text()
            try:
                addr = int(item[4].text(),16)
            except Exception:
                addr = 0
            fileInfo = (path, addr, item[6], item[8].isChecked())
            paramObj.files.append(fileInfo)
        if self.slowModeCombobox.currentIndex()==0:
            paramObj.slowMode = True
        else:
            paramObj.slowMode = False
        
        if self.spiFlashIoModeCombobox.currentIndex()==0:
            paramObj.ioMode = "dio"
        else:
            paramObj.ioMode = "qio"

        paramObj.save(parameters.configFilePath)

    def programStartGetSavedParameters(self):
        paramObj = paremeters_save.ParametersToSave()
        paramObj.load(parameters.configFilePath)
        translation.setLanguage(paramObj.language)
        self.param = paramObj

    def updateFrameParams(self):
        pathLen = len(self.param.files)
        if pathLen != 0:
            if len(self.param.files[0]) != 4: # [ (path, addr, prefix, enable), ...]
                return
            count = 0
            for path, addr, firmware, enable  in self.param.files:
                firmware = None if (not firmware) else True
                if count == 0:
                    self.fileSelectShow(None, path, addr, firmware, enable=enable, loadFirst = True)
                else:
                    self.fileSelectShow(None, path, addr, firmware, enable=enable, loadFirst = False)
                count += 1
        if type(self.param.board) == str:
            self.param.board = 0
        self.boardCombobox.setCurrentIndex(self.param.board)
        self.burnPositionCombobox.setCurrentText(self.param.burnPosition)
        self.serailBaudrateCombobox.setCurrentIndex(self.param.baudRate)
        if self.param.slowMode:
            self.slowModeCombobox.setCurrentIndex(0)
        else:
            self.slowModeCombobox.setCurrentIndex(1)

        if self.param.ioMode == 'dio':
            self.spiFlashIoModeCombobox.setCurrentIndex(0)
        else:
            self.spiFlashIoModeCombobox.setCurrentIndex(1)

    def closeEvent(self, event):
        try:
            self.programExitSaveParameters()
            self.kflash.kill()
            self.kflash.checkKillExit()
        except Exception:
            pass
        finally:
            event.accept()

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
        file.close()

    def showAbout(self):
        QMessageBox.information(self, tr("About"),"<h1 style='color:#f75a5a';margin=10px;>"+parameters.appName+
                                '</h1><br><b style="color:#08c7a1;margin = 5px;">V'+str(helpAbout.versionMajor)+"."+
                                str(helpAbout.versionMinor)+"."+str(helpAbout.versionDev)+
                                "</b><br><br>"+helpAbout.date+"<br><br>"+tr("help str")+"<br><br>"+helpAbout.strAbout())

    def autoUpdateDetect(self):
        auto = autoUpdate.AutoUpdate()
        if auto.detectNewVersion():
            self.hintSignal.emit(tr("Upgrade"), tr("Upgrade available, please download new release in release page"))
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
        self.progressbar.setValue(int(percent))
    
    def updateProgressPrint(self, str):
        self.statusBarStauts.setText(str)

    def kflash_py_printCallback(self, *args, **kwargs):
        # end = kwargs.pop('end', "\n")
        msg = ""
        for i in args:
            msg += str(i)
        msg.replace("\n", " ")
        self.updateProgressPrintSignal.emit(msg)

    def progress(self, fileTypeStr, current, total, speedStr):
        self.updateProgressSignal.emit(fileTypeStr, current, total, speedStr)

    def getSerialSettings(self):
        color = False
        board = "dan"
        boardText = self.boardCombobox.currentText()
        board = self.boardsInfo[boardText]

        sram = False
        if self.burnPositionCombobox.currentText()==tr("SRAM") or \
            self.burnPositionCombobox.currentText()==tr_en("SRAM"):
            sram = True
        try:
            baud = int(self.serailBaudrateCombobox.currentText())
        except Exception:
            return (None, tr("Error"), tr("BaudrateError"))
            
        dev = ""
        try:
            dev  = self.serialPortCombobox.currentText().split()[0]
        except Exception:
            pass
        if dev=="":
            return (None, tr("Error"), tr("PleaseSelectSerialPort"))
        slow = self.slowModeCombobox.currentIndex()==0
        iomode = "dio" if self.spiFlashIoModeCombobox.currentIndex()==0 else "qio"
        return ({
            "color": color,
            "board": board,
            "sram": sram,
            "dev": dev,
            "slow": slow,
            "baud": baud,
            "iomode": iomode
        },None, None)

    def download(self):
        if self.packing:
            self.hintSignal.emit(tr("Busy"), tr("Please wait, packing ..."))
            return
        if self.burning:
            self.terminateBurn()
            return
        fileType, filesInfo = self.getBurnFilesInfo()
        if not fileType or not filesInfo:
            self.errorSignal.emit(tr("Error"), filesInfo)
            return
        ok, msg = self.checkFilesAddrValid(fileType, filesInfo)
        if not ok:
            self.errorSignal.emit(tr("Error"), msg)
            return

        self.burning = True
        # if not self.checkFileName(filename):
        #     self.errorSignal.emit(tr("Error"), tr("FilePathError"))
        #     self.burning = False
        #     return
        
        config, err, msg = self.getSerialSettings()
        if not config:
            self.errorSignal.emit(err, msg)
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
        burnThread = threading.Thread(target=self.flashBurnProcess, args=(config['dev'], config['baud'], config['board'], config['sram'], fileType, filesInfo, self.progress, config['color'], config['slow'], config['iomode']))
        burnThread.setDaemon(True)
        burnThread.start()

    def flashBurnProcess(self, dev, baud, board, sram, fileType, files, callback, color, slow, io_mode):
        success = True
        errMsg = ""
        tmpFile = ""

        if fileType == "kfpkg":
            if sram:
                errMsg = tr("only support bin file when Download to SRAM")
                success = False
            else:
                filename = files
        else:#generate kfpkg
            if sram:
                filename = files[0][0]
            else:
                tmpFile = os.path.join(tempfile.gettempdir(), "kflash_gui_tmp.kfpkg")
                kfpkg = self.KFPKG()
                try:
                    for path, addr, prefix, enable in files:
                        if enable:
                            kfpkg.addFile(addr, path, prefix)
                    kfpkg.save(tmpFile)
                    filename = os.path.abspath(tmpFile)
                except Exception as e:
                    try:
                        os.remove(tmpFile)
                    except Exception:
                        print("can not delete temp file:", tmpFile)
                    errMsg = tr("Pack kfpkg fail")+":"+str(e)
                    success = False
        if success:
            try:
                self.kflash.process(terminal=False, dev=dev, baudrate=baud, board=board, sram = sram, file=filename, callback=callback, noansi=not color, slow_mode=slow, io_mode=io_mode)
            except Exception as e:
                errMsg = tr2(str(e))
                if str(e) != "Burn SRAM OK":
                    success = False
            if tmpFile != "" and filename:
                try:
                    os.remove(filename)
                except Exception:
                    print("Can not delete tmp file:", filename)
        if success:
            self.downloadResultSignal.emit(True, errMsg)
        else:
            self.downloadResultSignal.emit(False, errMsg)
        self.burning = False
            

    def downloadResult(self, success, msg):
        if success:
            self.hintSignal.emit(tr("Success"), tr("DownloadSuccess"))
            self.statusBarStauts.setText("<font color=%s>%s</font>" %("#1aac2d", tr("DownloadSuccess")))
        else:
            if msg == tr("Cancel"):
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
    file.close()
    app.setStyleSheet(qss)
    mainWindow.detectSerialPort()
    t = threading.Thread(target=mainWindow.autoUpdateDetect)
    t.setDaemon(True)
    t.start()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

