import io, re, sys, os, zipfile, pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import FORMATS, THEMES
from ai import local_plan, Plan
from engine import render, LAYOUTS
from export import to_pdf, to_zip

TXT = " ".join(f"Frase número {i} sobre estratégia de conteúdo para marcas autênticas." for i in range(60))


@pytest.mark.parametrize("fmt", list(FORMATS))
@pytest.mark.parametrize("n", [1, 2, 5, 10])
@pytest.mark.parametrize("layout", list(LAYOUTS))
def test_pdf(fmt, n, layout):
    p = local_plan(TXT, n, 0)
    assert Plan(**p.model_dump()) and len(p.slides) == n
    ims, W = render(p.slides, fmt, THEMES["Obsidiana"], layout, brand="@marca")
    assert not [w for w in W if "incorreta" in w or "vazia" in w or "dimensão" in w]
    pdf = to_pdf(ims)
    assert pdf[:5] == b"%PDF-"
    assert len(re.findall(rb"/Type\s*/Page(?!s)", pdf)) == n
    mb = re.findall(rb"/MediaBox\s*\[\s*0\s+0\s+([\d.]+)\s+([\d.]+)", pdf)
    assert all((round(float(a)), round(float(b))) == (FORMATS[fmt]["w"], FORMATS[fmt]["h"]) for a, b in mb)
    assert len(zipfile.ZipFile(io.BytesIO(to_zip(ims))).namelist()) == n
