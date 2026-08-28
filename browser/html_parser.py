class Text:
    def __init__(self, text, parent):
        self.text = text
        self.children = []
        self.parent = parent

    def __repr__(self):
        return repr(self.text)

class Element:
    def __init__(self, tag, attribute, parent):
        self.tag = tag
        self.children = []
        self.attribute = attribute
        self.parent = parent

    def __repr__(self):
        return "<" + self.tag + ">"

SELF_CLOSING_TAGS = [
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr"
]

class HTMLParser:
    def __init__(self, body):
        self.body = body
        self.unfinished = []
        self.HEAD_TAGS = [
            "base", "basefont", "bgsound", "noscript",
            "link", "meta", "title", "style", "script"
        ]

    def implicit_tags(self, tag):
        while True:
            open_tags = [node.tag for node in self.unfinished]

            if open_tags == [] and tag != "html":
                self.add_tag("html")
            elif open_tags == ["html"] and tag != "html" and tag not in ["head", "body", "/html"]:
                if tag in self.HEAD_TAGS:
                    self.add_tag("head")
                else:
                    self.add_tag("body")
            elif open_tags == ["html", "head"] and tag not in ["/head"] + self.HEAD_TAGS:
                self.add_tag("/head")
            else:
                break

    def get_attribute(self, text):
        parts = text.split()
        tag = parts[0].casefold()
        attribute = {}
        for attrpair in parts[1:]:
            # href="htt..."
            if "=" in attrpair:
                key, value = attrpair.split("=", 1)
                attribute[key.casefold()] = value
                # 引用符かっこっている場合 引用符を取り除く
                if len(value) > 2 and value[0] in ["'", "\""]:
                    value = value[1:-1]
            # <input disabled>
            else:
                attribute[attrpair.casefold()] = ""

        return tag, attribute

    def add_text(self, text):
        # 空白のみのテキストを破棄
        if text.isspace(): return
        self.implicit_tags(None)

        # 最後の未完成ノードの子要素にするだけ
        parent = self.unfinished[-1]
        node = Text(text, parent)
        parent.children.append(node)

    def add_tag(self, tag):
        tag, attribute = self.get_attribute(tag)
        # DOCTYPE・コメントは破棄
        if tag.startswith("!"): return
        self.implicit_tags(tag)

        # 終了タグ
        if tag.startswith("/"):
            if len(self.unfinished) == 1: return
            # 先っちょの未完成ノードを閉じる
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        # 自己終了タグ
        elif tag in SELF_CLOSING_TAGS:
            parent = self.unfinished[-1]
            node = Element(tag, attribute, parent)
            parent.children.append(node)
        # 開始タグ
        else:
            # リストの最後に未完成ノードを追加
            parent = self.unfinished[-1] if self.unfinished else None # 最初の開始タグは親がない
            node = Element(tag, attribute, parent)
            self.unfinished.append(node)

    def finish(self):
        # 空文字列でもhtml/head/bodyは出力する
        if not self.unfinished:
            self.implicit_tags(None)

        while len(self.unfinished) > 1:
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        return self.unfinished.pop()


# '<!DOCTYPE html>\n<html lang="ja">\n<body>\n    <h1>Hello, World!</h1>\n
# <p>This is <b>bold tag!</b>.</p>\n    <p>But, This is <i>italic tag!</i>.</p>\n</body>\n</html>'
    def parse(self):
        text = ""
        in_tag = False
        for c in self.body:
            # 開始タグ
            if c == "<":
                in_tag = True

                if text: self.add_text(text)
                text = ""
            # 終了タグ
            elif c == ">":
                in_tag = False

                # p>
                self.add_tag(text)
                text = ""
            else:
                text += c

        if not in_tag and text:
            self.add_text(text)

        return self.finish()

def print_tree(node, indent=0):
    print(" " * indent, node)
    for child in node.children:
        print_tree(child, indent + 2)