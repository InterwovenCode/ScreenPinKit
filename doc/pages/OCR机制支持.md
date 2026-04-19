- [PaddleOCR二次全流程——1. 确定字体_ocr常用中英文字体font-CSDN博客](https://blog.csdn.net/Castlehe/article/details/115399563)
- ### 实现思路
	- 用PaddleOCR、CnOCR来将文本识别出来，获得它的识别出来的文本框顶点坐标，然后每建立一个QGraphicsTextItem的时候，都针对这个Rect来测算它的合适字体，并且未选中的时候，让这个文本框是透明显示的，直到选中文本框才会显示出来
- ### 遗留问题
	- 目前还没有想到比较好的思路来实现一个类似微信图片OCR那样的文本选中功能，这块PixPin作者已经复刻过了
	- 一个开源方案 https://github.com/ocrmypdf/OCRmyPDF
		- [Windows下的安装教程](https://ocrmypdf.readthedocs.io/en/latest/installation.html#native-windows)
			- https://www.cnblogs.com/edisp/p/16667455.html
		- `ocrmypdf -l eng --rotate-pages --deskew --title "My PDF" --jobs 4 --output-type pdfa rotated_skew.pdf rotated_skew_ocr.pdf`
			- 用这个命令，可以为官方tests示例添加上文本操作层，效果正是我想要的，先记下来，以后工作之余去分析它
		- https://github.com/YaoXuanZhi/OCRmyPDF/tree/learn
			- 已经搭建好了分析OcrMyPdf的调试运行环境了，后面有时间再进一步去分析学习
		- 开源的Pdf查看器
			- https://github.com/turgu1/uPDF2
			- https://github.com/JakubMelka/PDF4QT
				- `Pdf4QtLibWidgets\sources\pdftexteditpseudowidget.cpp`
				- `uPDF2\src\pdfviewer.cpp`
				- 这个源文件包含了一个PDF文本选择功能
- ### 解决方案（已废弃）
	- ~~可以使用QWebEngineView来渲染PDF，现在浏览器内核都可以直接打开PDF文件了，但使用的是浏览器默认PDF样式，无法定制，而借助[PDF.js - Home](https://mozilla.github.io/pdf.js/)，则定制pdfViewer样式~~
	- 该方案已废弃：QWebEngineView 资源占用大，且文本选中效果不理想，现已整体移除，相关依赖 `pdf_viewer`、`pdfjs-3.4.120-legacy-dist`、`ocr_loader/html_builder.py` 均已删除

## 最终实现：基于 QGraphicsWidget 的可选中文本层

本方案的思路来自本地开源项目 `pyside6-ocr-text-selection`（PySide6 实现），
移植进本项目后位于 `src/ocr_text_selection/`（PyQt5 版本），用来替换原先基于 `QAutoSizeLineEdit` 的 `CanvasOcrTextItem` 文本层。

### 与旧实现的区别
| | 旧文本层 | 新文本层 |
| --- | --- | --- |
| 载体 | 每个文本框一个 `QGraphicsTextItem` + `QAutoSizeLineEdit` | 整页一个 `CanvasOcrTextLayerItem`（`QGraphicsWidget`） |
| 选中方式 | 逐个点选文本框 | 按住左键拖拽跨行、跨段选中 |
| 高亮 | 文本框控件自身外观 | `paint()` 里按行绘制半透明色块 |
| 命中测试 | 控件矩形 | `shape()` 只覆盖 OCR 文本框，其余区域鼠标穿透给绘图工具 |
| 导出 | 需要额外隐藏控件 | 生成图片前调用 `setOcrTextLayerVisible(False)` 即可 |

### 模块划分
- `model.py`：`Rect` / `OcrToken` / `OcrPage` 数据模型
- `page_builder.py`：把 OCR 加载器返回的 JSON（`{"data": [{"text", "box", "score"}]}`）转换成 `OcrPage`，
  坐标按 `dpiScale` 折算到场景坐标系，并沿用旧的 `drop_score = 0.5` 置信度过滤
- `layout/selection.py`：`OcrLayout` 负责阅读顺序、按行聚类、字符级命中测试与选中文本提取
- `layout/GapTree_Sort_Algorithm/`：内置的[间隙·树·排序算法](https://github.com/hiroi-sora/GapTree_Sort_Algorithm)，用于计算文本阅读顺序段落的划分
- `ui/canvas_item.py`：`CanvasOcrTextLayerItem`，即画布上真正使用的文本层图元
- `ui/svg_widget.py`：上游项目自带的 `SelectableSvgWidget` / `SelectableSvgWindow`，需要 `PyQt5.QtSvg`，因此延迟导入

### 交互约定
- 只有在「选择对象」工具下文本层才响应鼠标与键盘（`setSelectionEnabled`），其余绘图工具不受影响
- `shape()` 在文本层失效时返回空路径，从而让点击和悬停事件穿透到下方的绘图工具
- `Ctrl+C`、`Ctrl+A`、`Esc` 只在确实会改变选中状态时才拦截，
  否则把事件透传给外层窗口，保证「复制整张图片」「Esc 取消截图」等原有快捷键仍然有效
- 文本层 `zValue = -1`，位于截图背景之上、所有绘制图元之下

### 调用入口
`src/view/painter_interface.py` 中的 `buildOcrTextLayer()` / `clearOcrTextLayer()` /
`syncOcrTextLayerState()` / `setOcrTextLayerVisible()`，
由 `onOcrEndForReturnJson()` 在 OCR 完成后调用。相较旧实现，一次识别只创建一个图元，
不再为每段文字单独创建控件。