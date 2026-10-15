import sys, os, re, pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import FORMATS
from ai import local_plan
from templates import TEMPLATES
from dsl import render_dsl
from export import to_pdf
TXT = " ".join(f"Frase {i} sobre consórcio, planejamento financeiro e contemplação para quem quer comprar." for i in range(40))
DSL = [k for k, v in TEMPLATES.items() if v.get("engine") == "dsl"]

@pytest.mark.parametrize("name", DSL)
@pytest.mark.parametrize("fmt", list(FORMATS))
@pytest.mark.parametrize("n", [1, 2, 5, 10])
def test_dsl(name, fmt, n):
    p = local_plan(TXT, n, 0); p.slides[0].highlight = "consórcio"
    ims, W = render_dsl(p.slides, fmt, TEMPLATES[name])
    assert len(ims) == n and not [w for w in W if "incorreta" in w or "vazia" in w or "fora da" in w or "sobreposição" in w], W
    assert len(re.findall(rb"/Type\s*/Page(?!s)", to_pdf(ims))) == n
