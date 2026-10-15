"""Registro automático: todo arquivo .py nesta pasta com um dict TEMPLATE vira opção no app."""
import importlib, pkgutil
TEMPLATES = {}
for _m in pkgutil.iter_modules(__path__):
    _t = importlib.import_module(f"templates.{_m.name}").TEMPLATE
    TEMPLATES[_t["name"]] = _t
