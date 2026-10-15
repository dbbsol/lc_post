"""Schemas (Pydantic), prompt, Gemini e planejador local (modo demo)."""
import os, re, json
from typing import Optional
from pydantic import BaseModel, field_validator


class Slide(BaseModel):
    label: str = ""
    headline: str = ""
    subhead: str = ""
    body: str = ""
    cta: str = ""
    highlight: str = ""
    image: Optional[int] = None

    @field_validator("label", "headline", "subhead", "body", "cta", "highlight", mode="before")
    @classmethod
    def _txt(cls, v):  # Gemini costuma devolver null nos campos vazios
        return "" if v is None else str(v)

    @field_validator("image", mode="before")
    @classmethod
    def _img(cls, v):
        try:
            return None if v in (None, "", "null") else int(v)
        except (TypeError, ValueError):
            return None


class Plan(BaseModel):
    slides: list[Slide]


PROMPT = """Você é social media, copywriter e diretor de arte.
Transforme o TEXTO em um plano editorial de EXATAMENTE {n} slide(s) de Instagram ({fmt}).
Regras: preserve ideias e fatos do texto; NÃO invente fatos; headline curta (máx 12 palavras);
subhead = frase de destaque curta (máx 25 palavras, vira o parágrafo em negrito); body curto (máx 40 palavras, frases curtas); label = 1 ou 2 palavras-chave em maiúsculas ou vazio; highlight = palavra-chave grande da capa (1 palavra) ou vazio; slide 1 é capa/hook; último pode ter cta.
Deixe vazio o que não for necessário. Há {k} imagem(ns) (índices 0..{k_1}); use "image" apenas se fizer sentido, senão null.
Responda SOMENTE JSON: {{"slides":[{{"label":"","headline":"","subhead":"","body":"","cta":"","highlight":"","image":null}}]}}
TEXTO:
{text}"""


def local_plan(text, n, k):
    S = [x for x in re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text).strip()) if x] or [""]
    out = []
    for i in range(n):
        ch = S[i * len(S) // n:(i + 1) * len(S) // n] or [S[-1]]
        first, rest = ch[0], " ".join(ch[1:])
        if len(first) > 90:
            w = first.split()
            rest, first = " ".join(ch), " ".join(w[:10]) + "…"
        out.append(Slide(label=f"{i+1:02d}", headline=first, body=rest, image=i if i < k else None))
    return Plan(slides=out)


def _clean(e):
    m = f"{type(e).__name__}: {str(e)}"
    k = os.environ.get("GEMINI_API_KEY", "").strip()
    return (m.replace(k, "***") if k else m)[:300]


def gemini_plan(text, n, fmt, k):
    from google import genai
    key = os.environ["GEMINI_API_KEY"].strip().strip("\"'")
    client = genai.Client(api_key=key)
    models = [m for m in dict.fromkeys([os.getenv("GEMINI_MODEL", "").strip(), "gemini-2.5-flash",
                                        "gemini-flash-latest", "gemini-2.0-flash"]) if m]
    last = None
    for model in models:
        try:
            r = client.models.generate_content(
                model=model, contents=PROMPT.format(n=n, fmt=fmt, k=k, k_1=max(k - 1, 0), text=text),
                config={"response_mime_type": "application/json"})
            raw = r.text or ""
            data = json.loads(raw[raw.index("{"):raw.rindex("}") + 1])
            p = Plan(**data)
            break
        except Exception as e:  # tenta o próximo modelo
            last = e
    else:
        raise last
    p.slides = (p.slides + [Slide()] * n)[:n]
    for i, s in enumerate(p.slides):
        s.label = s.label or f"{i+1:02d}"
        if s.image is not None and not (0 <= s.image < k):
            s.image = None
    return p


def make_plan(text, n, fmt, k, use_ai):
    """Retorna (plano, modo, aviso). Nunca depende da IA para funcionar."""
    if use_ai and os.getenv("GEMINI_API_KEY"):
        try:
            return gemini_plan(text, n, fmt, k), "gemini", ""
        except Exception as e:  # noqa
            return local_plan(text, n, k), "demo", f"Gemini falhou, usei o modo local. Motivo: {_clean(e)}"
    return local_plan(text, n, k), "demo", ""
