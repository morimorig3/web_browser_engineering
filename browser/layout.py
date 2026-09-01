from draw import DrawText, DrawRect, Rect
from html_parser import Element, Text
from helper import get_font

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
        self.line = []

        self.x = None
        self.y = None
        self.width = None
        self.height = None
        self.cursor_x = 0
        self.cursor_y = 0

    def self_rect(self):
        return Rect(self.x, self.y, self.x + self.width, self.y + self.height)

    def paint(self):
        cmds = []
        if isinstance(self.node, Element) and self.node.tag == "pre":
            x2, y2 = self.x + self.width, self.y + self.height
            rect = DrawRect(Rect(self.x, self.y, x2, y2), "gray")
            cmds.append(rect)

        bgcolor = self.node.style.get("background-color", "transparent")
        if bgcolor != "transparent":
            rect = DrawRect(self.self_rect(), bgcolor)
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
            self.new_line()
            self.recurse(self.node)

        for child in self.children:
            child.layout()

        self.height = sum([child.height for child in self.children])

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
            self.new_line()

        # self.line.append((self.cursor_x, word, font, color))

        line = self.children[-1]
        previous_word = line.children[-1] if line.children else None
        text = TextLayout(node, word, line, previous_word)
        line.children.append(text)

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

    def new_line(self):
        self.cursor_x = 0
        last_line = self.children[-1] if self.children else None
        new_line = LineLayout(self.node, self, last_line)
        self.children.append(new_line)

class LineLayout:
    def __init__(self, node, parent, previous):
        self.node = node
        self.parent = parent
        self.previous = previous
        self.children = []

    def layout(self):
        self.width = self.parent.width
        self.x = self.parent.x

        if self.previous:
            self.y = self.previous.y + self.previous.height
        else:
            self.y = self.parent.y

        for word in self.children:
            word.layout()

        if not self.children:
            self.height = 0
            return

        # 行内の最大アセントを計算
        max_ascent = max([word.font.metrics("ascent") for word in self.children])
        baseline = self.y + 1.25 * max_ascent

        # 各単語をベースラインに沿って配置する
        for word in self.children:
            word.y = baseline - word.font.metrics("ascent")

        # 行内の最大ディセントを計算して次行開始位置を調整
        max_descent = max([word.font.metrics("descent") for word in self.children])

        self.height = 1.25 * (max_ascent+ max_descent)

    def paint(self):
        return []

class TextLayout:
    def __init__(self, node, word, parent, previous):
        self.node = node
        self.word = word
        self.children = []
        self.parent = parent
        self.previous = previous

    def layout(self):
        weight = self.node.style["font-weight"]
        style = self.node.style["font-style"]
        if style == "normal": style = "roman"
        size = int(float(self.node.style["font-size"][:-2]) * .75)
        self.font = get_font(size, weight, style)

        self.width = self.font.measure(self.word)
        if self.previous:
            space = self.previous.font.measure(" ")
            self.x = self.previous.x + space + self.previous.width
        else:
            self.x = self.parent.x

        self.height = self.font.metrics("linespace")

    def paint(self):
        color = self.node.style["color"]
        return [DrawText(
            self.x,
            self.y,
            self.word,
            self.font,
            color
        )]