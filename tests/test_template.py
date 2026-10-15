import sys, os, re, pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import FORMATS
from ai import local_plan
from templates import TEMPLATES
from template_engine import render_tpl
from export import to_pdf
TXT = " ".join(f"Frase {i} sobre automação de processos para empresas que querem crescer." for i in range(50))

@pytest.mark.parametrize("fmt", list(FORMATS))
@pytest.mark.parametrize("n", [1, 2, 3, 5, 10])
def test_tpl(fmt, n):
    tpl = TEMPLATES["DBB Soluções"]; nc = n - 1 if n >= 3 else n
    ims, W = render_tpl(local_plan(TXT, nc, 0).slides, fmt, tpl, "", n >= 3)
    assert len(ims) == n and not [w for w in W if "incorreta" in w or "vazia" in w]
    assert len(re.findall(rb"/Type\s*/Page(?!s)", to_pdf(ims))) == n
