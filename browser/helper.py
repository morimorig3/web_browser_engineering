import tkinter.font

FONTS = {}

def get_font(size, weight, style):
    key = (size, weight, style)
    if key not in FONTS:
        font = tkinter.font.Font(
            size=size,
            weight=weight,
            slant=style if style in ("roman", "italic") else "roman"
        )
        label = tkinter.Label(font=font)
        FONTS[key] = (font, label)

    return FONTS[key][0]