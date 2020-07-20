import parameters, os, json

language_en = "en"
language_zh = "zh"
current_lang = language_en

lang_json_list = {}

for f in os.listdir(parameters.translationPathAbs):
    lang = f.split(".")[0][12:]
    if lang == "":
        continue
    f = parameters.translationPathAbs+"/"+f
    with open(f,"r", encoding='utf-8') as fd:
        try:
            jsonObj = json.loads(fd.read())
        except Exception as e:
            print("tranlation:",f," format(json) error!")
            raise e
        lang_json_list[lang] = jsonObj
if len(lang_json_list) == 0:
    raise Exception("No translation file!")


def setLanguage(language):
    global current_lang
    transFileName = "translation_"+language+".json"
    for f in os.listdir(parameters.translationPathAbs):
        if f.endswith(transFileName):
            current_lang = language

def getCurrentLanguage():
    global current_lang
    return current_lang

def tr(str):
    try:
        return lang_json_list[current_lang][str]
    except Exception:
        try:
            return lang_json_list[language_en][str]
        except Exception:
            return str

def tr_en(str):
    return lang_json_list[language_en][str]

def tr2(str):
    ret = str
    key_find = None
    max_find_len = 0
    for key in lang_json_list[current_lang].keys():
        if key in str:
            if len(key) > max_find_len:
                key_find = key
                max_find_len = len(key)
    if key_find:
        ret = ret.replace(key_find, lang_json_list[current_lang][key_find])
    return ret
