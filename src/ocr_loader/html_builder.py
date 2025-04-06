import html
from PIL import ImageFont

IsSupportGapTree = True

try:
    from .GapTree_Sort_Algorithm.preprocessing import linePreprocessing
    from .GapTree_Sort_Algorithm.gap_tree import GapTree
    IsSupportGapTree = True
except ImportError:
    IsSupportGapTree = False

def calculate_best_font_size(
    text, font_path, max_width, max_height, initial_font_size=5
):
    """
    通过ImageFont计算最适合固定文本框的字体大小
    :param text: 要显示的文本
    :param font_path: 字体文件路径
    :param max_width: 文本框的最大宽度
    :param max_height: 文本框的最大高度
    :param initial_font_size: 初始字体大小
    :return: 最适合的字体大小
    """

    font_size = initial_font_size

    while True:
        font = ImageFont.truetype(font_path, font_size)
        text_width, text_height = font.getsize(text)

        if text_width <= max_width and text_height <= max_height:
            font_size += 1
        else:
            break

    return font_size


def calculate_best_font_size_by_qpainter(
    text, font_family, max_width, max_height, initial_font_size=5
):
    """
    通过QPainter计算最适合固定文本框的字体大小
    :param text: 要显示的文本
    :param font_path: 字体文件路径
    :param max_width: 文本框的最大宽度
    :param max_height: 文本框的最大高度
    :param initial_font_size: 初始字体大小
    :return: 最适合的字体大小
    @Note
        获得的字体偏小，不建议采用
    """
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QImage, QPainter, QFont

    image = QImage(1, 1, QImage.Format_ARGB32)

    painter = QPainter(image)

    font_size = initial_font_size
    font = QFont(font_family, font_size)

    while True:
        font.setPointSize(font_size)
        painter.setFont(font)

        # 获取文本的边界矩形
        rect = painter.boundingRect(image.rect(), Qt.AlignLeft, text)
        text_width = rect.width()
        text_height = rect.height()

        if text_width <= max_width and text_height <= max_height:
            font_size += 1
        else:
            break
    painter.end()
    return font_size


def build_svg_html(font_path, width, height, box_infos, dpi_scale=1):
    """将图片进行OCR识别后，将结果转换成html"""
    # box_info = {"box":[x, y, w, h], "text":text}

    width = width / dpi_scale
    height = height / dpi_scale

    # 构建 HTML 内容
    html_content = f"""
    <html>
    <head>
        <title>OCR Result</title>
        <style>
            body {{
                background-color: transparent;
                margin: 0;
                padding: 0;
                box-sizing: border-box; /* 确保内边距和边框不会增加元素的宽度 */
            }} 

            /*
            ::selection{{
                background-color: transparent;
            }}
            */

            .ocr_image {{
                position: relative;
                width: {width}px;
                height: {height}px;
            }}
        </style>

        <script src="qrc:/qtwebchannel/qwebchannel.js"></script>
        <script>
            // 屏蔽右键菜单
            document.addEventListener('contextmenu', function(event) {{
                event.preventDefault();
            }});

            // 监听 keydown 事件
            document.addEventListener('keydown', function(event) {{
                if (event.ctrlKey && event.key === 'c') {{
                    //由于WebEngineView的复制结果并不符合预期，因此屏蔽掉再额外做处理
                    event.preventDefault();
                    // 透传网页的复制事件
                    window.receiver.hookCopyText(window.getSelection().toString());
                }}

                if (event.key === 'Escape') {{
                    event.preventDefault();
                    window.receiver.hookEscPressed(window.getSelection().toString().length > 0);
                }}
            }});

            // 初始化QWebChannel
            new QWebChannel(qt.webChannelTransport, function(channel) {{
                window.receiver = channel.objects.receiver;
                window.receiver.htmlRenderFinished(document.documentElement.scrollWidth, document.documentElement.scrollHeight);
            }});
        </script>
    </head>
    <body class="ocr_image">
       <svg width="100%" height="100%" viewBox="0 0 {width} {height}" preserveAspectRatio="xMaxYMax slice" xmlns="http://www.w3.org/2000/svg">
    """

    # 遍历 OCR 结果，生成 HTML 文本层
    for info in box_infos:
        text = info["text"]
        box = info["box"]
        [left_top, right_top, right_bottom, left_bottom] = box

        x, y = left_top
        w = right_top[0] - left_top[0]
        h = left_bottom[-1] - left_top[-1]

        x = x / dpi_scale
        y = y / dpi_scale
        w = w / dpi_scale
        h = h / dpi_scale
        text = html.escape(text)

        best_font_size = calculate_best_font_size(text, font_path, w, h, 2)

        # # 调试专用
        # html_content += f"""
        # <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="gray"/>
        # <text x="{x}" y="{y+h}" width="{w}" height="{h}" font-family="Arial" font-size="{best_font_size}" fill="blue" textLength="{w}" lengthAdjust="spacingAndGlyphs">
        #     {text}
        # </text>
        # """

        # # 正式版
        # html_content += f"""
        # <text x="{x}" y="{y+h}" width="{w}" height="{h}" font-family="Arial" font-size="{best_font_size}" fill="none" textLength="{w}" lengthAdjust="spacingAndGlyphs">
        #     {text}
        # </text>
        # """

        # 正式版
        html_content += f"""
        <text x="{x}" y="{y+h/2}" width="{w}" height="{h}" text-anchor="start" dominant-baseline="middle" font-family="Arial" font-size="{best_font_size}" fill="none" textLength="{w}" lengthAdjust="spacingAndGlyphs">
            {text}
        </text>
        """

    html_content += """
        </svg>
    </body>
    </html>
    """

    return html_content


