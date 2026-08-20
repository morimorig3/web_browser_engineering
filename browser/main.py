import socket
import ssl

class URL:
    # http://example.org
    def __init__(self, url):
        # "://"でschemeとurlを分割
        # 「http」「example.org」
        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https"]
        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443

        # example.org を example.org/に正規化する
        if "/" not in url:
            url = url + "/"
        # examole.org/ or examole.org/index.html
        self.host, url = url.split("/", 1)
        # パスはスラッシュ始まりにする
        self.path = "/" + url

        # カスタムポート対応
        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)

    def request(self):
        # ソケット作成
        # 接続先と繋げるトンネルを作る
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP
        )
        # 接続
        s.connect((self.host, self.port))

        # HTTPSの場合SSL/TLSでラップする
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        # リクエスト作成
        request = f"GET {self.path} HTTP/1.0\r\n"
        request += f"Host: {self.host}\r\n"
        request += "Connection: close\r\n"
        request += "User-Agent: tekitou_user_agent\r\n"
        request += "\r\n" # ヘッダー終了

        # 送信
        self.bytes = s.send(request.encode("utf8"))

        # 受信
        response = s.makefile("r", encoding="utf8", newline="\r\n")
        statusLine = response.readline()
        # HTTP1.0 200 OK
        version, status, explanation = statusLine.split(" ", 2)

        # ヘッダー辞書を作成するループ
        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n": break
            header, value = line.split(":", 1)
            key = header.casefold() # 小文字にする
            v = value.strip() # 前後空白除去
            response_headers[key] = v

        # Transfer-Encodingがないかチェック
        assert "transfer-encoding" not in response_headers
        # Content-Encodingがないかチェック
        assert "content-encoding" not in response_headers

        # 残りはボディ
        content = response.read()
        s.close()

        return content

import tkinter

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18 # 水平・垂直ステップ
SCROLL_STEP = 100

def layout(text):
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP
    for c in text:
        display_list.append((cursor_x, cursor_y, c))
        cursor_x += HSTEP
        if cursor_x >= WIDTH - HSTEP:
            cursor_y += VSTEP
            cursor_x = HSTEP
    return display_list


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

    def load(self, url):
        body = url.request()
        text = lex(body)
        self.display_list = layout(text)
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        for x, y, c in self.display_list:
            if y > self.scroll + HEIGHT: continue
            if y + VSTEP < self.scroll: continue

            self.canvas.create_text(x, y - self.scroll, text=c)

    def scrolldown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()

# def main():
#     u = URL(url="http://example.org")
#     body = u.request()
#     print(f"{u.scheme=} {u.host=} {u.path=} {u.port=} {u.bytes=}")
#     show(body)

def lex(body):
    text = ""
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            text += c
    return text

def show(body):
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            print(c, end="")

if __name__ == "__main__":
    import sys
    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()