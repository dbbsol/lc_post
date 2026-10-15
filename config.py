"""Formatos e temas configuráveis. Para novo formato/tema: adicione uma entrada."""
FORMATS = {
    "Instagram 4:5": dict(w=1080, h=1350, margin=90, top=0),
    "Instagram 1:1": dict(w=1080, h=1080, margin=80, top=0),
    "Story/Reels 9:16": dict(w=1080, h=1920, margin=100, top=150),
}
THEMES = {
    "Obsidiana": dict(bg="#0B0B10", fg="#F4F1EA", accent="#C8A96A", muted="#8A8794", primary="#1A1A24"),
    "Marfim": dict(bg="#F4F1EA", fg="#15141A", accent="#B4452F", muted="#6E6A63", primary="#E6E1D6"),
    "Neon": dict(bg="#07070D", fg="#FFFFFF", accent="#B6FF3B", muted="#9A9AB0", primary="#16162C"),
    "Oceano": dict(bg="#0A1F2E", fg="#EAF6F6", accent="#4FD1C5", muted="#7FA3B0", primary="#10304A"),
}