def build_origin_html(width, height, box_infos, dpi_scale=1):
    """将图片进行OCR识别后，将结果转换成html"""
    # box_info = {"box":[x, y, w, h], "text":text}

    width = width / dpi_scale
    height = height / dpi_scale

    # 构建 HTML 内容
    html_content = f"""
    <html>
    <head>
        <title>OCR Result</title>
        <style>

            /* 禁止所有元素被选择 */
            * {{
                -webkit-user-select: none; /* 适用于WebKit浏览器（如Chrome、Safari） */
                -moz-user-select: none; /* 适用于Firefox */
                -ms-user-select: none; /* 适用于IE10+ */
                user-select: none; /* 标准属性 */
            }}

            /* 允许文本被选择 */
            p, span, div {{
                -webkit-user-select: text; /* 适用于WebKit浏览器（如Chrome、Safari） */
                -moz-user-select: text; /* 适用于Firefox */
                -ms-user-select: text; /* 适用于IE10+ */
                user-select: text; /* 标准属性 */
            }}

            body {{
                background-color: transparent;
                margin: 0;
                padding: 0;
                box-sizing: border-box; /* 确保内边距和边框不会增加元素的宽度 */
            }} 

            ::selection{{
                background-color: transparent;
            }}

            .ocr_image {{
                position: relative;
                width: {width}px;
                height: {height}px;
            }}

            img {{
                width: 100%;
                height: 100%;
                pointer-events: none; /* 禁止鼠标事件 */
                opacity: 0
            }}

            .container {{
                position: absolute;
                white-space: pre;
                /* border: 1px solid gray; */
                background-color: transparent;
                display: flex;
                align-items: center;
                justify-content: center;
                overflow: hidden; /* 防止内容溢出 */
            }}

            .text {{
                font-family: Arial, sans-serif;
                font-size: 5px; /* 初始字体大小 */
                line-height: 1.2; /* 初始行高 */
                display: inline-block;
                /* color: red; */
                color: transparent;
                max-width: 100%;
                max-height: 100%;
                overflow: hidden;
                /* text-overflow: ellipsis; */
                white-space: nowrap; /* 防止文本换行 */
                text-align: justify;
            }}

            .text::selection {{
                color: transparent;
                background-color: rgba(64, 128, 191, 0.5);
            }}

            /* 使用媒体查询或JavaScript动态调整字体大小和行距 */
            @media (max-width: 400px) {{
                .text {{
                    font-size: 14px;
                    line-height: 1.1;
                }}
            }}

            @media (max-width: 300px) {{
                .text {{
                    font-size: 12px;
                    line-height: 1.0;
                }}
            }}

            /* 隐藏所有滚动条 */
            :root {{
            overflow: hidden;
            /* background-color: orange; */
            background-color: transparent;
            }}
        </style>

        <script src="qrc:/qtwebchannel/qwebchannel.js"></script>
        <script>
            // 屏蔽右键菜单
            document.addEventListener('contextmenu', function(event) {{
                event.preventDefault();
            }});

            // 监听 keydown 事件
            document.addEventListener('keydown', function(event) {{
                if (event.ctrlKey && event.key === 'c') {{
                    //由于WebEngineView的复制结果并不符合预期，因此屏蔽掉再额外做处理
                    event.preventDefault();
                    // 透传网页的复制事件
                    window.receiver.hookCopyText(window.getSelection().toString());
                }}

                if (event.key === 'Escape') {{
                    event.preventDefault();
                    window.receiver.hookEscPressed(window.getSelection().toString().length > 0);
                }}
            }});

            // 初始化QWebChannel
            new QWebChannel(qt.webChannelTransport, function(channel) {{
                window.receiver = channel.objects.receiver;
                window.receiver.htmlRenderFinished(document.documentElement.scrollWidth, document.documentElement.scrollHeight);
            }});
        </script>

        <script>
                function adjustFontSize() {{
                    // 获取所有具有特定类名的元素
                    const elements = document.querySelectorAll('.container');

                    // 遍历所有元素
                    elements.forEach((element, index) => {{
                        const container = element;
                        const text = container.querySelector('.text');
                        const containerWidth = container.clientWidth;
                        const containerHeight = container.clientHeight;

                        let fontSize = 2; // 初始字体大小
                        let lineHeight = 1.2; // 初始行高

                        // 调整字体大小，直到文本适应容器
                        while (text.scrollWidth <= containerWidth && text.scrollHeight <= containerHeight) {{
                            fontSize += 0.5;
                            text.style.fontSize = fontSize + 'px';
                            text.style.lineHeight = lineHeight;
                        }}

                        let textWidth = text.scrollWidth
                        if (textWidth < containerWidth) {{
                            // 计算需要的字符间距
                            const excessWidth = containerWidth - textWidth;
                            const numChars = text.textContent.length;
                            const letterSpacing = excessWidth / numChars;

                            // 设置字符间距
                            text.style.letterSpacing = `${{letterSpacing}}px`;
                        }} else {{
                            // 如果文本宽度小于或等于容器宽度，移除字符间距
                            text.style.letterSpacing = '0px';
                        }}
                    }});
                }}

            // 页面加载时调整字体大小
            window.addEventListener('load', adjustFontSize);

            // 窗口大小改变时重新调整字体大小
            window.addEventListener('resize', adjustFontSize);
        </script>
    </head>
    <body class="ocr_image">
    """

    # 遍历 OCR 结果，生成 HTML 文本层
    for info in box_infos:
        text = info["text"]
        box = info["box"]
        [left_top, right_top, right_bottom, left_bottom] = box

        x, y = left_top
        w = right_top[0] - left_top[0]
        h = left_bottom[-1] - left_top[-1]

        x = x / dpi_scale
        y = y / dpi_scale
        w = w / dpi_scale
        h = h / dpi_scale
        text = html.escape(text)

        html_content += f"""
        <div class="container" style="left: {x}px; top: {y}px; width: {w}px; height: {h}px;">
            <span class="text">{text}</span>
        </div>
        """

    html_content += """
    </body>
    </html>
    """

    return html_content


