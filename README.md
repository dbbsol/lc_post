# Instagram Content Studio
Texto bruto → plano editorial (Gemini ou algoritmo local) → motor determinístico (Pillow) → PDF full-bleed.
## Instalação (Windows + VS Code)
    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    copy .env.example .env   (preencha GEMINI_API_KEY; opcional — sem ela roda em modo demo)
    python -m streamlit run app.py
## Arquitetura
config.py (formatos/temas) · ai.py (schemas, prompt, Gemini, fallback) · engine.py (tipografia, grid, layouts, validação) · export.py (PDF/ZIP) · app.py (UI).
Novo layout: crie uma função em engine.py e registre em LAYOUTS. Novo formato/tema: adicione em config.py.
Trocar layout/tema/formato e editar texto NÃO chamam o Gemini. Testes: `python -m pytest`.
## Problemas comuns
Fonte feia no Linux/Mac: instale Georgia/Arial ou DejaVu. Gemini falhou: o app cai para o modo demo.
## Evolução
Análise visual das imagens pela IA, fontes de marca, PDF vetorial (ReportLab), mais layouts.

## Início rápido (Windows)
Extraia o ZIP, entre na pasta e dê dois cliques em `iniciar.bat` (cria o ambiente, instala e abre o app).
Para usar o Gemini, abra o arquivo `.env` e preencha `GEMINI_API_KEY=sua_chave`.
Modelos disponíveis: DBB Soluções, Legado Capital, Glau Personal, Rosé Gestão e Livre. Novos modelos: crie um arquivo em `templates/`.
Fontes livres (OFL) em `assets/fonts/`.
