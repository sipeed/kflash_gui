appName = "kflash_gui"
strDataDirName = "kflash_gui_data"
strDataAssetsDirName = "kflash_gui_data/assets"
appIcon = "assets/logo.png"
appLogo = "assets/logo.png"
appLogo2 = "assets/logo2.png"

author = "Neucrack"
strDownload = "Download"
strSend = "Send"
strReceive = "Receive"
strFile = "File"
strSerialPort = "Port"
strSerialBaudrate = "Baudrate"
strBoard = "Board"
strSerialBytes = "DataBytes"
strSerialParity = "Parity"
strSerialStopbits = "Stopbits"
strAscii = "ASCII"
strHex = "HEX"
strBoardSettings = "Board Settings"
strSendSettings = "Send Settings"
strOpenFile = "Open File"
strReceiveSettings = "Receive Settings"
strOpen = "OPEN"
strClose = "CLOSE"
strAutoLinefeed = "Auto\nLinefeed\n(ms)"
strAutoLinefeedTime = "200"
strScheduled = "Scheduled\nSend(ms)"
strScheduledTime = "300"
strSelectFile = "Select File"
strSerialSettings = "Serial Settings"
strSerialReceiveSettings = "Receive Settings"
strSerialSendSettings = "Send Settings"
strClearReceive = "ClearReceive"
strAdd = "+"
strFunctionalSend = "Functional Send"
strBaudRateDefault = "115200"
strOpenFailed = "Open Failed"
strOpenReady = "Open Ready"
strClosed = "Closed"
strWriteError = "Send Error"
strReady = "Ready"
strWriteFormatError = "format error"
strCRLF = "<CRLF>"
strTimeFormatError = "Time format error"
strHelp = "HELP"
strAbout = "ABOUT"
strSettings = "Settings"
strNeedUpdate = "Need Update"
strUpdateNow = "update now?"
strUninstallApp = "uninstall app"
strConfigFilePath = "kflash_gui.conf"
strSipeedMaixDock = "Sipeed Maix Dock"
strSipeedMaixBit  = "Sipeed Maix Bit"
strSipeedMaixGoE  = "Sipeed Maix Go(open-ec)"
strSipeedMaixGoD  = "Sipeed Maix Go(CMSIS-DAP)"
strKendriteKd233  = "Kendryte KD233"
strSRAM = "SRAM"
strFlash = "Flash"
strBurnTo = "Burn To"

class ParametersToSave:
    filePath = ""
    board    = strSipeedMaixBit
    burnPosition = strFlash
    baudRate = 2
    skin = 2

    def __init__(self):
        return

    def __del__(self):
        return


