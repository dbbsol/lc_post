"""Motor de modelos (DSL): tipografia por métricas reais, balanceamento de linhas, quebra de palavras
gigantes, fluxo vertical (sem sobreposição) e validação de limites/colisões."""
import re
from functools import lru_cache
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from config import FORMATS
from engine import font as sysfont, validate_render, cover

FD = Path(__file__).parent / "assets" / "fonts"
FACES = {"os_b": ("OpenSans-VF.ttf", [700, 100]), "os_r": ("OpenSans-VF.ttf", [400, 100]),
         "pf_r": ("PlayfairDisplay-VF.ttf", [400]), "pf_b": ("PlayfairDisplay-VF.ttf", [700]),
         "pf_i": ("PlayfairDisplay-Italic-VF.ttf", [600]), "pop_r": ("Poppins-Regular.ttf", None),
         "pop_m": ("Poppins-Medium.ttf", None), "pop_s": ("Poppins-SemiBold.ttf", None),
         "chewy": ("Fredoka-VF.ttf", [700, 100]), "bebas": ("BebasNeue-Regular.ttf", None)}


def T(**k): return ("text", k)
def G(**k): return ("grad", k)
def I(**k): return ("img", k)
def PH(**k): return ("photo", k)
def L(**k): return ("line", k)
def A(**k): return ("arrow", k)
def R(**k): return ("rrect", k)
def PL(**k): return ("pill", k)
def BU(**k): return ("bullets", k)


@lru_cache(None)
def face(k, s):
    n, ax = FACES[k]; p = FD / n
    if p.exists():
        f = ImageFont.truetype(str(p), max(int(s), 8))
        if ax:
            try: f.set_variation_by_axes(ax)
            except Exception: pass
        return f
    return sysfont("t_title" if k in ("os_b", "pf_b", "pop_s", "chewy", "bebas") else "t_body", max(int(s), 8))


def tl(d, t, f, sp=0): return d.textlength(t, font=f) + sp * max(len(t) - 1, 0)


def wrap2(d, t, f, w, sp=0):
    out = []
    for para in t.split("\n"):
        cur = ""
        for wd in para.split():
            while tl(d, wd, f, sp) > w and len(wd) > 1:      # palavra maior que a caixa: quebra com hífen
                k = len(wd)
                while k > 1 and tl(d, wd[:k] + "-", f, sp) > w: k -= 1
                if cur: out.append(cur); cur = ""
                out.append(wd[:k] + "-"); wd = wd[k:]
            t2 = (cur + " " + wd).strip()
            if tl(d, t2, f, sp) <= w or not cur: cur = t2
            else: out.append(cur); cur = wd
        out.append(cur)
    return out


def balance(d, t, f, w, sp, n):
    """Mesmo nº de linhas, mas com larguras equilibradas (sem última linha órfã)."""
    lo, hi = w * .45, w
    for _ in range(14):
        m = (lo + hi) / 2
        if len(wrap2(d, t, f, m, sp)) <= n: hi = m
        else: lo = m
    return wrap2(d, t, f, hi, sp)


