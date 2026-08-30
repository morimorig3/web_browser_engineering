from html_parser import Element


INHERITED_PROPERTIES = {
    "font-size": "16px",
    "font-style": "normal",
    "font-weight": "normal",
    "color": "black"
}

class CSSParser:
    def __init__(self, s):
        self.s = s # ex. "color: red;"
        self.i = 0

    def whitespace(self):
        # 空白の場合はインデックスをインクリメント
        while self.i < len(self.s) and self.s[self.i].isspace():
            self.i += 1

    def word(self):
        start = self.i
        # プロパティ名として許容されている文字ならインデックスをインクリメント
        while self.i < len(self.s):
            if self.s[self.i].isalnum() or self.s[self.i] in "#-.%":
                self.i += 1
            else:
                break

        # 1文字も進んでない場合はエラー
        if not (self.i > start):
            raise Exception("Parsing error")
        return self.s[start:self.i]

    def literal(self, literal):
        if not (self.i < len(self.s) and self.s[self.i] == literal):
            raise Exception("Parsing error")
        self.i += 1

    # ex. color: red;
    def pair(self):
        prop = self.word() # color まで読み進めて返す
        self.whitespace() # 空白があれば進める
        self.literal(":") # コロンがあれば進める
        self.whitespace() # 空白があれば進める
        val = self.word() # red まで読み進めて返す
        return prop.casefold(), val

    def body(self):
        pairs = {}
        while self.i < len(self.s) and self.s[self.i] != "}":
            try:
                prop, val = self.pair()
                pairs[prop.casefold()] = val
                self.whitespace()
                self.literal(";")
                self.whitespace()
            except Exception:
                # エラーの場合は捨てて次の開始までインデックスを進める
                why = self.ignore_until([";", "}"])
                if why == ";":
                    self.literal(";")
                    self.whitespace()
                else:
                    break
        return pairs

    # 指定の文字まで中身を捨てながらインデックスを進める
    def ignore_until(self, chars):
        while self.i < len(self.s):
            if self.s[self.i] in chars:
                return self.s[self.i]
            else:
                self.i += 1
        return None

    def selector(self):
        # 最初のセレクタを取得 ex. p
        out = TagSelector(self.word().casefold())
        # スペースを進める
        self.whitespace()
        # body開始タグまでループ
        while self.i < len(self.s) and self.s[self.i] != "{":
            # セレクタを読む span
            tag = self.word()
            descendant = TagSelector(tag.casefold())
            # p spanのような子孫セレクタにまとめる
            out = DescendantSelector(out, descendant)
            self.whitespace()
        return out

    def parse(self):
        rules = []
        while self.i < len(self.s):
            try:
                self.whitespace()
                selector = self.selector()
                self.literal("{")
                self.whitespace()
                body = self.body()
                self.literal("}")
                rules.append((selector, body))
            except Exception:
                why = self.ignore_until(["}"])
                if why == "}":
                    self.literal("}")
                    self.whitespace()
                else:
                    break

        return rules

def style(node, rules):
    node.style = {}

    # デフォルトスタイルを付与する
    for property, default_value in INHERITED_PROPERTIES.items():
        if node.parent:
            node.style[property] = node.parent.style[property]
        else:
            node.style[property] = default_value

    # CSSのセレクタにマッチするNodeにstyleを付与する
    for selector, body in rules:
        if not selector.matches(node): continue
        for property, value in body.items():
            node.style[property] = value

    if isinstance(node, Element) and "style" in node.attributes:
        pairs = CSSParser(node.attributes["style"]).body()
        for property, value in pairs.items():
            node.style[property] = value

    if node.style["font-size"].endswith("%"):
        if node.parent:
            parent_font_size = node.parent.style["font-size"]
        else:
            # html要素のとき
            parent_font_size = INHERITED_PROPERTIES["font-size"]
        node_pct = float(node.style["font-size"][:-1]) / 100
        parent_px = float(parent_font_size[:-2])
        node.style["font-size"] = str(node_pct * parent_px) + "px"

    for child in node.children:
        style(child, rules)

class TagSelector:
    def __init__(self, tag):
        self.tag = tag
        self.priority = 1

    # p { color: blue; }
    def matches(self, node):
        return isinstance(node, Element) and self.tag == node.tag

class DescendantSelector:
    def __init__(self, ancestor, descendant):
        self.ancestor = ancestor # 先祖
        self.descendant = descendant # 子孫
        self.priority = self.ancestor.priority + self.descendant.priority

    def matches(self, node):
        # p a { color: blue; }
        # 自分自身が子孫セレクタ（a）と一致するか
        if not self.descendant.matches(node): return False
        # 親を再起的にたどって親にpがあれば一致
        # p span a とかでも一致
        while node.parent:
            if self.ancestor.matches(node.parent): return True
            node = node.parent
        return False
