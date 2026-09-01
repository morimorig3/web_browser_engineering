from helper import get_font
from draw import DrawOutline, DrawText, DrawLine, DrawRect, Rect
from url import URL


WIDTH, HEIGHT = 800, 600

class Chrome:
    def __init__(self, browser):
        self.browser = browser
        self.font = get_font(20, "normal", "roman")
        self.font_height = self.font.metrics("linespace")
        self.padding = 5
        self.tabbar_top = 0
        self.tabbar_bottom = self.font_height + 2*self.padding
        self.urlbar_top = self.tabbar_bottom
        self.urlbar_bottom = self.urlbar_top + self.font_height + 2*self.padding
        self.bottom = self.urlbar_bottom
        back_width = self.font.measure("<") + 2*self.padding
        self.back_rect = Rect(
            self.padding,
            self.urlbar_top + self.padding,
            self.padding + back_width,
            self.urlbar_bottom - self.padding
        )

        self.address_rect = Rect(
            self.back_rect.top + self.padding,
            self.urlbar_top + self.padding,
            WIDTH - self.padding,
            self.urlbar_bottom - self.padding
        )

        plus_width = self.font.measure("+") + 2*self.padding
        self.newtab_rect = Rect(
            self.padding, # left
            self.padding, # top
            self.padding + plus_width, # right
            self.padding + self.font_height # bottom
        )
        self.focus = None
        self.address_bar = ""

    def click(self, x, y):
        self.focus = None
        if self.newtab_rect.containsPoint(x, y):
            self.browser.new_tab(URL("https://browser.engineering/"))
        elif self.back_rect.containsPoint(x, y):
            self.browser.active_tab.go_back()
        elif self.address_rect.containsPoint(x, y):
            self.focus = "address bar"
            self.address_bar = ""
        else:
            for i , tab in enumerate(self.browser.tabs):
                if self.tab_rect(i).containsPoint(x, y):
                    self.browser.active_tab = tab
                    break

    def tab_rect(self, i):
        tabs_start = self.newtab_rect.right + self.padding
        tab_width = self.font.measure("Tab X") + 2*self.padding
        return Rect(
            tabs_start + tab_width * i, # left
            self.tabbar_top, # top
            tabs_start + tab_width * (i + 1), # right
            self.tabbar_bottom # bottom
        )

    def keypress(self, char):
        if self.focus == "address bar":
            self.address_bar += char

    def backspace(self):
        if self.focus == "address bar":
            self.address_bar = self.address_bar[:-1]

    def enter(self):
        if self.focus == "address bar":
            self.browser.active_tab.load(URL(self.address_bar))
            self.focus = None


    def paint(self):
        cmds = []

        # Chrome背景の描画
        cmds.append(DrawRect(
            Rect(0, 0, WIDTH, self.bottom),
            "white"
        ))
        cmds.append(DrawLine(
            0, self.bottom, WIDTH, self.bottom, "black", 1
        ))

        # + ボタンの描画
        cmds.append(DrawOutline(self.newtab_rect, "black", 1))
        cmds.append(DrawText(
            self.newtab_rect.left + self.padding,
            self.newtab_rect.top,
            "+",
            self.font,
            "black"
        ))

         # Tabの描画
        for i, tab in enumerate(self.browser.tabs):
            bounds = self.tab_rect(i)
            cmds.append(DrawLine(
                bounds.left,
                0,
                bounds.left,
                bounds.bottom,
                "black",
                1
            ))
            cmds.append(DrawLine(
                bounds.right,
                0,
                bounds.right,
                bounds.bottom,
                "black",
                1
            ))
            cmds.append(DrawText(
                bounds.left + self.padding,
                bounds.top + self.padding,
                f"Tab {i}",
                self.font,
                "black"
            ))
            if tab == self.browser.active_tab:
                cmds.append(DrawLine(
                    0,
                    bounds.bottom,
                    bounds.left,
                    bounds.bottom,
                    "black",
                    1
                ))
                cmds.append(DrawLine(
                    bounds.right,
                    bounds.bottom,
                    WIDTH,
                    bounds.bottom,
                    "black",
                    1
                ))

        # 戻るボタン
        cmds.append(DrawOutline(self.back_rect, "black", 1))
        cmds.append(DrawText(
            self.back_rect.left + self.padding,
            self.back_rect.top,
            "<",
            self.font,
            "black"
        ))

        # アドレスバーの描画
        cmds.append(DrawOutline(self.address_rect, "black", 1))
        url = str(self.browser.active_tab.url)
        if self.focus == "address bar":
            cmds.append(DrawText(
                self.address_rect.left + self.padding,
                self.address_rect.top,
                self.address_bar,
                self.font,
                "black"
            ))
            w = self.font.measure(self.address_bar)
            cmds.append(DrawLine(
                self.address_rect.left + self.padding + w,
                self.address_rect.top,
                self.address_rect.left + self.padding + w,
                self.address_rect.bottom,
                "red",
                1
            ))
        else:
            cmds.append(DrawText(
                self.address_rect.left + self.padding,
                self.address_rect.top,
                url,
                self.font,
                "black"
            ))

        return cmds