def fit(d, t, k, size, mn, w, h, lh, sp, bal, W, tag):
    s = float(size)
    while True:
        f = face(k, int(s)); Ls = wrap2(d, t, f, w, sp)
        if bal and len(Ls) > 1: Ls = balance(d, t, f, w, sp, len(Ls))
        a, dc = f.getmetrics(); lp = int(s * lh); H = a + dc + (len(Ls) - 1) * lp
        if H <= h or s <= mn: break
        s -= max(1.5, s * .04)
    if H > h:
        Ls = Ls[:max(1, int((h - a - dc) // lp) + 1)]; Ls[-1] = Ls[-1].rstrip(" .,;:-") + "…"
        H = a + dc + (len(Ls) - 1) * lp; W.append(f"{tag}: texto condensado automaticamente (sugestão: encurtar o conteúdo).")
    return Ls, f, lp, a, H


def P(c, v, ax):
    if isinstance(v, float) and abs(v) <= 1.0: return v * (c["W"] if ax == "x" else c["H"])
    return v * c["u"]


def Y(c, y):
    if isinstance(y, tuple): y = y[0] if c["img"] is not None else y[1]
    if isinstance(y, str):
        n, g = y[6:].split("+"); return c["bot"].get(n, 0) + float(g) * c["u"]
    return P(c, y, "y")


def col(c, v): return c["pal"].get(v, v)


def field(c, f):
    if f == "=brand": return c["brand"]
    if f.startswith("="): return f[1:]
    t = (getattr(c["s"], f, "") or "").strip()
    return "" if f == "label" and t.isdigit() else t


def ok(c, e):
    if "if_img" in e and (c["img"] is not None) != e["if_img"]: return False
    return not ("if_field" in e and not field(c, e["if_field"]))


def e_text(c, e):
    d, u = c["d"], c["u"]; t = field(c, e["f"]); t = t.upper() if e.get("upper") else t; y = Y(c, e["y"])
    if not t: c["bot"][e["name"]] = y; return
    x, w = P(c, e["x"], "x"), P(c, e["w"], "x"); lim = P(c, e.get("lim", .9), "y")
    h = P(c, e["h"], "y") if "h" in e else max(lim - y, 40 * u); sp = e.get("sp", 0) * u; al = e.get("align", "l")
    Ls, f, lp, a, H = fit(d, t, e["face"], e["size"] * u, e["min"] * u, w, h, e.get("lh", 1.2), sp, e.get("bal", False), c["Wn"], f"Slide {c['i']+1}")
    for k, l in enumerate(Ls):
        lw = tl(d, l, f, sp); xx = x if al == "l" else (x + (w - lw) / 2 if al == "c" else x + w - lw); by = y + a + k * lp
        if sp:
            for ch in l: d.text((xx, by), ch, font=f, fill=col(c, e["color"]), anchor="ls"); xx += d.textlength(ch, font=f) + sp
        else: d.text((xx, by), l, font=f, fill=col(c, e["color"]), anchor="ls")
    mw = max(tl(d, l, f, sp) for l in Ls); x0 = x if al == "l" else (x + (w - mw) / 2 if al == "c" else x + w - mw)
    c["bot"][e["name"]] = y + H; c["boxes"].append((x0, y, x0 + mw, y + H, e["name"]))


def e_bullets(c, e):
    d, u = c["d"], c["u"]; t = field(c, e["f"]); y = Y(c, e["y"])
    items = [i.strip() for i in re.split(r"(?<=[.;!?])\s+|\n", t) if i.strip()][:6]
    if not items: c["bot"][e["name"]] = y; return
    x, w = P(c, e["x"], "x"), P(c, e["w"], "x"); lim = P(c, e.get("lim", .9), "y")
    pad, ind, gap = int(36 * u), int(76 * u), int(24 * u); s = e["size"] * u
    while True:
        f = face(e["face"], int(s)); rows = [wrap2(d, i, f, w - 2 * pad - ind) for i in items]; a, dc = f.getmetrics(); lp = int(s * 1.28)
        hh = sum(a + dc + (len(r) - 1) * lp for r in rows) + gap * (len(rows) - 1) + 2 * pad
        if y + hh <= lim or s <= e["min"] * u: break
        s -= max(1.5, s * .04)
    if y + hh > lim: c["Wn"].append(f"Slide {c['i']+1}: lista longa demais (sugestão: menos itens).")
    d.rounded_rectangle((x, y, x + w, y + hh), int(36 * u), fill=col(c, e["card"]), outline=col(c, e["line"]), width=2)
    cy = y + pad; rad = s * .5
    for r in rows:
        cx, cm = x + pad + rad, cy + a - s * .33
        d.ellipse((cx - rad, cm - rad, cx + rad, cm + rad), fill=col(c, e["check"]))
        d.line([(cx - rad * .45, cm), (cx - rad * .1, cm + rad * .4), (cx + rad * .5, cm - rad * .35)], fill="#FFFFFF", width=max(3, int(u * 4)), joint="curve")
        for k, l in enumerate(r): d.text((x + pad + ind, cy + a + k * lp), l, font=f, fill=col(c, e["color"]), anchor="ls")
        cy += a + dc + (len(r) - 1) * lp + gap
    c["bot"][e["name"]] = y + hh; c["boxes"].append((x, y, x + w, y + hh, e["name"]))


def box(c, b): return [int(P(c, b[0], "x")), int(P(c, b[1], "y")), int(P(c, b[2], "x")), int(P(c, b[3], "y"))]


def e_img(c, e):
    if c["img"] is None: return
    x, y, w, h = box(c, e["box"]); pic = cover(c["img"], w, h); r = int(e.get("r", 0) * c["u"])
    if r:
        m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w, h), r, fill=255); c["im"].paste(pic, (x, y), m)
    else: c["im"].paste(pic, (x, y))


def e_photo(c, e):
    if c["img"] is not None: c["im"].paste(cover(c["img"], c["W"], c["H"]), (0, 0))


def e_grad(c, e):
    W, H = c["W"], c["H"]; h = col(c, e["c"]).lstrip("#"); rgb = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov); hz = e.get("dir", "v") == "h"; n = W if hz else H
    y0, y1 = e.get("y0", 0) * n, e.get("y1", 1) * n
    for p in range(n):
        t = min(1, max(0, (p - y0) / max(y1 - y0, 1))); al = int(255 * (e["a0"] + (e["a1"] - e["a0"]) * t ** e.get("pw", 1)))
        od.line((p, 0, p, H) if hz else (0, p, W, p), fill=rgb + (al,))
    c["im"].paste(ov, (0, 0), ov)


