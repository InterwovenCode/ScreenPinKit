<p align="center">
  <img width="18%" align="center" src="https://raw.githubusercontent.com/YaoXuanZhi/ScreenPinKit/main/images/logo.svg" alt="logo">
</p>
  <h1 align="center">
  ScreenPinKit
</h1>
<p align="center">
  一款基于PyQt5的迷你截图标注、桌面标注工具
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
<a href="./README.md">English</a> | 简体中文
</p>

![Interface](https://raw.githubusercontent.com/YaoXuanZhi/ScreenPinKit/main/images/Interface.png)

![OCR](https://raw.githubusercontent.com/YaoXuanZhi/ScreenPinKit/main/images/ocr.png)

## 安装
```shell
# 暂时只推荐在Python3.8、Python3.9上安装
## 源码安装
#cd src/
#python setup.py install
# pip安装
pip install ScreenPinKit -i https://pypi.org/simple/

ScreenPinKit
```

> **Warning**
> 该应用使用了第三方库system_hotkey来注册全局快捷键，但是由于该包已经有3年以上不维护了，推荐在python3.8上安装并运行

## 开发
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

### 运行示例
使用 pip 安装好 ScreenPinKit 包并下载好此仓库的代码之后，就可以运行 src 目录下的任意示例程序，比如：

```sh
cd src
python main.py

python ./canvas_editor/demos/canvas_editor_demo_full.py

python ./canvas_item/demos/canvas_arrow_demo.py

```

## 打包分发
```sh
# Windows Defender可能会报毒，忽略即可打包出来
cd src
# 显式打包OCR环境，需要在ocr_loader_manager.py里显式导入相关依赖模块
pyinstaller --icon=../images/logo.png --add-data "internal_deps:internal_deps" --windowed main.py -n ScreenPinKit

# 隐式包含内置OCR环境
# pyinstaller --onefile --hidden-import=cv2 --hidden-import=onnxruntime --hidden-import=pyclipper --hidden-import=shapely --icon=../images/logo.png --add-data "internal_deps:internal_deps" --windowed main.py -n ScreenPinKit
```

## 代码检查&格式化
```sh
#利用ruff包对源码做语法检测和代码自动格式化
pip install ruff

# 作为 linter 运行
ruff check

# 作为格式化程序运行
ruff format
```

## 使用教程
| 作用域 | 快捷键 | 作用 |
|-------|-------|-------|
| 全局 | F7 | 截图 |
| 全局 | F4 | 呼出屏幕标注 |
| 全局 | F2 | 在鼠标位置上显示剪贴板上的图像 |
| 全局 | Esc | 逐步退出该窗口的编辑状态 |
| 截图窗口 | Ctrl+T | 将截图选区转换为屏幕贴图 |
| 截图窗口 | Shift | 切换放大镜上的颜色格式(rgb/hex) |
| 截图窗口 | C | 复制当前拾取到的颜色格式 |
| 贴图窗口 | Ctrl+A | OCR识别 |
| 贴图窗口 | Alt+F | 切换鼠标穿透状态 |
| 贴图窗口 | Ctrl+C | 复制当前贴图到剪贴板上 |
| 贴图窗口 | Ctrl+S | 将当前贴图保存到磁盘上 |
| 贴图窗口 | Ctrl+W | 完成绘图 |
| 贴图窗口 | Ctrl+Z | 撤销 |
| 贴图窗口 | Ctrl+Y | 重做 |
| 贴图窗口 | 3次Space | 清除绘图 |
| 屏幕标注窗口 | Alt+L | 隐藏/显示屏幕标注内容 |
| 屏幕标注窗口 | Ctrl+W | 完成绘图 |

请仔细阅读 [wiki](https://github.com/YaoXuanZhi/ScreenPinKit/wiki)

## 参考
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

## 修复system_hotkey的异常表现
经测试，在python3.10下会抛异常，并且在python3.8上其异常也不能被正常捕获，考虑到它已经有将近3年不维护了，需要做对它做全方位的兼容性处理

## ☐ 无感设置快捷键
## ☐ 无感切换语言
## ✔ 插件市场
  - ✔ 添加插件系统
  - ✔ 添加插件市场UI

## ✔ 更快的离线OCR识别支持
## ❑ 完善OCR识别层的UI显示
目前已采用QWebEngineView来实现了OCR文本层，但该方案资源占用较大，另外文本层选择的效果也不够理想，还需要继续迭代

### 优化方向
  - ☐ 目前采用了QWebEngineView来实现了OCR文本层，可以参考PDF4QT(PDFSelectTextTool类)来实现一个更轻量级的版本 
    >基本上要将PDFTextLayout及其配套的类都重写一遍，工作量并不小
    >PDFCharacterPointer.py PDFTextBlock.py PDFTextLayout.py PDFTextLine.py PDFTextSelection.py PDFTextSelectionColoredltem.py TextCharacter.py
    - https://github.com/openwebos/qt/blob/master/src/svg/qgraphicssvgitem.cpp
  - ✔ 根据文本识别段落来构筑各个文本标签，目前段落选择效果不佳
    - https://github.com/hiroi-sora/GapTree_Sort_Algorithm

## ☐ 支持图片翻译功能
类似日漫汉化之类的效果，将图片上的文本涂抹掉，然后填充回翻译后的文本，考虑下以插件形式提供该功能

#### 参考资料
 - https://ocr.wdku.net/index_pictranslation
 - https://www.basiccat.org/zh/imagetrans/
 - https://www.basiccat.org/zh/tagged/#imagetrans
 - https://www.appinn.com/cotrans-manga-image-translator-regular-edition/#google_vignette
 - https://github.com/KUR-creative/SickZil-Machine
 - https://www.bilibili.com/read/cv7181027/
 - https://github.com/zyddnys/manga-image-translator
 - https://github.com/jtl1207/comic-translation

## ☐ 增加配色预设
让箭头、矩形等工具增加配色预设功能，考虑按下Alt键，直接弹出一个浮动轮盘菜单，用来让用户快捷选择预设或者自定义颜色

## ☐ 重构绘图工具模块
由于当初实现的时候，很多绘图工具功能并没有明晰，都是摸索着实现的，所以存在很多硬编码的情况，现在功能基本已稳定，可以重新梳理该功能的行为，计划将拆分为DrawToolProvider、DrawToolSchduler、DrawToolFactory等模块，甚至将它们提炼为一个插件，让绘图工具的实现更灵活，更易扩展

经过测试，其实还可以换一种思路，那就是将Excalidraw、TlDraw之类的web绘图应用使用WebEngineView控件来嵌入到PinEditorWindow上，然后修改绘图层的背景以及取消视图缩放和滚动机制，
，再追加一个演示模式，那就同原生的体验差不多了，同很多web显示echarts思路差不多，不过性能上损耗会有点大，但是考虑到目前主流机器都还是比较不错的，这个方案理论上也可以落地

https://tldraw.dev/examples/use-cases/image-annotator

更进一步，也可以将绘图层模块重新封装成NativeDrawTool、TlDrawEmbedTool、ExcalidrawEmbedTool，可以节省很多开发工作

当下本人比较建议先接入TlDrawEmbedTool，因为它还支持媒体、gif等格式的媒体文件插入并且预览显示，更有妙用

其实考虑到OCR识别之后，也是采用WebEngineView作为文本选择层，那么将它们两者结合起来也不失为一个更好的方案，起码省事多了

## ☐ 增加节点式流程定制化支持
可以让用户通过节点式拖曳定制一些快捷流程，比如某些自动化任务啥的，具体可以参考以下项目
 - [pyqt-node-editor](https://gitlab.com/pavel.krupala/pyqt-node-editor)
 - [qtpynodeeditor](https://github.com/klauer/qtpynodeeditor)
 - [graphite (Node Graph Feauture)](https://editor.graphite.rs/)

## ✔ 兼容Linux Desktop系统，比如Ubuntu
由于采用了Qt，它是一个跨平台的GUI，因此理论上是可以兼容Linux Desktop的，但需要做以下适配，比如热键注册之类需要调整

```sh
# Ubuntu默认没有安装openssh-server，这会导致Vscode Remote-SSH无法使用，需要手动安装
# sudo apt-get install openssh-server

# 安装Qt依赖库
sudo apt install libxcb-*

# Ubuntu需要xpyb - XCB 的 Python 版本
pip install xpybutil
```

```sh
# 打包应用
sudo apt install binutils
pip install pyinstaller
```

 - [解决部分软件在 Linux 下截屏黑屏，远程控制黑屏的问题](https://blog.csdn.net/u010912615/article/details/141295444)
   >某些Linux发行版默认使用Waylan显示协议，截屏时屏幕是黑的，只能截取到纯黑的图像，使用`/etc/gdm3/custom.conf`文件，在`[daemon]`段中添加`WaylandEnable=false`即可，重启电脑即可生效

</details>