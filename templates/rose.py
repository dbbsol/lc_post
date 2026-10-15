"""Rosé Gestão: bege + rosé, Bebas Neue + Poppins, lista com checks, botão e cartão final."""
from dsl import T, I, L, R, PL, BU
PAL = dict(bg="#F4E9E1", rose="#B8705F", brown="#6B4E43", sage="#A3A56A", card="#FBF4EE", line="#E0C7BA", white="#FFFFFF")
BR = lambda y: T(name="br", f="=brand", face="pop_m", size=24, min=18, color="brown", x=70, y=y, w=940, h=40, align="c", sp=2)
COVER = [("bg", "bg"),
         T(name="h", f="headline", face="bebas", size=170, min=90, color="rose", x=70, y=.07, w=800, h=.30, lh=1.0, upper=True),
         L(after="h", gap=34, x0=70, x1=330, color="rose", w=3),
         T(name="s", f="subhead", face="pop_r", size=36, min=24, color="brown", x=70, y="after:h+70", w=860, h=.10, lh=1.3),
         I(box=(70, .50, 940, .34), r=40, if_img=True), R(box=(70, .50, 940, .34), r=40, fill="card", outline="line", if_img=False),
         PL(f="cta", box=(70, .885, 940, 92), fill="rose", color="white"), BR(.965)]
TEXT = [("bg", "bg"),
        T(name="k", f="label", face="bebas", size=46, min=30, color="sage", x=70, y=.07, w=900, h=60, upper=True, sp=4, if_field="label"),
        T(name="h", f="headline", face="bebas", size=124, min=64, color="rose", x=70, y=.12, w=940, h=.22, lh=1.02, upper=True),
        BU(name="b", f="body", face="pop_m", size=38, min=26, color="brown", x=70, y="after:h+50", w=940, lim=.80, card="card", line="line", check="sage"),
        T(name="s", f="subhead", face="bebas", size=84, min=48, color="rose", x=70, y="after:b+40", w=940, lim=.93, upper=True, lh=1.05), BR(.965)]
END = [("bg", "bg"), R(box=(110, .16, 860, .62), r=60, fill="card", outline="line"),
       T(name="k", f="label", face="bebas", size=46, min=30, color="sage", x=110, y=.20, w=860, h=60, align="c", upper=True, sp=4),
       T(name="h", f="headline", face="bebas", size=150, min=80, color="rose", x=150, y=.25, w=780, h=.24, align="c", lh=1.0, upper=True, bal=True),
       T(name="s", f="subhead", face="pop_r", size=38, min=24, color="brown", x=150, y="after:h+30", w=780, h=.12, align="c", lh=1.3),
       PL(f="cta", box=(190, .70, 700, 100), fill="rose", color="white"), BR(.965)]
TEMPLATE = dict(name="Rosé Gestão", engine="dsl", pal=PAL, handle="@seunegocio",
                seq=lambda i, n: "cover" if i == 0 else ("end" if i == n - 1 and n > 2 else "text"),
                kinds=dict(cover=COVER, text=TEXT, end=END))
