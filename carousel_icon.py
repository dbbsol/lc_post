"""Indicador de carrossel: pontos de paginação + seta (quando há próximo slide).
Canto inferior direito, cor automática por contraste com o fundo. Funciona em qualquer modelo/layout."""
from PIL import Image, ImageDraw, ImageStat

S = 4


def add_indicator(im, i, n):
    """Desenha o indicador no slide i (de n). Em post único (n < 2) não faz nada."""
    if n < 2:
        return im
    W, H = im.size; u = W / 1080
    dd, gap, aw, ag, cw, pad = 14 * u, 12 * u, 38 * u, 22 * u, 16 * u, 22 * u
    ws = [aw if j == i else dd for j in range(n)]
    arrow = i < n - 1
    dots_w = sum(ws) + gap * (n - 1)
    w, h = dots_w + 2 * pad + ((ag + cw) if arrow else 0), 52 * u
    x = W - .06 * W - w
    yc = (.905 if H / W > 1.5 else .958) * H          # em 9:16 sobe para fugir da interface do Instagram
    x, y = int(max(x, 0)), int(min(max(yc - h / 2, 0), H - h))
    lum = ImageStat.Stat(im.crop((x, y, int(x + w), int(y + h))).convert("L")).mean[0]
    fg, bg = ((255, 255, 255), (0, 0, 0, 85)) if lum < 140 else ((25, 25, 25), (255, 255, 255, 85))
    tile = Image.new("RGBA", (int(w * S) + 2, int(h * S) + 2), (0, 0, 0, 0)); d = ImageDraw.Draw(tile)
    d.rounded_rectangle((0, 0, w * S, h * S), h * S / 2, fill=bg)
    cx = pad
    for j, wd in enumerate(ws):
        d.rounded_rectangle((cx * S, (h - dd) / 2 * S, (cx + wd) * S, (h + dd) / 2 * S), dd * S / 2,
                            fill=fg + ((255,) if j == i else (110,)))
        cx += wd + gap
    if arrow:
        t, x0, r = max(3, 4 * u) * S, (pad + dots_w + ag) * S, max(3, 4 * u) * S / 2
        pts = [(x0, (h / 2 - 11 * u) * S), (x0 + cw * S, h / 2 * S), (x0, (h / 2 + 11 * u) * S)]
        d.line(pts, fill=fg + (255,), width=int(t), joint="curve")
        for px, py in (pts[0], pts[2]):
            d.ellipse((px - r, py - r, px + r, py + r), fill=fg + (255,))
        d.ellipse((pts[1][0] - r, pts[1][1] - r, pts[1][0] + r, pts[1][1] + r), fill=fg + (255,))
    tile = tile.resize((max(1, round(tile.width / S)), max(1, round(tile.height / S))), Image.LANCZOS)
    im.paste(tile, (x, y), tile)
    return im