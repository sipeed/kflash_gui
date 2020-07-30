#!/bin/bash

cp -rf app ../../dist/
cd ../../dist
mkdir -p app/usr/bin
cp -rf kflash_gui/* app/usr/bin/
if [[ -f /lib/libc.so.6 ]]; then
    echo "copy /lib/libc.so.6 to app/usr/lib"
    cp -f /lib/libc.so.6 app/usr/lib
fi

if [[ -f appimagetool-x86_64.AppImage ]]; then
    rm appimagetool-x86_64.AppImage -f
fi
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage -O appimagetool-x86_64.AppImage
echo "===== download tool end ====="
chmod +x appimagetool-x86_64.AppImage
ls -al
ARCH=x86_64 ./appimagetool-x86_64.AppImage -v app