def e_line(c, e):
    y = Y(c, f"after:{e['after']}+{e['gap']}") if "after" in e else P(c, e["y0"], "y")
    c["d"].line((P(c, e["x0"], "x"), y, P(c, e["x1"], "x"), y), fill=col(c, e["color"]), width=max(2, int(e.get("w", 3) * c["u"])))


def e_arrow(c, e):
    u = c["u"]; cx, y, w = P(c, e["cx"], "x"), P(c, e["y"], "y"), e["w"] * u; k = col(c, e["color"]); t = max(3, int(4 * u))
    c["d"].line((cx - w / 2, y, cx + w / 2, y), fill=k, width=t)
    for s in (-1, 1): c["d"].line((cx + w / 2 - 20 * u, y + s * 12 * u, cx + w / 2, y), fill=k, width=t)


def e_rrect(c, e):
    x, y, w, h = box(c, e["box"]); c["d"].rounded_rectangle((x, y, x + w, y + h), int(e.get("r", 0) * c["u"]),
                                                            fill=col(c, e["fill"]) if e.get("fill") else None,
                                                            outline=col(c, e["outline"]) if e.get("outline") else None, width=2)


def e_pill(c, e):
    t = field(c, e["f"]).upper()
    if not t: return
    d, u = c["d"], c["u"]; x, y, w, h = box(c, e["box"]); d.rounded_rectangle((x, y, x + w, y + h), h // 2, fill=col(c, e["fill"]))
    s = h * .36
    while tl(d, t, face("pop_s", int(s))) > w - 56 * u and s > 12: s -= 2
    d.text((x + w / 2, y + h / 2), t, font=face("pop_s", int(s)), fill=col(c, e["color"]), anchor="mm")


EL = dict(text=e_text, bullets=e_bullets, img=e_img, photo=e_photo, grad=e_grad, line=e_line, arrow=e_arrow, rrect=e_rrect, pill=e_pill)


def render_dsl(slides, fmt, tpl, brand="", imgs=()):
    F = FORMATS[fmt]; Wd, H = F["w"], F["h"]; out, Wn = [], []; n = len(slides)
    for i, s in enumerate(slides):
        pic = None
        if s.image is not None and 0 <= s.image < len(imgs):
            import io; pic = Image.open(io.BytesIO(imgs[s.image])).convert("RGB")
        im = Image.new("RGB", (Wd, H), tpl["pal"]["bg"])
        c = dict(im=im, d=ImageDraw.Draw(im), W=Wd, H=H, u=Wd / 1080, bot={}, boxes=[], s=s, img=pic, pal=tpl["pal"],
                 brand=(brand or tpl["handle"]), Wn=Wn, i=i)
        for t, e in tpl["kinds"][tpl["seq"](i, n)]:
            if t == "bg": im.paste(Image.new("RGB", (Wd, H), col(c, e)))
            elif ok(c, e): EL[t](c, e)
        B = c["boxes"]
        for a in range(len(B)):
            if B[a][0] < -2 or B[a][2] > Wd + 2 or B[a][3] > H + 2: Wn.append(f"Slide {i+1}: '{B[a][4]}' fora da página.")
            for b in range(a + 1, len(B)):
                p, q = B[a], B[b]
                if p[0] < q[2] - 2 and q[0] < p[2] - 2 and p[1] < q[3] - 2 and q[1] < p[3] - 2:
                    Wn.append(f"Slide {i+1}: possível sobreposição entre '{p[4]}' e '{q[4]}'.")
        out.append(im)
    return out, validate_render(out, fmt, n) + Wn
