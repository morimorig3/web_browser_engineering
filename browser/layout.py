import tkinter.font

from draw import DrawText, DrawRect
from html_parser import Element, Text

HSTEP, VSTEP = 13, 18 # 水平・垂直ステップ
BLOCK_ELEMENTS = [
    "html",
    "body",
    "article",
    "section",
    "nav",
    "aside",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hgroup",
    "header",
    "footer",
    "address",
    "p",
    "hr",
    "pre",
    "blockquote",
    "ol",
    "ul",
    "menu",
    "li",
    "dl",
    "dt",
    "dd",
    "figure",
    "figcaption",
    "main",
    "div",
    "table",
    "form",
    "fieldset",
    "legend",
    "details",
    "summary",
]

class BlockLayout:
    def __init__(self, node, parent, previous):
        self.node = node
        self.parent = parent # 親ポインタ
        self.previous = previous # 前の兄弟ポインタ
        self.children = [] # 子ポインタ
        self.display_list = []
        self.line = []

        self.x = None
        self.y = None
        self.width = None
        self.height = None
        self.cursor_x = 0
        self.cursor_y = 0

    def paint(self):
        cmds = []
        if self.layout_mode() == "inline":
            for x, y ,word, font, color in self.display_list:
                cmds.append(DrawText(x, y, word, font, color))

        # if isinstance(self.node, Element) and self.node.tag == "pre":
        #     x2, y2 = self.x + self.width, self.y + self.height
        #     rect = DrawRect(self.x, self.y, x2, y2, "gray")
        #     cmds.append(rect)

        bgcolor = self.node.style.get("background-color", "transparent")
        if bgcolor != "transparent":
            x2, y2 = self.x + self.width, self.y + self.height
            rect = DrawRect(self.x, self.y, x2, y2, bgcolor)
            cmds.append(rect)

        return cmds

    def layout_mode(self):
        if isinstance(self.node, Text):
            return "inline"
        elif any([isinstance(child, Element) and child.tag in BLOCK_ELEMENTS for child in self.node.children]):
            return "block"
        elif self.node.children:
            return "inline"
        else:
            return "block"

    def layout(self):
        # スタイルなしではx位置も横幅も親と同じ
        self.x = self.parent.x
        self.width = self.parent.width

        # 兄弟ブロック要素がある場合は兄弟分の高さを考慮
        if self.previous:
            self.y = self.previous.y + self.previous.height
        else:
            self.y = self.parent.y

        mode = self.layout_mode()
        if mode == "block":
            previous = None
            for child in self.node.children:
                next = BlockLayout(child, self, previous)
                self.children.append(next)
                previous = next
        else:
            self.height = self.cursor_y
            self.cursor_x = 0
            self.cursor_y = 0
            self.weight = "normal"
            self.style = "roman"
            self.size = 12

            self.recurse(self.node)
            self.flush()

        for child in self.children:
            child.layout()

        if mode == "block":
            self.height = sum([child.height for child in self.children])
        else:
            self.height = self.cursor_y

    def recurse(self, node):
        if isinstance(node, Text):
            for word in node.text.split():
                self.word(node, word)
        else:
            if node.tag == "br":
                self.flush()
            for child in node.children:
                self.recurse(child)

    def word(self, node, word):
        color = node.style["color"]
        weight = node.style["font-weight"]
        style = node.style["font-style"]
        # styleとsizeをTk用に変換
        if style == "normal": style = "roman"
        size = int(float(node.style["font-size"][:-2]) * .75)
        font = get_font(size, weight, style)
        w = font.measure(word) # 単語の横幅

        # 描画開始位置 + 文字幅 が単語の描画終了位置
        right_end = self.cursor_x + w

        # 画面幅を超える場合はフラッシュする
        if right_end > self.width:
            self.flush()

        self.line.append((self.cursor_x, word, font, color))
        self.cursor_x += w + font.measure(" ") # 文字

    def flush(self):
        if not self.line: return

        # 行内の最大アセントを計算
        max_ascent = max([font.metrics("ascent") for x, word, font, _ in self.line])
        baseline = self.cursor_y + 1.25 * max_ascent

        # 各単語をベースラインに沿って配置する
        for rel_x, word, font, color in self.line:
            x = self.x + rel_x
            y = self.y + baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font, color))

        # 行内の最大ディセントを計算して次行開始位置を調整
        metrics = [font.metrics() for x, word, font, _ in self.line]
        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent

        # カーソルリセットとバッファクリア
        self.cursor_x = 0
        self.line = []

FONTS = {}

def get_font(size, weight, style):
    key = (size, weight, style)
    if key not in FONTS:
        font = tkinter.font.Font(
            size=size,
            weight=weight,
            slant=style
        )
        label = tkinter.Label(font=font)
        FONTS[key] = (font, label)

    return FONTS[key][0]