def build_svg_content(font_path, width, height, box_infos, dpi_scale=1):
    # 构建 HTML 内容
    svg_content = f"""
<svg width="100%" height="100%" viewBox="0 0 {width} {height}" preserveAspectRatio="xMaxYMax slice" xmlns="http://www.w3.org/2000/svg">
    """

    # 遍历 OCR 结果，生成 HTML 文本层
    for info in box_infos:
        text = info["text"]
        box = info["box"]
        [left_top, right_top, right_bottom, left_bottom] = box

        x, y = left_top
        w = right_top[0] - left_top[0]
        h = left_bottom[-1] - left_top[-1]

        x = x / dpi_scale
        y = y / dpi_scale
        w = w / dpi_scale
        h = h / dpi_scale
        text = html.escape(text)

        best_font_size = calculate_best_font_size(text, font_path, w, h, 2)

        svg_content += f"""
    <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="gray"/>
    <text x="{x}" y="{y+h}" width="{w}" height="{h}" font-family="Arial" font-size="{best_font_size}" fill="blue" textLength="{w}" lengthAdjust="spacingAndGlyphs">
        {text}
    </text>
        """

    svg_content += """
</svg>
    """
    return svg_content


def handle_gap_tree_sort_for_box_infos(box_infos):
    """
    进行版面分析，将各个boxInfo进行重新排序
    提取自https://github.com/hiroi-sora/GapTree_Sort_Algorithm/blob/main/test.py
    """
    bboxes = linePreprocessing(box_infos)

    for i, tb in enumerate(box_infos):
        tb["bbox"] = bboxes[i]  # 写入标准化的bbox

    gtree = GapTree(lambda tb: tb["bbox"])
    sortedBoxInfos = gtree.sort(box_infos)  # 输入文本块，获得排序后结果
    return sortedBoxInfos


def build_svg_html_by_gap_tree_sort(font_path, width, height, box_infos, dpi_scale=1):
    if IsSupportGapTree == True:
        sorted_box_infos = handle_gap_tree_sort_for_box_infos(box_infos)
    else:
        sorted_box_infos = box_infos
    return build_svg_html(
        font_path=font_path,
        width=width,
        height=height,
        box_infos=sorted_box_infos,
        dpi_scale=dpi_scale,
    )


def build_origin_html_by_gap_tree_sort(width, height, box_infos, dpi_scale=1):
    if IsSupportGapTree == True:
        sorted_box_infos = handle_gap_tree_sort_for_box_infos(box_infos)
    else:
        sorted_box_infos = box_infos
    return build_origin_html(
        width=width, height=height, box_infos=sorted_box_infos, dpi_scale=dpi_scale
    )
