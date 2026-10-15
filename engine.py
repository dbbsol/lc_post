"""Motor determinístico: tipografia com auto-ajuste, grid, 3 layouts, validação."""
import io
from pathlib import Path
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont
from config import FORMATS

FONTS = {"serif": ["georgiab.ttf", "DejaVuSerif-Bold.ttf"], "bold": ["arialbd.ttf", "DejaVuSans-Bold.ttf"],
         "reg": ["arial.ttf", "DejaVuSans.ttf"]}


FONT_DIR = Path(__file__).parent / "assets" / "fonts"  # coloque aqui as fontes do modelo (dbb_*.ttf)
FONTS.update({"t_serif": ["dbb_serif.ttf", "georgia.ttf", "DejaVuSerif.ttf"],
              "t_black": ["dbb_black.ttf", "ariblk.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"],
              "t_title": ["dbb_title.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"],
              "t_body": ["dbb_body.ttf", "arial.ttf", "DejaVuSans.ttf"]})


@lru_cache(None)
def font(k, s):
    for n in FONTS[k]:
        for p in (str(FONT_DIR / n), n):
            try:
                return ImageFont.truetype(p, s)
            except OSError:
                pass
    return ImageFont.load_default(s)


def wrap(d, t, f, w):
    L = []
    for para in t.split("\n"):
        cur = ""
        for wd in para.split():
            while d.textlength(wd, font=f) > w and len(wd) > 1:  # palavra maior que a caixa: quebra com hífen
                k = len(wd)
                while k > 1 and d.textlength(wd[:k] + "-", font=f) > w:
                    k -= 1
                if cur:
                    L.append(cur); cur = ""
                L.append(wd[:k] + "-"); wd = wd[k:]
            test = (cur + " " + wd).strip()
            if d.textlength(test, font=f) <= w or not cur:
                cur = test
            else:
                L.append(cur); cur = wd
        L.append(cur)
    return L


