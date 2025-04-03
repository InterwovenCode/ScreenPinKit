<p align="center">
  <img width="18%" align="center" src="https://raw.githubusercontent.com/YaoXuanZhi/ScreenPinKit/main/images/logo.svg" alt="logo">
</p>
  <h1 align="center">
  ScreenPinKit
</h1>
<p align="center">
  A mini screenshot annotation and desktop annotation tool based on PyQt5
</p>

<p align="center">
  <a href="https://discord.gg/VCqKgF7f">
    <img src="https://img.shields.io/badge/Chat-On%20Discord-7289da.svg?sanitize=true" alt="Chat">
  </a>

  <a href="https://pypi.org/project/ScreenPinKit" target="_blank">
    <img src="https://img.shields.io/pypi/v/ScreenPinKit?color=ffa&label=Version" alt="Version">
  </a>

  <a href="">
    <img src="https://img.shields.io/badge/Python-3.8,3.9-aff.svg">
  </a>

  <a href="./LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-dfd.svg">
  </a>

  <a style="text-decoration:none">
    <img src="https://static.pepy.tech/personalized-badge/pyqt-fluent-widgets?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Downloads" alt="Download"/>
  </a>

  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/Platform-Win%2C%20Linux-pink.svg" alt="Platform">
  </a>
</p>

<p align="center">
English | <a href="./README.zh_cn.md">简体中文</a>
</p>

