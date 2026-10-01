"""Persistência do estado em disco (JSON) e formato de backup."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Optional

SCHEMA_VERSION = 2
STATE_KEYS = ("inventory", "weights", "custom_presets", "requirements", "overrides", "missing_score")


def data_file() -> Optional[Path]:
    """Arquivo de estado; None quando a persistência está desligada (NOTEDALU_PERSIST=0)."""
    if os.environ.get("NOTEDALU_PERSIST", "1").strip().lower() in {"0", "false", "no", "nao", "não", "off"}:
        return None
    return Path(os.environ.get("NOTEDALU_DATA_DIR", ".data")) / "estado.json"


def mtime() -> float:
    path = data_file()
    try:
        return path.stat().st_mtime if path else 0.0
    except OSError:
        return 0.0


def load() -> tuple[Optional[dict], float]:
    path = data_file()
    if not path or not path.exists():
        return None, 0.0
    try:
        with path.open(encoding="utf-8") as fh:
            return parse_backup(json.load(fh)), path.stat().st_mtime
    except (OSError, ValueError):
        return None, 0.0


def save(state: dict) -> float:
    """Grava de forma atômica. Retorna o novo mtime (0 se a persistência estiver desligada)."""
    path = data_file()
    if not path:
        return 0.0
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".estado-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(to_backup(state), fh, ensure_ascii=False, indent=1)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    return path.stat().st_mtime


def to_backup(state: dict) -> dict:
    return {"app": "notedalu", "versao": SCHEMA_VERSION, **{k: state[k] for k in STATE_KEYS if k in state}}


def parse_backup(obj) -> dict:
    """Aceita o backup completo atual ou o formato antigo (lista de notebooks)."""
    if isinstance(obj, list):
        items = [x for x in obj if isinstance(x, dict)]
        if not items:
            raise ValueError("A lista não contém notebooks.")
        return {"inventory": items}
    if not isinstance(obj, dict) or not isinstance(obj.get("inventory"), list):
        raise ValueError("Arquivo não reconhecido: esperado um backup do Note da Lu.")
    state = {k: obj[k] for k in STATE_KEYS if k in obj}
    state["inventory"] = [x for x in state["inventory"] if isinstance(x, dict)]
    for key in ("weights", "custom_presets", "requirements", "overrides"):
        if key in state and not isinstance(state[key], dict):
            del state[key]
    return state
