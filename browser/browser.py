import tkinter
from layout import Layout, Text, Tag

SCROLL_STEP = 100
WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18 # 水平・垂直ステップ

class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT
        )
        self.canvas.pack()
        self.scroll = 0

        # 下矢印キーをスクロール関数にバインド
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)

    def load(self, url):
        body = url.request()
        tokens = lex(body)
        self.display_list = Layout(tokens).display_list
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        for x, y, c, f in self.display_list:
            if y > self.scroll + HEIGHT: continue
            if y + VSTEP < self.scroll: continue

            self.canvas.create_text(x, y - self.scroll, text=c, anchor='nw', font=f)

    def scrolldown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()

    def scrollup(self, e):
        self.scroll -= SCROLL_STEP
        self.draw()

# '<!DOCTYPE html>\n<html lang="ja">\n<body>\n    <h1>Hello, World!</h1>\n
# <p>This is <b>bold tag!</b>.</p>\n    <p>But, This is <i>italic tag!</i>.</p>\n</body>\n</html>'

# パース
def lex(body):
    out = []
    buffer = "" # テキスト タグ内容を一時保存するバッファ
    in_tag = False
    for c in body:
        # 開始タグ
        if c == "<":
            in_tag = True

            # バッファにテキストがあればテキストオブジェクトにして保存してリセット
            # ex. This is <i>it..
            if buffer: out.append(Text(buffer))
            buffer = ""
        # 終了タグ
        elif c == ">":
            in_tag = False

            # p>
            out.append(Tag(buffer))
            buffer = ""
        else:
            buffer += c

    if not in_tag and buffer:
        out.append(Text(buffer))

    return out