def put(c, t, kind, x, y, w, h, size, mn, fill, upper=False):
    """Mede, quebra, reduz a fonte até caber; se não couber, condensa e avisa."""
    if not t.strip():
        return y
    d = c["d"]; t = t.upper() if upper else t; s = float(size)
    while True:
        f = font(kind, int(s)); L = wrap(d, t, f, w); lh = int(s * 1.22)
        ok = len(L) * lh <= h and all(d.textlength(l, font=f) <= w for l in L)
        if ok or s <= mn:
            break
        s -= max(2, s * .06)
    if not ok:
        c["W"].append(f"Slide {c['i']+1}: texto condensado automaticamente (sugestão: encurtar o conteúdo).")
        L = L[:max(1, int(h // lh))]; L[-1] = L[-1].rstrip(" .,;") + "…"
    for k, l in enumerate(L):
        d.text((x, y + k * lh), l, font=f, fill=fill)
    return y + len(L) * lh


def cover(img, w, h):
    r = max(w / img.width, h / img.height)
    img = img.resize((int(img.width * r) + 1, int(img.height * r) + 1))
    l, t = (img.width - w) // 2, (img.height - h) // 2
    return img.crop((l, t, l + w, t + h))


def getimg(c, s):
    b = c["imgs"]
    return Image.open(io.BytesIO(b[s.image])).convert("RGB") if s.image is not None and 0 <= s.image < len(b) else None


def stack(c, s, x, y, cw, bottom, hk, hs, hc, upper=False):
    th, w = c["th"], c["w"]; g = int(w * .025)
    y = put(c, s.headline, hk, x, y, cw, (bottom - y) * .5, hs, int(w * .05), hc, upper) + g
    y = put(c, s.subhead, "bold" if upper else "reg", x, y, cw, (bottom - y) * .35, int(w * .04), int(w * .03), th["fg"]) + g
    y = put(c, s.body, "reg", x, y, cw, (bottom - y) * .8, int(w * .034), int(w * .026), th["fg"]) + g
    put(c, s.cta, "bold", x, y, cw, bottom - y, int(w * .035), int(w * .026), th["accent"])


def zones(c, s, tf, ff, y0):
    """Posiciona a imagem opcional (topo no vertical, rodapé nos demais) e devolve a área de texto."""
    w, h, m = c["w"], c["h"], c["m"]; bot = h - m - 50; im = getimg(c, s)
    if im is None:
        return y0, bot
    if c["tall"]:
        b = (m, y0, w - m, y0 + int(h * tf)); y, e = b[3] + 50, bot
    else:
        b = (m, bot - int(h * ff), w - m, bot); y, e = y0, b[1] - 40
    c["im"].paste(cover(im, b[2] - b[0], b[3] - b[1]), (b[0], b[1]))
    c["d"].rectangle(b, outline=c["th"]["accent"], width=4)
    return y, e


def editorial(c, s):
    d, w, m, th, top = c["d"], c["w"], c["m"], c["th"], c["m"] + c["top"]
    put(c, s.label, "bold", m, top, w * .5, 40, 26, 20, th["accent"], True)
    t = f"{c['i']+1:02d}/{c['n']:02d}"; d.text((w - m - d.textlength(t, font=font("reg", 26)), top), t, font=font("reg", 26), fill=th["muted"])
    d.line((m, top + 52, w - m, top + 52), fill=th["accent"], width=2)
    y, e = zones(c, s, .30, .27, top + 90)
    stack(c, s, m, y, w - 2 * m, e, "serif", int(w * .085), th["fg"])


def impact(c, s):
    d, w, m, th, top = c["d"], c["w"], c["m"], c["th"], c["m"] + c["top"]
    d.rectangle((m, top, m + 140, top + 18), fill=th["accent"])
    put(c, s.label, "bold", m + 170, top - 12, w * .4, 40, 26, 20, th["muted"], True)
    y, e = zones(c, s, .26, .24, top + 60)
    stack(c, s, m, y, w - 2 * m, e, "bold", int(w * .14), th["accent"], True)


def magazine(c, s):
    im, d, w, h, m, th, top = c["im"], c["d"], c["w"], c["h"], c["m"], c["th"], c["m"] + c["top"]
    pic = getimg(c, s)
    if pic is not None:
        im.paste(cover(pic, w, h))
    else:
        d.rectangle((0, 0, w, h), fill=th["primary"])
        d.text((m, top), f"{c['i']+1:02d}", font=font("serif", int(w * .5)), fill=th["accent"] if False else th["primary"])
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov); y0 = int(h * .30)
    rgb = tuple(int(th["bg"][i:i + 2], 16) for i in (1, 3, 5))
    for y in range(y0, h):
        od.line((0, y, w, y), fill=rgb + (int(240 * ((y - y0) / (h - y0)) ** 1.3),))
    im.paste(ov, (0, 0), ov)
    d.rectangle((0, 0, int(m * .45), h), fill=th["accent"])
    x = int(m * 1.6)
    chip = font("bold", 26); tw = d.textlength(s.label.upper(), font=chip)
    d.rectangle((x, top, x + tw + 40, top + 52), fill=th["accent"]); d.text((x + 20, top + 11), s.label.upper(), font=chip, fill=th["bg"])
    ys = int(h * (.52 if c["tall"] else .50))
    stack(c, s, x, ys, w - x - m, h - m - 50, "serif", int(w * .09), th["fg"])


LAYOUTS = {"Editorial": editorial, "Impacto": impact, "Magazine": magazine}


def render(slides, fmt, theme, layout, imgs=(), brand="", logo=None):
    F = FORMATS[fmt]; out, W = [], []
    for i, s in enumerate(slides):
        im = Image.new("RGB", (F["w"], F["h"]), theme["bg"])
        c = dict(im=im, d=ImageDraw.Draw(im), w=F["w"], h=F["h"], m=F["margin"], top=F["top"], th=theme, i=i,
                 n=len(slides), W=W, imgs=imgs, tall=F["h"] / F["w"] > 1.5)
        LAYOUTS[layout](c, s)
        if brand:
            c["d"].text((int(F["margin"] * 1.6) if layout == "Magazine" else F["margin"], F["h"] - F["margin"] + 8), brand,
                        font=font("reg", 26), fill=theme["muted"] if layout != "Magazine" else theme["fg"])
        if logo:
            lg = Image.open(io.BytesIO(logo)).convert("RGBA"); lg.thumbnail((200, 70))
            im.paste(lg, (F["w"] - F["margin"] - lg.width, F["h"] - F["margin"] - 10), lg)
        out.append(im)
    return out, validate_render(out, fmt, len(slides)) + W


def validate_render(ims, fmt, expected):
    F = FORMATS[fmt]; W = []
    if len(ims) != expected:
        W.append("Quantidade de páginas incorreta.")
    for i, im in enumerate(ims):
        if im.size != (F["w"], F["h"]):
            W.append(f"Slide {i+1}: dimensão incorreta.")
        if im.convert("L").getextrema()[0] == im.convert("L").getextrema()[1]:
            W.append(f"Slide {i+1}: página vazia.")
    return W
