import translation, parameters
from translation import tr_en


class ParametersToSave:
    filePath = ""
    board    = parameters.SipeedMaixBit
    burnPosition = tr_en("Flash")
    baudRate = 2
    skin = 2
    language = translation.language_en

    def __init__(self):
        return

    def __del__(self):
        return
