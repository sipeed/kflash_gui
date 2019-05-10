kflash_gui
=============

Cross platform GUI wrapper for [kflash.py](https://github.com/sipeed/kflash.py.git) (download(/burn) tool for k210)


|  |  |
| -| -|
| ![](kflash_gui_data/assets/screenshot_1.png) | ![](kflash_gui_data/assets/screenshot_2.png) |
| ![](kflash_gui_data/assets/screenshot_download.png) | ![](kflash_gui_data/assets/screenshot_download_en.png) |
| ![](kflash_gui_data/assets/screenshot_en.png) | ![](kflash_gui_data/assets/screenshot_file.png) |


## Features

* Support `*.bin` and `*.kfpgk` file with file picker
* Support development board select
* Support select where the firmware burned to
* Auto scan serial port support
* Baudrate editable
* White skin and night skin support
* Support Chinese and English Language 
* Download(/burn) progress and speed display
* Cancel download support

## Usage

* Select `bin` file or `kfpkg` file
* Select board
* Select where firmware flash to, `Flash` or `SRAM`
* Select serial port
* Select baudrate, `1.5M` recommend
* Click Download to burn firmware or model to board

## If download fail

* Check hardware connection
* Check board selection
* Check serial port selection
* Check baudrate, do not too high
* Check if serial occupied by other software
* Replug in USB cable and try again


---------------------------

## 特性

* 支持 `*.bin` 和 `*.kfpgk` 文件， 支持文件选择器选择
* 支持开发板选择
* 可选择程序烧录到 `Flash` 或者 `SRAM`
* 自动检测电脑上的串口
* 波特率可编辑
* 黑白两种皮肤可供选择
* 界面支持中英文切换
* 支持烧录进度显示和烧录速度显示
* 支持取消下载进程

## 使用方法

* 选择 `bin` 文件或者 `kfpkg` 文件
* 选择开发板
* 选择烧录到开发板的哪个位置 `Flash`（速度慢但是重新上电还可运行） 或者 `SRAM`（`RAM`中运行，下载快断电丢失程序）
* 选择串口
* 选择波特率，推荐`1.5M`
* 点击 `下载` 按钮来开始下载
* 如果需要取消，点击 `取消` 按钮

## 无法下载时检查

* 板子连接是否正确
* 开发板是否选择正确
* 串口是否选择正确
* 串口速度是否选择过高，可以适当降低速度试试
* 串口是否被其它软件占用
* 串口是否出了奇怪的问题，拔掉电脑连接到板子的线重新插一下试试








