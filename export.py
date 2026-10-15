"""PDF full-bleed (página = tamanho exato do formato, 1px = 1pt) e ZIP de PNGs."""
import io, zipfile


def to_pdf(ims):
    b = io.BytesIO()
    ims[0].convert("RGB").save(b, "PDF", resolution=72.0, save_all=True, append_images=[i.convert("RGB") for i in ims[1:]])
    return b.getvalue()


def to_zip(ims):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w", zipfile.ZIP_DEFLATED) as z:
        for k, im in enumerate(ims, 1):
            p = io.BytesIO(); im.save(p, "PNG"); z.writestr(f"slide_{k:02d}.png", p.getvalue())
    return b.getvalue()