![Interface](https://raw.githubusercontent.com/YaoXuanZhi/ScreenPinKit/main/images/Interface.png)

![OCR](https://raw.githubusercontent.com/YaoXuanZhi/ScreenPinKit/main/images/ocr.png)

## Installation
```shell
# Currently only recommended for Python 3.8 and Python 3.9
## Source installation
#cd src/
#python setup.py install
# pip installation
pip install ScreenPinKit -i https://pypi.org/simple/

ScreenPinKit
```

> **Warning**
> This application uses the third-party library system_hotkey to register global hotkeys. However, since this package hasn't been maintained for over 3 years, it's recommended to install and run it on Python 3.8.

## Development
```sh
conda create -n pyqt5_env python=3.9
conda activate pyqt5_env
git clone https://github.com/YaoXuanZhi/ScreenPinKit ScreenPinKit
cd ScreenPinKit
pip install -r requirements.txt
git submodule update --init

cd src
python main.py
```

![OCR](https://raw.githubusercontent.com/YaoXuanZhi/ScreenPinKit/main/images/source_code_installation_animation.svg)

### Run Examples
After installing the ScreenPinKit package via pip and downloading this repository's code, you can run any example program in the src directory, such as:

```sh
cd src
python main.py

python ./canvas_editor/demos/canvas_editor_demo_full.py

python ./canvas_item/demos/canvas_arrow_demo.py

```

## Package Distribution
```sh
# Windows Defender might report it as a virus - just ignore it to complete packaging
cd src
# Explicitly package the OCR environment, requires explicitly importing related dependency modules in ocr_loader_manager.py
pyinstaller --icon=../images/logo.png --add-data "internal_deps:internal_deps" --windowed main.py -n ScreenPinKit

# Implicitly include built-in OCR environment
# pyinstaller --onefile --hidden-import=cv2 --hidden-import=onnxruntime --hidden-import=pyclipper --hidden-import=shapely --icon=../images/logo.png --add-data "internal_deps:internal_deps" --windowed main.py -n ScreenPinKit
```

## Code Checking & Formatting
```sh
# Use the ruff package for syntax checking and automatic code formatting
pip install ruff

# Run as a linter
ruff check

# Run as a formatter
ruff format
```

## Usage Guide
| Scope | Hotkey | Function |
|-------|-------|-------|
| Global | F7 | Screenshot |
| Global | Shift+F7 | Repeat the last screenshot |
| Global | F4 | Call up screen annotation |
| Global | F2 | Display clipboard image at mouse position |
| Global | Esc | Gradually exit the editing state of the current window |
| Screenshot Window | Ctrl+T | Convert screenshot selection to screen pin |
| Screenshot Window | Shift | Toggle color format on magnifier (rgb/hex) |
| Screenshot Window | C | Copy currently picked color format |
| Pin Window | Ctrl+A | OCR recognition |
| Pin Window | Alt+F | Toggle mouse click-through state |
| Pin Window | Ctrl+C | Copy current pin to clipboard |
| Pin Window | Ctrl+S | Save current pin to disk |
| Pin Window | Ctrl+W | Complete drawing |
| Pin Window | Ctrl+Z | Undo |
| Pin Window | Ctrl+Y | Redo |
| Pin Window | 3x Space | Clear drawing |
| Screen Annotation Window | Alt+L | Hide/show screen annotation content |
| Screen Annotation Window | Ctrl+W | Complete drawing |

Please proceed to [Youtube - ScreenPinKit](https://www.youtube.com/playlist?list=PL3uuKTASzjRYNdl7wYlgUd7agQIA2_y5V)

## References
* [**Snipaste**: Snipaste 是一个简单但强大的截图工具，也可以让你将截图贴回到屏幕上](https://zh.snipaste.com/)
* [**excalidraw**: Design guidelines and toolkits for creating native app experiences](https://excalidraw.com/)
* [**PyQt-Fluent-Widgets**: A fluent design widgets library based on C++ Qt/PyQt/PySide. Make Qt Great Again.](https://github.com/zhiyiYo/PyQt-Fluent-Widgets)
* [**ShareX**: Screen capture, file sharing and productivity tool](https://github.com/ShareX/ShareX)
* [**ppInk**: An easy to use on-screen annotation software inspired by Epic Pen.](https://github.com/onyet/ppInk/)
* [**pyqtgraph**: Fast data visualization and GUI tools for scientific / engineering applications](https://github.com/pyqtgraph/pyqtgraph)
* [**Jamscreenshot**: 一个用python实现的类似微信QQ截屏的工具源码，整合提取自本人自制工具集Jamtools](https://github.com/fandesfyf/Jamscreenshot)
* [**EasyCanvas**: 基于Qt QGraphicsView的简易画图软件](https://github.com/douzhongqiang/EasyCanvas)
* [**PixPin**: 功能强大使用简单的截图/贴图工具，帮助你提高效率](https://pixpinapp.com/)

<details>
<summary>TodoList</summary>

## Fix abnormal behavior of system_hotkey
Testing shows it throws exceptions under Python 3.10, and even on Python 3.8 its exceptions can't be properly caught. Considering it hasn't been maintained for nearly 3 years, comprehensive compatibility handling is needed.

## ☐ Seamless hotkey configuration
## ☐ Seamless language switching
## ✔ Plugin marketplace
  - ✔ Add plugin system
  - ✔ Add plugin marketplace UI

## ✔ Faster offline OCR recognition support
## ❑ Improve UI display of OCR recognition layer
Currently using QWebEngineView to implement the OCR text layer, but this solution has high resource usage. Also, the text selection effect isn't ideal and needs further iteration.

### Optimization direction
  - ☐ Currently using QWebEngineView for OCR text layer. Could reference PDF4QT (PDFSelectTextTool class) to implement a lighter version.
    >Essentially need to rewrite PDFTextLayout and its supporting classes, which is non-trivial work.
    >PDFCharacterPointer.py PDFTextBlock.py PDFTextLayout.py PDFTextLine.py PDFTextSelection.py PDFTextSelectionColoredltem.py TextCharacter.py
    - https://github.com/openwebos/qt/blob/master/src/svg/qgraphicssvgitem.cpp
  - ✔ Build text labels based on recognized paragraphs. Current paragraph selection effect is poor.
    - https://github.com/hiroi-sora/GapTree_Sort_Algorithm

## ☐ Support image translation feature
Similar to Japanese manga translation effects: erase text on images and fill back with translated text. Consider providing this as a plugin.

#### References
 - https://ocr.wdku.net/index_pictranslation
 - https://www.basiccat.org/zh/imagetrans/
 - https://www.basiccat.org/zh/tagged/#imagetrans
 - https://www.appinn.com/cotrans-manga-image-translator-regular-edition/#google_vignette
 - https://github.com/KUR-creative/SickZil-Machine
 - https://www.bilibili.com/read/cv7181027/
 - https://github.com/zyddnys/manga-image-translator
 - https://github.com/jtl1207/comic-translation

## ☐ Add color presets
Add color preset functionality for tools like arrows and rectangles. Consider pressing Alt to directly pop up a floating wheel menu for quick selection of presets or custom colors.

## ☐ Refactor drawing tool module
Initial implementation had many hardcoded elements as functionality wasn't clear during development. Now that features are stable, we can reorganize this functionality, potentially splitting into DrawToolProvider, DrawToolSchduler, DrawToolFactory modules, or even extracting them as a plugin for more flexible and extensible drawing tool implementation.

After testing, another approach could be embedding web drawing apps like Excalidraw or TlDraw using WebEngineView controls in PinEditorWindow, then modifying the drawing layer background and disabling view zoom/scroll mechanisms, plus adding a demo mode for near-native experience - similar to how many web apps display echarts. Performance impact would be higher but feasible on modern machines.

https://tldraw.dev/examples/use-cases/image-annotator

Further, the drawing layer module could be repackaged as NativeDrawTool, TlDrawEmbedTool, ExcalidrawEmbedTool to save development effort.

Currently recommending TlDrawEmbedTool first as it supports media/GIF file insertion and preview display, offering more utility.

Considering OCR also uses WebEngineView for text selection layer, combining both approaches might be better and more convenient.

## ☐ Add node-based workflow customization
Allow users to customize quick workflows through node-based drag-and-drop, like certain automation tasks. Reference projects:
 - [pyqt-node-editor](https://gitlab.com/pavel.krupala/pyqt-node-editor)
 - [qtpynodeeditor](https://github.com/klauer/qtpynodeeditor)
 - [graphite (Node Graph Feauture)](https://editor.graphite.rs/)

## ✔ Compatibility with Linux Desktop systems like Ubuntu
Since Qt is cross-platform, it should theoretically support Linux Desktop, but requires adaptations like hotkey registration adjustments.

```sh
# Ubuntu doesn't install openssh-server by default, preventing Vscode Remote-SSH usage
# sudo apt-get install openssh-server

# Install Qt dependency libraries
sudo apt install libxcb-*

# Ubuntu needs xpyb - Python version of XCB
pip install xpybutil
```

```sh
# Package application
sudo apt install binutils
pip install pyinstaller
```

 - [Fix black screen when some software screenshots or remote controls on Linux](https://blog.csdn.net/u010912615/article/details/141295444)
   >Some Linux distros default to Wayland display protocol, resulting in black screenshots. Add `WaylandEnable=false` to `/etc/gdm3/custom.conf` under `[daemon]` section, then reboot.

</details>