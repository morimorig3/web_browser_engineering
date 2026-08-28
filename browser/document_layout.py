from layout import BlockLayout

HSTEP, VSTEP = 13, 18 # 水平・垂直ステップ
WIDTH, HEIGHT = 800, 600


class DocumentLayout:
    def __init__(self, node):
        self.node = node
        self.parent = None
        self.children = []

    def paint(self):
        return []

    def layout(self):
        child = BlockLayout(self.node, self, None)
        self.children.append(child)

        self.width = WIDTH - 2*HSTEP
        self.x = HSTEP
        self.y = VSTEP
        child.layout()
        self.display_list = child.display_list
        self.height = child.height