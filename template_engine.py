"""Motor de modelos: capa (título duplo), texto justificado, slide final de marca.
Posições em frações da página, então recompõe sozinho em 4:5, 1:1 e 9:16."""
from PIL import Image, ImageDraw
from engine import font, wrap, validate_render
from config import FORMATS


def tw(d, t, f, sp):
    return sum(d.textlength(c, font=f) for c in t) + sp * max(len(t) - 1, 0)


def tdraw(d, t, f, cx, y, fill, sp):
    x = cx - tw(d, t, f, sp) / 2
    for ch in t:
        d.text((x, y), ch, font=f, fill=fill, anchor="ls"); x += d.textlength(ch, font=f) + sp


def twrap(d, t, f, sp, w):
    L, cur = [], ""
    for wd in t.split():
        test = (cur + " " + wd).strip()
        if tw(d, test, f, sp) <= w or not cur:
            cur = test
        else:
            L.append(cur); cur = wd
    return L + [cur]


def fit(c, t, kind, w, h, size, mn, lhk=1.3):
    d, s = c["d"], float(size)
    while True:
        f = font(kind, int(s)); L = wrap(d, t, f, w); lh = int(s * lhk)
        ok = len(L) * lh <= h and all(d.textlength(l, font=f) <= w for l in L)
        if ok or s <= mn:
            break
        s -= max(2, s * .05)
    if not ok:
        c["W"].append(f"Slide {c['i']+1}: texto condensado automaticamente (sugestão: encurtar o conteúdo).")
        L = L[:max(1, int(h // lh))]; L[-1] = L[-1].rstrip(" .,;") + "…"
    return L, f, lh


def arrow(d, cx, y, w, col):
    x0, x1 = cx - w / 2, cx + w / 2
    d.line((x0, y, x1, y), fill=col, width=3)
    d.line((x1 - 14, y - 9, x1, y), fill=col, width=3); d.line((x1 - 14, y + 9, x1, y), fill=col, width=3)


def handle(c, y):
    d, w, th = c["d"], c["w"], c["th"]
    tdraw(d, c["handle"], font("t_body", int(.021 * w)), w / 2, y, th["fg"], .011 * w)


def text_slide(c, s, last):
    d, w, h, th = c["d"], c["w"], c["h"], c["th"]
    handle(c, int(.053 * h))
    mx = int((.088 if last else .102) * w); cw = int((.917 if last else .949) * w) - mx
    y = int((.205 if last else .148) * h)
    if s.headline:
        L, f, lh = fit(c, s.headline, "t_title", cw, int(.2 * h), .056 * w, .036 * w)
        for l in L:
            x = mx + (cw - d.textlength(l, font=f)) / 2 if last else mx
            d.text((x, y), l, font=f, fill=th["fg"]); y += lh
        y += int(.012 * h)
    body = " ".join(filter(None, [s.subhead, s.body, s.cta]))
    if body:
        L, f, lh = fit(c, body, "t_body", cw, int(.87 * h) - y, .058 * w, .032 * w, 1.32)
        for k, l in enumerate(L):
            ws = l.split(); gap = (cw - sum(d.textlength(t, font=f) for t in ws)) / max(len(ws) - 1, 1)
            if k == len(L) - 1 or len(ws) == 1 or gap > f.size * 1.3:
                d.text((mx, y), l, font=f, fill=th["fg"])
            else:
                x = mx
                for t in ws:
                    d.text((x, y), t, font=f, fill=th["fg"]); x += d.textlength(t, font=f) + gap
            y += lh
    if not last:
        arrow(d, w / 2, int(.92 * h), .163 * w, th["fg"])


def cover(c, s):
    d, w, h, th = c["d"], c["w"], c["h"], c["th"]
    handle(c, int(.285 * h))
    words = (s.headline or s.body).split()
    k = 0 if len(words) <= 1 else (1 if len(words) == 2 else (len(words) + 1) // 2)
    top, bot = " ".join(words[:k]).upper(), " ".join(words[k:])
    sb = .14 * w
    while tw(d, bot, font("t_black", int(sb)), 0) > .86 * w and sb > .05 * w: sb -= 3
    sb = int(sb); yb = int(.57 * h) if top else int(.53 * h)
    if top:
        st = .19 * w
        while tw(d, top, font("t_serif", int(st)), 0) > .84 * w and st > .06 * w: st -= 3
        yt = yb - int(.88 * sb)
        tdraw(d, top, font("t_serif", int(st)), w / 2, yt, th["fg"], 0)
    tdraw(d, bot, font("t_black", sb), w / 2, yb, th["fg"], 0)
    sub = (s.subhead or "").upper()
    if sub:
        f = font("t_body", int(.0215 * w)); sp = .0115 * w
        L = twrap(d, sub, f, sp, .8 * w)[:4]; y = int(.635 * h)
        for l in L:
            tdraw(d, l, f, w / 2, y, th["fg"], sp); y += int(f.size * 1.5)
    arrow(d, w / 2, int(.92 * h), .163 * w, th["fg"])


def brand_slide(c):
    d, w, h, th = c["d"], c["w"], c["h"], c["th"]
    f = font("t_black", int(.218 * w)); gap = int(.03 * w)
    ls = th["logo"]; ws = [d.textlength(ch, font=f) for ch in ls]
    gl = (w - (sum(ws) + gap * 2)) / 2 + .02 * w; x = gl; yb = int(.495 * h)
    for ch, wd, col in zip(ls, ws, th["logo_colors"]):
        d.text((x, yb), ch, font=f, fill=col, anchor="ls"); x += wd + gap
    L = int(.32 * w)
    d.line((gl - .062 * w, int(.33 * h), gl - .062 * w + L, int(.33 * h)), fill=th["fg"], width=4)
    d.line((gl + .221 * w, int(.536 * h), gl + .221 * w + L, int(.536 * h)), fill=th["fg"], width=4)
    tf = font("t_body", int(.021 * w))
    d.text((w / 2 + .01 * w, int(.572 * h)), th["tagline"], font=tf, fill=th["muted"], anchor="ms")


def render_tpl(slides, fmt, tpl, brand="", brand_page=False):
    F = FORMATS[fmt]; w, h = F["w"], F["h"]; out, W = [], []
    kinds = [("cover" if i == 0 and len(slides) >= 2 else "text") for i in range(len(slides))]
    items = list(zip(slides, kinds)) + ([(None, "brand")] if brand_page else [])
    for i, (s, kind) in enumerate(items):
        im = Image.new("RGB", (w, h), tpl["bg"])
        c = dict(d=ImageDraw.Draw(im), w=w, h=h, W=W, i=i, th=tpl, handle=(brand or tpl["handle"]).upper())
        if kind == "cover": cover(c, s)
        elif kind == "brand": brand_slide(c)
        else: text_slide(c, s, last=(i == len(slides) - 1 and len(slides) > 1))
        out.append(im)
    return out, validate_render(out, fmt, len(out)) + W
