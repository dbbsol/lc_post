"""Glau Personal: foto + degradê magenta, Playfair Display + Poppins."""
from dsl import T, G, PH
PAL = dict(bg="#9B1B5A", mag="#B3125F", white="#FFFFFF")
HD = lambda y, al, x, w: T(name="hd", f="=brand", face="pop_s", size=26, min=20, color="white", x=x, y=y, w=w, h=60, align=al, upper=True, sp=5)


def cover(yh):
    return [("bg", "bg"), PH(), G(c="mag", a0=0, a1=.94, y0=.45, y1=.8, if_img=True), G(c="mag", a0=0, a1=.85, if_img=False),
            T(name="h", f="headline", face="pf_r", size=74, min=44, color="white", x=70, y=yh, w=940, h=.15, align="c", upper=True, lh=1.1, bal=True),
            T(name="s", f="subhead", face="pop_r", size=34, min=22, color="white", x=70, y="after:h+22", w=940, h=.08, align="c", upper=True, sp=3),
            T(name="c", f="cta", face="pop_m", size=30, min=20, color="white", x=70, y="after:s+30", w=940, h=.06, align="c", upper=True, sp=3),
            HD(.935, "c", 70, 940)]


TEXT = [("bg", "bg"), PH(), G(c="mag", a0=0, a1=.88, dir="h", y0=.12, y1=.85, if_img=True), G(c="mag", a0=0, a1=.9, if_img=False),
        HD(62, "r", 380, 620),
        T(name="h", f="headline", face="pf_i", size=60, min=40, color="white", x=300, y=.19, w=700, h=.13, align="r", lh=1.12, bal=True),
        T(name="b", f="body", face="pf_r", size=44, min=30, color="white", x=260, y="after:h+18", w=740, align="r", lh=1.3),
        T(name="s", f="subhead", face="pf_i", size=44, min=30, color="white", x=260, y="after:b+26", w=740, align="r", lh=1.3)]
TEMPLATE = dict(name="Glau Personal", engine="dsl", pal=PAL, handle="@PERSONALGLAU",
                seq=lambda i, n: "cover" if i == 0 else ("end" if i == n - 1 and n > 2 else "text"),
                kinds=dict(cover=cover(.70), end=cover(.58), text=TEXT))
