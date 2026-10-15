"""Legado Capital (consórcio): verde-oliva + dourado, Open Sans. Alterna fundo oliva/cinza nos slides de texto."""
from dsl import T, G, I, PH, L, A
PAL = dict(bg="#55672F", gold="#C9A227", gray="#E4E4E4", white="#FFFFFF", dark="#000000")


def txt(bg, title, body, kick):
    return [("bg", bg), I(box=(540, 0, 540, .28), if_img=True),
            T(name="k", f="label", face="os_b", size=34, min=24, color=kick, x=60, y=92, w=460, h=60, upper=True, if_field="label"),
            L(x0=40, y0=158, x1=470, y1=158, color="gold", w=3, if_field="label"),
            T(name="h", f="headline", face="os_b", size=84, min=48, color=title, x=60, y=(.33, .13), w=960, h=.34, lh=1.14, bal=True),
            T(name="b", f="body", face="os_r", size=46, min=30, color=body, x=60, y="after:h+46", w=960, lh=1.32),
            T(name="s", f="subhead", face="os_b", size=46, min=30, color=body, x=60, y="after:b+30", w=960, lh=1.32),
            A(cx=.5, y=.935, w=300, color="gold")]


COVER = [("bg", "bg"), PH(), G(c="dark", a0=0, a1=.8, y0=.3, y1=.88, if_img=True),
         T(name="br", f="=brand", face="os_b", size=26, min=20, color="gold", x=60, y=70, w=700, h=50, upper=True, sp=6),
         T(name="h", f="headline", face="chewy", size=108, min=60, color="gold", x=40, y=.50, w=1000, h=.22, align="c", lh=1.06, bal=True),
         T(name="s", f="subhead", face="os_b", size=38, min=26, color="white", x=40, y="after:h+22", w=1000, h=.07, align="c", upper=True, sp=5),
         T(name="k", f="highlight", face="pf_r", size=170, min=90, color="gold", x=40, y="after:s+8", w=1000, h=.18, align="c", upper=True, lh=1.0)]
END = [("bg", "bg"),
       T(name="h", f="headline", face="os_b", size=92, min=52, color="gold", x=60, y=.24, w=960, h=.26, align="c", lh=1.14, bal=True),
       T(name="b", f="body", face="os_r", size=46, min=30, color="white", x=60, y="after:h+40", w=960, h=.22, align="c", lh=1.32),
       T(name="c", f="cta", face="os_b", size=50, min=30, color="gold", x=60, y="after:b+34", w=960, h=.12, align="c", lh=1.2),
       T(name="br", f="=brand", face="os_b", size=26, min=20, color="gold", x=60, y=.93, w=960, h=50, align="c", upper=True, sp=6)]
TEMPLATE = dict(name="Legado Capital", engine="dsl", pal=PAL, handle="Legado Capital",
                seq=lambda i, n: "cover" if i == 0 else ("end" if i == n - 1 and n > 2 else ("a" if i % 2 else "b")),
                kinds=dict(cover=COVER, end=END, a=txt("bg", "gold", "white", "white"), b=txt("gray", "bg", "bg", "bg")))
