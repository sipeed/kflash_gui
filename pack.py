import os, sys, shutil

if os.path.exists("kflash_py/__pycache__"):
    shutil.rmtree("kflash_py/__pycache__")

if os.path.exists("build"):
    shutil.rmtree("build")

if os.path.exists("dist"):
    shutil.rmtree("dist")

if sys.platform.startswith("win32"):
    cmd = 'pyinstaller --add-binary="kflash_gui_data;kflash_gui_data" --add-binary="kflash_py;kflash_py" -i="kflash_gui_data/assets/logo.ico" -w kflash_gui.py'
elif sys.platform.startswith("darwin"):
    cmd = 'pyinstaller --add-data="kflash_gui_data:kflash_gui_data" --add-data="kflash_py:kflash_py" -i="kflash_gui_data/assets/logo.icns" -w kflash_gui.py'
else:
    cmd = 'pyinstaller --add-binary="kflash_gui_data:kflash_gui_data" --add-binary="kflash_py:kflash_py" -i="kflash_gui_data/assets/logo.png" -w kflash_gui.py'

result = os.system(cmd)

if result != 0:
    exit(1)

if sys.platform.startswith("darwin"):
    if os.path.exists("./dist/kflash_gui.dmg"):
        os.remove("./dist/kflash_gui.dmg")

    result = os.system("""create-dmg \
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
    """)

    if result != 0:
        exit(1)
