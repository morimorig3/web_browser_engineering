import tkinter
from layout import Layout
from html_parser import HTMLParser, print_tree

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
        self.nodes = HTMLParser(body).parse()
        # print_tree(self.nodes)
        self.display_list = Layout(self.nodes).display_list
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
