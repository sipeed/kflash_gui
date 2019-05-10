import os, sys, shutil

if os.path.exists("kflash_py/__pycache__"):
    shutil.rmtree("kflash_py/__pycache__")
if sys.platform == "win32":
    cmd = 'pyinstaller --add-data="kflash_gui_data;kflash_gui_data" --add-binary="kflash_py;kflash_py" -i="kflash_gui_data/assets/logo.ico" -w kflash_gui.py'
else:
    cmd = 'pyinstaller --add-data="kflash_gui_data:kflash_gui_data" --add-binary="kflash_py:kflash_py" -i="kflash_gui_data/assets/logo.ico" -w kflash_gui.py'
os.system(cmd)

