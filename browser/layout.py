import tkinter.font

HSTEP, VSTEP = 13, 18 # 水平・垂直ステップ
WIDTH, HEIGHT = 800, 600

class Layout:
    def __init__(self, tokens):
        self.display_list = []
        self.line = []
        self.cursor_x = HSTEP
        self.cursor_y = VSTEP
        self.weight = "normal"
        self.style = "roman"
        self.size = 16

        for tok in tokens:
            self.token(tok)

        self.flush()

    def token(self, tok):
        if isinstance(tok, Text):
            for word in tok.text.split():
                self.word(word)
        elif tok.tag == "i":
            self.style = "italic"
        elif tok.tag == "/i":
            self.style = "roman"
        elif tok.tag == "b":
            self.weight = "bold"
        elif tok.tag == "/b":
            self.weight = "normal"
        elif tok.tag == "big":
            self.size += 4
        elif tok.tag == "/big":
            self.size -= 4
        elif tok.tag == "small":
            self.size -= 2
        elif tok.tag == "/small":
            self.size += 2
        elif tok.tag == "br":
            self.flush()
        elif tok.tag == "/p":
            self.flush()
            self.cursor_y += VSTEP
        elif tok.tag == "/h1":
            self.flush()
            self.cursor_y += VSTEP

    def word(self, word):
        font = get_font(self.size, self.weight, self.style)
        w = font.measure(word) # 単語の横幅

        # 描画開始位置 + 文字幅 が単語の描画終了位置
        right_end = self.cursor_x + w
        screen_size = WIDTH - HSTEP

        # 画面幅を超える場合はフラッシュする
        if right_end > screen_size:
            self.flush()

        self.line.append((self.cursor_x, word, font))
        self.cursor_x += w + font.measure(" ") # 文字

    def flush(self):
        if not self.line: return

        # 行内の最大アセントを計算
        max_ascent = max([font.metrics("ascent") for x, word, font in self.line])
        baseline = self.cursor_y + 1.25 * max_ascent

        # 各単語をベースラインに沿って配置する
        for x, word, font in self.line:
            y = baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font))

        # 行内の最大ディセントを計算して次行開始位置を調整
        metrics = [font.metrics() for x, word, font in self.line]
        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent

        # カーソルリセットとバッファクリア
        self.cursor_x = HSTEP
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


class Text:
    def __init__(self, text):
        self.text = text

class Tag:
    def __init__(self, tag):
        self.tag = tag
