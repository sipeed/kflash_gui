import os, sys, shutil

if os.path.exists("kflash_py/__pycache__"):
    shutil.rmtree("kflash_py/__pycache__")

if os.path.exists("build"):
    shutil.rmtree("build")

if os.path.exists("dist"):
    shutil.rmtree("dist")

# pyinstaller generate files
if sys.platform.startswith("win32"):
    # NOTE: Some stupid antivirus software will kill the generated exe by mistake
    cmd = 'pyinstaller --onefile --key=stupidantivirus --add-data="kflash_gui_data;kflash_gui_data" --add-binary="kflash_py;kflash_py" -i="kflash_gui_data/assets/logo.ico" -w kflash_gui.py'
elif sys.platform.startswith("darwin"):
    # NOTE: must use --add-data under darwin, or you will get "Unknown Mach-O header" error
    cmd = 'pyinstaller --add-data="kflash_gui_data:kflash_gui_data" --add-data="kflash_py:kflash_py" -i="kflash_gui_data/assets/logo.icns" -w kflash_gui.py'
else:
    cmd = 'pyinstaller --onefile --add-binary="kflash_gui_data:kflash_gui_data" --add-binary="kflash_py:kflash_py" -i="kflash_gui_data/assets/logo.png" -w kflash_gui.py'

result = os.system(cmd)

if result != 0:
    exit(1)

# create packages
if sys.platform.startswith("win32"):
    if os.path.exists("./dist/kflash_gui.7z"):
        os.remove("./dist/kflash_gui.7z")
    cmd = """bash.exe -c \
        " \
        cd ./dist || exit -1 ; ls ; \
        7z a "kflash_gui.7z" "kflash_gui.exe" -bd -mx9 || exit -1 ; \
        " \
    """
elif sys.platform.startswith("darwin"):
    if os.path.exists("./dist/kflash_gui.dmg"):
        os.remove("./dist/kflash_gui.dmg")
    cmd = """create-dmg \
        --volname "KFlash GUI Installer" \
        --volicon "kflash_gui_data/assets/logo.icns" \
        --background "kflash_gui_data/assets/installer_background_mac.png" \
        --window-pos 200 120 \
        --window-size 800 400 \
        --icon-size 100 \
        --icon "kflash_gui.app" 200 190 \
        --hide-extension "kflash_gui.app" \
        --app-drop-link 600 185 \
        "./dist/kflash_gui.dmg" \
        "./dist/kflash_gui.app"
    """
else:
    if os.path.exists("./dist/kflash_gui.tar.xz"):
        os.remove("./dist/kflash_gui.tar.xz")
    cmd = """sh -c \
        " \
        cd ./dist || exit -1 ; ls ; \
        XZ_OPT=-9 tar -Jcf kflash_gui.tar.xz kflash_gui || exit -1 ; \
        " \
    """

result = os.system(cmd)

if result != 0:
    exit(1)
