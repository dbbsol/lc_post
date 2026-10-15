import time
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
load_dotenv()
from config import FORMATS, THEMES
from ai import make_plan, gemini_plan, _clean
from engine import render, LAYOUTS
from templates import TEMPLATES
from template_engine import render_tpl
from dsl import render_dsl
from export import to_pdf, to_zip

st.set_page_config("Instagram Content Studio", "✦", layout="wide")
st.markdown(f"<style>{(Path(__file__).parent / 'assets' / 'style.css').read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
S = st.session_state
for k, v in dict(plan=None, cur=0, ver=0, mode="", msg="").items():
    S.setdefault(k, v)

if not S.get("splash"):
    _b = st.empty()
    _b.markdown('<div class="splash"><div class="splash-ring"></div><div class="splash-title">CONTENT STUDIO</div><div class="splash-sub">Instagram · Editorial · Render Engine</div><div class="splash-bar"><span></span></div></div>', unsafe_allow_html=True)
    time.sleep(1.2); _b.empty(); S.splash = True

with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-mark">✦</div><div><div class="brand-name">CONTENT STUDIO</div><div class="brand-sub">Instagram Publishing Engine</div></div></div>', unsafe_allow_html=True)
    st.markdown("### ⚙️ Configuração")
    kind = st.radio("Tipo", ["Post único", "Carrossel"], horizontal=True)
    n = 1 if kind == "Post único" else st.slider("Slides", 2, 10, 5)
    fmt = st.selectbox("Formato", list(FORMATS))
    modelo = st.selectbox("Modelo", list(TEMPLATES) + ["Livre (layouts criativos)"])
    usetpl = modelo in TEMPLATES
    layout = st.selectbox("Layout", list(LAYOUTS), disabled=usetpl)
    theme = st.selectbox("Tema", list(THEMES), disabled=usetpl)
    use_ai = st.toggle("Inteligência editorial (Gemini)", True)
    brand = st.text_input("Marca / @usuário", "")
    logo = st.file_uploader("Logo (opcional)", ["png", "jpg", "jpeg", "webp"])
    dev = st.toggle("Modo desenvolvedor", False)
    st.markdown('<div class="side-title">INTELIGÊNCIA ARTIFICIAL</div>', unsafe_allow_html=True)
    import os
    _ok = bool(os.getenv("GEMINI_API_KEY"))
    st.markdown(f'<div class="status {"ok" if _ok else "off"}"><i></i>{"Gemini configurado" if _ok else "Gemini não configurado (modo demo)"}</div>', unsafe_allow_html=True)
    if _ok and st.button("Testar Gemini", width="stretch"):
        try:
            with st.spinner("Testando..."):
                gemini_plan("Teste rápido de conexão.", 1, "Instagram 4:5", 0)
            st.success("Gemini respondeu corretamente ✓")
        except Exception as e:
            st.error(_clean(e))
    st.caption("🔑 Chave Gemini: arquivo `.env` (pasta do projeto) → `GEMINI_API_KEY=sua_chave`. Reinicie o app após salvar.")

tpl = TEMPLATES.get(modelo)
ncont = n - 1 if tpl and tpl.get("brand_slide") and n >= 3 else n
st.markdown('<div class="hero"><div class="hero-eyebrow">✦ AI · EDITORIAL · RENDER ENGINE</div><h1>Instagram Content Studio</h1><p>Do texto bruto à publicação premium: a IA planeja, o motor desenha e o PDF sai perfeito.</p></div>', unsafe_allow_html=True)
_cur = 3 if S.plan else (1 if st.session_state.get("txt_main", "").strip() else 0)
_names = ["Conteúdo", "Geração", "Preview", "Exportação"]
_cur = {0: 0, 1: 1, 3: 3}[_cur]
_h = ""
for _n, _t in enumerate(_names):
    _st = "active" if _n == _cur else ("done" if _n < _cur else "todo")
    _h += f'<div class="step {_st}"><div class="dot">{"✓" if _st == "done" else _n + 1}</div><div class="lbl">{_t}</div></div>'
    if _n < 3:
        _h += f'<div class="line {"full" if _n < _cur else ""}"></div>'
st.markdown(f'<div class="stepper">{_h}</div>', unsafe_allow_html=True)
def head(e, t, d):
    st.markdown(f'<div class="page-head"><div class="page-eyebrow">{e}</div><h3>{t}</h3><p>{d}</p></div>', unsafe_allow_html=True)
head("ETAPA 1", "Conteúdo", "Cole o texto e envie imagens opcionais. O sistema decide estrutura, hierarquia e composição.")
txt = st.text_area("Conteúdo", height=220, placeholder="Digite ou cole o conteúdo da publicação...", label_visibility="collapsed", key="txt_main")
st.caption(f"{len(txt)} caracteres · ~{len(txt.split())} palavras")
files = st.file_uploader("Imagens (opcional)", ["png", "jpg", "jpeg", "webp"], accept_multiple_files=True)
imgs = [f.getvalue() for f in files]


def gen():
    if not txt.strip():
        st.warning("Cole um texto para começar."); return
    try:
        with st.spinner("Planejando a publicação..."):
            S.plan, S.mode, S.msg = make_plan(txt, ncont, fmt, len(imgs), use_ai)
            S.cur, S.ver = 0, S.ver + 1
    except Exception as e:
        st.error("Não foi possível gerar o planejamento. Verifique sua chave Gemini e tente novamente.")
        if dev:
            st.exception(e)


b1, b2, _ = st.columns([2, 1.2, 4])
if b1.button("✦ ORGANIZAR E GERAR", type="primary", width="stretch"):
    gen()
    if S.plan:
        st.toast("Publicação planejada!", icon="✨")
if S.plan and b2.button("↻ REGENERAR", width="stretch"):
    gen()

if S.plan:
    if S.mode == "demo":
        st.markdown('<span class="badge">Modo demonstração (algoritmo local)</span>', unsafe_allow_html=True)
    if S.msg:
        st.warning(S.msg)
    sl = S.plan.slides
    if len(sl) != ncont:
        st.info("O número de slides mudou: clique em REGENERAR para redistribuir o conteúdo.")
    S.cur = min(S.cur, len(sl) - 1)
    head("ETAPA 2", "Preview e edição", "Edite o texto, troque imagem, layout ou tema: tudo recompõe localmente, sem nova chamada à IA.")
    left, right = st.columns([3, 2])
    with right:  # edição manual: re-renderiza localmente, sem chamar o Gemini
        s, v, i = sl[S.cur], S.ver, S.cur
        s.headline = st.text_input("Headline", s.headline, key=f"h{i}_{v}")
        s.subhead = st.text_input("Subheadline", s.subhead, key=f"s{i}_{v}")
        s.body = st.text_area("Body", s.body, key=f"b{i}_{v}")
        s.cta = st.text_input("CTA", s.cta, key=f"c{i}_{v}")
        s.label = st.text_input("Etiqueta (palavra-chave)", s.label, key=f"l{i}_{v}")
        s.highlight = st.text_input("Palavra de destaque (capa)", s.highlight, key=f"x{i}_{v}")
        opts = ["Sem imagem"] + [f"Imagem {j+1}" for j in range(len(imgs))]
        cur_i = s.image + 1 if s.image is not None and s.image < len(imgs) else 0
        pick = st.selectbox("Imagem do slide", opts, index=cur_i, key=f"i{i}_{v}")
        s.image = None if pick == "Sem imagem" else opts.index(pick) - 1
    if tpl and tpl.get("engine") == "dsl":
        ims, warns = render_dsl(sl, fmt, tpl, brand, imgs)
    elif tpl:
        ims, warns = render_tpl(sl, fmt, tpl, brand, ncont != n)
    else:
        ims, warns = render(sl, fmt, THEMES[theme], layout, imgs, brand, logo.getvalue() if logo else None)
    with left:
        with st.container(key="stage"):
            st.markdown(f'<div class="slide-count">SLIDE {S.cur+1} / {len(ims)}</div>', unsafe_allow_html=True)
            st.image(ims[S.cur], width="stretch")
    for w in dict.fromkeys(warns):
        st.warning(w)
    cols = st.columns(len(ims))
    for k, cc in enumerate(cols):
        with cc.container(key=f"thumb_{'on' if k == S.cur else 'off'}_{k}"):
            st.image(ims[k], width="stretch")
            if st.button(f"{k+1:02d}", key=f"t{k}", width="stretch"):
                S.cur = k; st.rerun()
    head("ETAPA 3", "Exportação", "PDF full-bleed no tamanho exato do formato, ou PNGs em ZIP.")
    e1, e2, _ = st.columns([2, 2, 4])
    name = "instagram_post" if len(ims) == 1 else "instagram_carousel"
    e1.download_button("⬇ BAIXAR PDF", to_pdf(ims), f"{name}.pdf", "application/pdf", width="stretch")
    e2.download_button("⬇ BAIXAR IMAGENS (ZIP)", to_zip(ims), f"{name}.zip", "application/zip", width="stretch")
