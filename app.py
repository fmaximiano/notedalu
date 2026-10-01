"""Note da Lu — comparador racional de notebooks (interface Streamlit)."""
from __future__ import annotations

import hashlib
import html
import json
from types import SimpleNamespace

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from notedalu import scoring as sc
from notedalu import storage
from notedalu.data import (
    FIELD_HELP, GROUPS, LONG_TEXT_FIELDS, MODEL_COL, NOTEBOOKS, NUMERIC_FIELDS, PRICE_COL, SPEC_COLUMNS, URL_FIELDS,
)

st.set_page_config(page_title="Note da Lu · Comparador de notebooks", page_icon="💻", layout="wide",
                   initial_sidebar_state="auto")

esc = html.escape

# Paleta categórica validada (ordem fixa) para os grupos de critérios; status reservado para requisitos.
GROUP_COLORS = dict(zip(sc.CRITERIA_GROUPS, ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7"]))
COLOR_A, COLOR_B = "#2a78d6", "#eb6834"
GOOD, BAD = "#0ca30c", "#d03b3b"
INK, INK_2, MUTED, GRID = "#172033", "#4b5565", "#6b7385", "#e6e8ee"
CUSTOM_LABEL = "Personalizado"
MISSING_BG = "#eeede9"
WIDGET_PREFIXES = ("w_", "req_", "ed_", "f_")

ESSENTIAL_COLUMNS = {src for c in sc.CRITERIA for src in c.sources} | {
    "Tela (pol.)", "HDMI", "Leitor de cartões", "Teclado numérico", "Teclado retroiluminado", "Sistema operacional",
    "Garantia informada", "Link do anúncio", "Limitações / ressalvas", "NPU",
}
PRIMARY_SOURCE = {c.sources[0]: c.key for c in sc.CRITERIA}


# ---------------------------------------------------------------------------
# Estado (sessão + arquivo)
# ---------------------------------------------------------------------------
def default_state() -> dict:
    return {
        "inventory": [dict(r) for r in NOTEBOOKS],
        "weights": dict(sc.DEFAULT_WEIGHTS),
        "custom_presets": {},
        "requirements": dict(sc.DEFAULT_REQUIREMENTS),
        "overrides": {},
        "missing_score": sc.DEFAULT_MISSING_SCORE,
    }


def clean_requirements(raw: dict | None) -> dict:
    req = dict(sc.DEFAULT_REQUIREMENTS)
    for key, default in sc.DEFAULT_REQUIREMENTS.items():
        if key in (raw or {}):
            try:
                req[key] = bool(raw[key]) if isinstance(default, bool) else type(default)(raw[key])
            except (TypeError, ValueError):
                pass
    return req


def apply_state(state: dict) -> None:
    base = default_state()
    inventory = state.get("inventory")
    inventory = base["inventory"] if inventory is None else inventory
    ss = st.session_state
    ss.inventory = [sc.normalize_item(r, SPEC_COLUMNS) for r in inventory]
    names = {str(r[MODEL_COL]) for r in ss.inventory}
    ss.weights = sc.clean_weights(state.get("weights"))
    ss.custom_presets = {str(k): sc.clean_weights(v) for k, v in (state.get("custom_presets") or {}).items() if isinstance(v, dict)}
    ss.requirements = clean_requirements(state.get("requirements"))
    ss.overrides = {
        str(name): {k: float(v) for k, v in values.items() if k in sc.CRITERIA_BY_KEY and isinstance(v, (int, float))}
        for name, values in (state.get("overrides") or {}).items() if isinstance(values, dict) and str(name) in names
    }
    try:
        ss.missing_score = float(min(10.0, max(0.0, float(state.get("missing_score", sc.DEFAULT_MISSING_SCORE)))))
    except (TypeError, ValueError):
        ss.missing_score = sc.DEFAULT_MISSING_SCORE
    for key in list(ss.keys()):
        if isinstance(key, str) and key.startswith(WIDGET_PREFIXES):
            del ss[key]
    ss.epoch = ss.get("epoch", 0) + 1


def current_state() -> dict:
    return {k: st.session_state[k] for k in storage.STATE_KEYS}


def state_fingerprint() -> str:
    return json.dumps(storage.to_backup(current_state()), sort_keys=True, ensure_ascii=False, default=str)


def init_state() -> None:
    ss = st.session_state
    if "inventory" not in ss:
        stored, mtime = storage.load()
        apply_state(stored or default_state())
        ss.loaded_mtime, ss.saved = mtime, state_fingerprint() if stored else ""
        ss.excluded = set()
        return
    # Outra sessão gravou depois de nós? Recarrega, a menos que haja mudança local ainda não salva.
    disk = storage.mtime()
    if disk and disk > ss.loaded_mtime + 1e-6 and state_fingerprint() == ss.saved:
        stored, mtime = storage.load()
        if stored:
            apply_state(stored)
            ss.loaded_mtime, ss.saved = mtime, state_fingerprint()


def autosave() -> None:
    ss = st.session_state
    if "inventory" not in ss:
        return
    fingerprint = state_fingerprint()
    if fingerprint == ss.get("saved"):
        return
    try:
        ss.loaded_mtime = storage.save(current_state())
        ss.saved, ss.save_error = fingerprint, None
    except OSError as exc:
        ss.save_error = str(exc)


def toast(message: str, icon: str = "✅") -> None:
    st.session_state.setdefault("toasts", []).append((icon, message))


def all_presets() -> dict[str, dict]:
    return {**sc.PRESETS, **st.session_state.custom_presets}


def matching_preset(weights: dict) -> str | None:
    for name, preset in all_presets().items():
        if all(abs(preset.get(k, 0) - weights.get(k, 0)) < 1e-6 for k in sc.CRITERION_KEYS):
            return name
    return None


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------
def cb_preset() -> None:
    name = st.session_state.get("preset_widget")
    presets = all_presets()
    if name in presets:
        st.session_state.weights = dict(presets[name])
        toast(f"Perfil “{name}” aplicado.", "⚖️")


def cb_items() -> None:
    chosen = set(st.session_state.get("sel_items", []))
    st.session_state.excluded = {str(r[MODEL_COL]) for r in st.session_state.inventory} - chosen


def cb_requirement(key: str) -> None:
    st.session_state.requirements[key] = st.session_state[f"req_{key}"]


def cb_clear_requirements() -> None:
    st.session_state.requirements = dict(sc.DEFAULT_REQUIREMENTS)


def cb_weight(key: str) -> None:
    st.session_state.weights[key] = float(st.session_state[f"w_{key}"])


def cb_missing() -> None:
    st.session_state.missing_score = float(st.session_state["w__missing"])


# ---------------------------------------------------------------------------
# Formatação e componentes
# ---------------------------------------------------------------------------
def fmt_value(value) -> str:
    if isinstance(value, bool):
        return "Sim" if value else "Não"
    if isinstance(value, float):
        return sc.fmt_num(value, 0) if value.is_integer() else str(value).replace(".", ",")
    if isinstance(value, int):
        return sc.fmt_num(value, 0) if abs(value) >= 1000 else str(value)
    return str(value)


def form_value(value) -> str:
    """Valor para o formulário, sem separador de milhar (para não ser relido como decimal)."""
    if isinstance(value, float):
        return str(int(value)) if value.is_integer() else str(value).replace(".", ",")
    return str(value)


def fmt_score(value: float, decimals: int = 1) -> str:
    return sc.fmt_num(float(value), decimals)


def safe_url(value) -> str | None:
    text = str(value or "").strip()
    return text if text.lower().startswith(("http://", "https://")) else None


def blend(hex_a: str, hex_b: str, t: float) -> str:
    a = [int(hex_a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(hex_b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def score_tint(score: float) -> str:
    """Divergente: vermelho (nota baixa) ← branco (5) → azul (nota alta)."""
    t = max(-1.0, min(1.0, (float(score) - 5) / 5))
    return blend("#ffffff", "#b7d3f6", t) if t >= 0 else blend("#ffffff", "#f6c5c4", -t)


def header(title: str, lead: str = "") -> None:
    st.html(f'<div class="nd-header"><h1 class="nd-title">{esc(title)}</h1>'
            + (f'<p class="nd-lead">{lead}</p>' if lead else "") + "</div>")


def stat_cards(cards: list[tuple[str, str, str]]) -> None:
    items = "".join(
        f'<div class="nd-stat"><div class="lbl">{esc(lbl)}</div><div class="val">{esc(val)}</div>'
        f'<div class="sub">{esc(sub)}</div></div>' for lbl, val, sub in cards)
    st.html(f'<div class="nd-grid">{items}</div>')


def callout(text: str, kind: str = "info") -> None:
    st.html(f'<div class="nd-callout {kind}">{text}</div>')


def chip(text: str, kind: str = "") -> str:
    return f'<span class="nd-chip {kind}">{esc(text)}</span>'


def status_chip(ok: bool, pending: str = "") -> str:
    return chip("✓ Atende aos requisitos", "good") if ok else chip(f"✕ Não atende: {pending}", "bad")


def config_of(name: str) -> str:
    parts = name.split(" — ", 1)
    return parts[1] if len(parts) == 2 else ""


def plot(fig: go.Figure, key: str | None = None) -> None:
    fig.update_layout(font=dict(family="Inter, system-ui, sans-serif", color=INK, size=13), separators=",.",
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      hoverlabel=dict(bgcolor="white", font_size=13, bordercolor=GRID))
    st.plotly_chart(fig, width="stretch", theme=None, key=key, config={"displayModeBar": False})


def inject_css() -> None:
    st.html("""
<style>
:root{--nd-ink:#172033;--nd-ink-2:#4b5565;--nd-muted:#6b7385;--nd-line:#e3e7ef;--nd-soft:#f5f7fb;
--nd-primary:#3157d5;--nd-primary-soft:#eef2fd;--nd-good:#0b6b0b;--nd-good-bg:#e8f6e8;--nd-bad:#a82424;--nd-bad-bg:#fcecec;
--nd-warn:#7a5200;--nd-warn-bg:#fff5dc}
.block-container{max-width:1320px;padding-top:4.6rem;padding-bottom:4rem}
[data-testid="stHeaderActionElements"],h1 a,h2 a,h3 a{display:none!important}
h2,h3{letter-spacing:-.015em}
.nd-header{margin:.1rem 0 1.1rem}
.nd-eyebrow{font-size:.74rem;font-weight:700;letter-spacing:.09em;text-transform:uppercase;color:var(--nd-primary)}
.nd-title{font-size:2rem!important;font-weight:800!important;letter-spacing:-.025em;color:var(--nd-ink);margin:.1rem 0 .3rem!important;padding:0!important;line-height:1.15!important}
.nd-lead{color:var(--nd-ink-2);font-size:1.02rem;max-width:860px;line-height:1.55;margin:0}
.nd-grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(200px,1fr))}
.nd-stat{border:1px solid var(--nd-line);border-radius:14px;padding:14px 16px;background:#fff}
.nd-stat .lbl{font-size:.74rem;color:var(--nd-muted);font-weight:700;text-transform:uppercase;letter-spacing:.05em}
.nd-stat .val{font-size:1.4rem;font-weight:750;color:var(--nd-ink);margin-top:4px;line-height:1.2}
.nd-stat .sub{font-size:.84rem;color:var(--nd-muted);margin-top:3px}
.nd-callout{border-radius:12px;padding:11px 14px;font-size:.93rem;line-height:1.5;border:1px solid var(--nd-line);background:var(--nd-soft);color:var(--nd-ink-2);margin:.2rem 0 .6rem}
.nd-callout.info{background:var(--nd-primary-soft);border-color:#d6defa}
.nd-callout.warn{background:var(--nd-warn-bg);border-color:#f3e0ad;color:var(--nd-warn)}
.nd-callout.good{background:var(--nd-good-bg);border-color:#cfe9cf;color:var(--nd-good)}
.nd-callout b{color:inherit}
.nd-chip{display:inline-flex;align-items:center;gap:4px;padding:2px 10px;border-radius:999px;font-size:.78rem;font-weight:600;background:var(--nd-soft);color:var(--nd-ink-2);border:1px solid var(--nd-line);margin:0 5px 5px 0;line-height:1.6}
.nd-chip.good{background:var(--nd-good-bg);color:var(--nd-good);border-color:#cfe9cf}
.nd-chip.bad{background:var(--nd-bad-bg);color:var(--nd-bad);border-color:#f3cccc}
.nd-chip.blue{background:var(--nd-primary-soft);color:var(--nd-primary);border-color:#d6defa}
.nd-step{display:flex;gap:10px;align-items:flex-start}
.nd-step .num{flex:0 0 28px;height:28px;border-radius:50%;background:var(--nd-primary);color:#fff;font-weight:700;display:flex;align-items:center;justify-content:center;font-size:.9rem}
.nd-step .t{font-weight:700;color:var(--nd-ink);font-size:1rem;line-height:1.3}
.nd-step .d{color:var(--nd-ink-2);font-size:.88rem;line-height:1.45;margin-top:3px}
/* Tabela comparativa */
.nd-table-wrap{overflow:auto;max-height:74vh;border:1px solid var(--nd-line);border-radius:14px;background:#fff}
table.nd-spec{border-collapse:separate;border-spacing:0;width:100%;font-size:.87rem;color:var(--nd-ink)}
table.nd-spec th,table.nd-spec td{padding:8px 12px;border-bottom:1px solid var(--nd-line);vertical-align:top;text-align:left;line-height:1.4}
table.nd-spec thead th{position:sticky;top:0;background:#fff;z-index:2;min-width:185px;border-bottom:2px solid var(--nd-line)}
table.nd-spec thead th.corner{left:0;z-index:3;min-width:200px;color:var(--nd-muted);font-size:.74rem;text-transform:uppercase;letter-spacing:.06em}
table.nd-spec th.rowh{position:sticky;left:0;background:#fafbfd;z-index:1;font-weight:600;color:var(--nd-ink-2);min-width:200px;max-width:240px;border-right:1px solid var(--nd-line)}
table.nd-spec tr.grp td{background:var(--nd-soft);font-weight:700;text-transform:uppercase;font-size:.72rem;letter-spacing:.08em;color:var(--nd-primary);padding:6px 12px}
table.nd-spec tr.grp td span{position:sticky;left:12px}
.nd-h-name{font-weight:750;font-size:.93rem;line-height:1.25}
.nd-h-sub{font-weight:500;color:var(--nd-muted);font-size:.78rem;margin-top:2px}
.nd-h-score{margin-top:6px}
.nd-badge{display:inline-block;margin-left:6px;font-size:.72rem;font-weight:700;padding:0 6px;border-radius:6px;background:rgba(255,255,255,.75);color:var(--nd-ink);border:1px solid rgba(23,32,51,.12);white-space:nowrap}
.nd-crit{display:block;font-size:.7rem;font-weight:600;color:var(--nd-primary);margin-top:1px}
table.nd-spec a{color:var(--nd-primary);font-weight:600;text-decoration:none}
/* Cartões de resumo e pódio */
.nd-cards{display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(400px,1fr))}
.nd-card{border:1px solid var(--nd-line);border-radius:16px;padding:18px 18px 14px;background:#fff;display:flex;flex-direction:column;gap:10px}
.nd-card.out{background:#fcfcfd;border-style:dashed}
.nd-card-head{display:flex;gap:12px;align-items:flex-start}
.nd-rank{flex:0 0 40px;height:40px;border-radius:12px;background:var(--nd-primary-soft);color:var(--nd-primary);font-weight:800;display:flex;align-items:center;justify-content:center;font-size:1rem}
.nd-card-title{font-weight:750;font-size:1.06rem;line-height:1.25;color:var(--nd-ink)}
.nd-card-sub{color:var(--nd-muted);font-size:.84rem;margin-top:2px}
.nd-score{margin-left:auto;text-align:right;font-weight:800;font-size:1.5rem;color:var(--nd-ink);line-height:1}
.nd-score small{display:block;font-size:.7rem;font-weight:600;color:var(--nd-muted);margin-top:4px;text-transform:uppercase;letter-spacing:.05em}
.nd-card p{margin:0;color:var(--nd-ink-2);font-size:.92rem;line-height:1.5}
.nd-specs{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
.nd-specs div{background:var(--nd-soft);border-radius:10px;padding:7px 9px;min-width:0}
.nd-specs .k{font-size:.68rem;font-weight:700;color:var(--nd-muted);text-transform:uppercase;letter-spacing:.05em}
.nd-specs .v{font-size:.86rem;font-weight:600;color:var(--nd-ink);overflow-wrap:anywhere;line-height:1.3}
.nd-pc{display:grid;grid-template-columns:1fr 1fr;gap:10px;font-size:.86rem}
.nd-pc ul{margin:.2rem 0 0;padding-left:1.1rem;color:var(--nd-ink-2)}
.nd-pc .h{font-weight:700;font-size:.74rem;text-transform:uppercase;letter-spacing:.05em}
.nd-pc .pro .h{color:var(--nd-good)}.nd-pc .con .h{color:var(--nd-bad)}
.nd-links{font-size:.85rem;border-top:1px solid var(--nd-line);padding-top:9px}
.nd-links a{color:var(--nd-primary);font-weight:600;text-decoration:none;margin-right:14px}
.nd-podium{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));margin-bottom:.6rem}
.nd-pod{border:1px solid var(--nd-line);border-radius:16px;padding:16px;background:#fff}
.nd-pod.first{border:2px solid var(--nd-primary);background:linear-gradient(180deg,#f3f6ff 0%,#fff 70%)}
.nd-pod .pos{font-size:.74rem;font-weight:800;color:var(--nd-primary);text-transform:uppercase;letter-spacing:.08em}
.nd-pod .name{font-weight:750;font-size:1.08rem;margin:.25rem 0 .1rem;color:var(--nd-ink);line-height:1.25}
.nd-pod .cfg{color:var(--nd-muted);font-size:.83rem}
.nd-pod .sc{font-size:2.1rem;font-weight:800;color:var(--nd-ink);margin:.45rem 0 .1rem;line-height:1}
.nd-pod .sc span{font-size:.95rem;color:var(--nd-muted);font-weight:600}
.nd-pod .meta{font-size:.84rem;color:var(--nd-ink-2);margin-bottom:.4rem}
.nd-brand{display:flex;align-items:center;gap:10px;margin:.2rem 0 .4rem}
.nd-brand .logo{width:38px;height:38px;border-radius:11px;background:var(--nd-primary);display:flex;align-items:center;justify-content:center;font-size:1.25rem}
.nd-brand .n{font-weight:800;font-size:1.15rem;color:var(--nd-ink);line-height:1.1}
.nd-brand .s{font-size:.78rem;color:var(--nd-muted)}
.nd-share-t{font-size:.8rem;font-weight:700;color:var(--nd-ink-2);margin-bottom:6px}
.nd-share{display:flex;height:34px;border-radius:10px;overflow:hidden;gap:2px;background:#fff}
.nd-share div{display:flex;align-items:center;justify-content:center;color:#fff;font-size:.78rem;font-weight:700;min-width:0}
.nd-legend{display:flex;flex-wrap:wrap;gap:4px 14px;margin:8px 0 4px;font-size:.8rem;color:var(--nd-ink-2)}
.nd-legend i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:5px;vertical-align:-1px}
.nd-side-h{font-size:.72rem;font-weight:800;letter-spacing:.09em;text-transform:uppercase;color:var(--nd-muted);margin:.6rem 0 .1rem}
[data-testid="stSidebar"] [data-testid="stExpander"] details{background:#fff}
@media (max-width:640px){.nd-cards{grid-template-columns:1fr}.nd-specs{grid-template-columns:repeat(2,minmax(0,1fr))}.nd-title{font-size:1.6rem!important}}
</style>
""")


# ---------------------------------------------------------------------------
# Contexto da execução
# ---------------------------------------------------------------------------
def build_context() -> SimpleNamespace:
    ss = st.session_state
    inventory = ss.inventory
    all_names = [str(r[MODEL_COL]) for r in inventory]
    ss.excluded = {n for n in ss.get("excluded", set()) if n in all_names}
    rows = [r for r in inventory if str(r[MODEL_COL]) not in ss.excluded]
    ev = sc.evaluate(rows, ss.weights, ss.overrides, ss.missing_score)
    rank = sc.ranking_table(rows, ev, ss.requirements)
    return SimpleNamespace(
        inventory=inventory, all_names=all_names, rows=rows, by_name={str(r[MODEL_COL]): r for r in inventory},
        short=sc.short_names(inventory), ev=ev, rank=rank,
        order=rank["Notebook"].tolist() if not rank.empty else [],
    )


def leader_info(ctx) -> dict | None:
    eligible = ctx.rank[ctx.rank["Atende"]] if not ctx.rank.empty else ctx.rank
    if eligible.empty:
        return None
    first = eligible.iloc[0]
    margin = float(first["Nota"] - eligible.iloc[1]["Nota"]) if len(eligible) > 1 else None
    return {"name": first["Notebook"], "score": float(first["Nota"]), "margin": margin, "eligible": len(eligible)}


# ---------------------------------------------------------------------------
# Barra lateral
# ---------------------------------------------------------------------------
REQ_FIELDS = [
    ("max_price", "Preço máximo (R$)", dict(min_value=0.0, step=100.0, format="%.0f"), "Itens sem preço cadastrado não atendem."),
    ("min_ram", "RAM mínima (GB)", dict(min_value=0, step=4), None),
    ("min_ram_ceiling", "Teto de RAM mínimo (GB)", dict(min_value=0, step=4), "RAM alcançável com upgrade oficial."),
    ("min_ssd", "SSD mínimo (GB)", dict(min_value=0, step=128), None),
    ("max_weight", "Peso máximo (kg)", dict(min_value=0.0, step=0.05, format="%.2f"), None),
    ("min_screen", "Tela mínima (pol.)", dict(min_value=0.0, step=0.5, format="%.1f"), None),
    ("max_screen", "Tela máxima (pol.)", dict(min_value=0.0, step=0.5, format="%.1f"), None),
]


def render_sidebar(ctx) -> None:
    ss = st.session_state
    with st.sidebar:
        st.html('<div class="nd-brand"><div class="logo">💻</div><div><div class="n">Note da Lu</div>'
                '<div class="s">Comparador racional de notebooks</div></div></div>')

        st.html('<div class="nd-side-h">Perfil de pesos</div>')
        presets = all_presets()
        current = matching_preset(ss.weights)
        options = list(presets) if current else [CUSTOM_LABEL] + list(presets)
        ss.preset_widget = current or CUSTOM_LABEL
        st.selectbox("Perfil de pesos", options, key="preset_widget", on_change=cb_preset, label_visibility="collapsed",
                     help="Conjunto pronto de pesos. O ajuste fino fica na página Pesos.")

        st.html('<div class="nd-side-h">Notebooks em análise</div>')
        ss.sel_items = [n for n in ctx.all_names if n not in ss.excluded]
        st.pills("Notebooks em análise", ctx.all_names, selection_mode="multi", key="sel_items", on_change=cb_items,
                 format_func=lambda n: ctx.short.get(n, n), label_visibility="collapsed")
        st.caption(f"{len(ctx.rows)} de {len(ctx.all_names)} cadastrados entram nas análises — clique para incluir ou tirar.")

        req = ss.requirements
        active = sum(1 for v in req.values() if v)
        st.html('<div class="nd-side-h">Requisitos mínimos</div>')
        with st.expander(f"{active} requisito(s) ativo(s)" if active else "Nenhum requisito ativo", icon=":material/rule:"):
            st.caption("Eliminatórios: quem não atende continua visível, mas vai para o fim do ranking. Use 0 para não exigir.")
            for key, label, kwargs, help_text in REQ_FIELDS:
                ss[f"req_{key}"] = req[key]
                st.number_input(label, key=f"req_{key}", on_change=cb_requirement, args=(key,), help=help_text, **kwargs)
            for key, label in (("usb_c_charge", "Exigir carga pelo USB‑C"), ("rj45", "Exigir rede cabeada (RJ‑45)")):
                ss[f"req_{key}"] = bool(req[key])
                st.checkbox(label, key=f"req_{key}", on_change=cb_requirement, args=(key,))
            if active:
                st.button("Limpar requisitos", on_click=cb_clear_requirements, width="stretch", icon=":material/close:")

        st.divider()
        if storage.data_file() is None:
            st.caption("💾 Alterações valem só nesta sessão. Faça backup em Equipamentos.")
        elif ss.get("save_error"):
            st.caption(f"⚠️ Não foi possível salvar: {ss.save_error}")
        else:
            st.caption("💾 Alterações salvas automaticamente.")


# ---------------------------------------------------------------------------
# Páginas
# ---------------------------------------------------------------------------
def page_home(ctx) -> None:
    header("Qual notebook comprar?",
           "Compare as fichas técnicas, diga o que importa para você e deixe o ranking organizar a decisão — "
           "com cada nota explicada e ajustável.")
    leader = leader_info(ctx)
    n = len(ctx.rows)
    priced = sum(1 for r in ctx.rows if sc.number_field(r, PRICE_COL))
    stat_cards([
        ("Em análise", f"{n} de {len(ctx.all_names)}", "notebooks cadastrados"),
        ("Preços cadastrados", f"{priced} de {n}", "necessários para custo-benefício"),
        ("Atendem aos requisitos", f"{leader['eligible'] if leader else 0} de {n}", "requisitos na barra lateral"),
        ("Líder atual", ctx.short.get(leader["name"], leader["name"]) if leader else "—",
         (f"nota {fmt_score(leader['score'])}" + (f" · {fmt_score(leader['margin'])} pts à frente" if leader["margin"] is not None else ""))
         if leader else "ninguém atende aos requisitos"),
    ])
    st.write("")
    if n and priced < n:
        callout("<b>Preços faltando.</b> Sem preço, o critério de custo recebe a nota padrão de dado ausente e o ranking "
                "não reflete custo-benefício. Cadastre os valores em <b>Equipamentos → Preços</b>.", "warn")

    st.subheader("Como decidir em 5 passos")
    steps = [
        ("compare", "1", "Compare as fichas", "Lado a lado, só o essencial ou a ficha completa, com cores indicando onde cada um vai bem."),
        (None, "2", "Defina o inegociável", "Na barra lateral: preço máximo, RAM, peso, tamanho de tela, carga via USB‑C…"),
        ("weights", "3", "Diga o que importa", "Escolha um perfil pronto ou ajuste o peso de cada critério de 0 a 10."),
        ("scores", "4", "Confira as notas", "Veja a regra por trás de cada nota e corrija o que não fizer sentido para você."),
        ("ranking", "5", "Decida", "Ranking explicado, teste de robustez entre perfis e análise de custo-benefício."),
    ]
    cols = st.columns(5, gap="small")
    for col, (page, num, title, text) in zip(cols, steps):
        with col.container(border=True, height="stretch"):
            st.html(f'<div class="nd-step"><div class="num">{num}</div><div><div class="t">{esc(title)}</div>'
                    f'<div class="d">{esc(text)}</div></div></div>')
            if page:
                st.page_link(PAGES[page], label="Abrir", icon=":material/arrow_forward:")
            else:
                st.caption("← barra lateral")

    if ctx.rows:
        st.subheader("Panorama rápido")
        render_contrib_chart(ctx, height_per_item=44)
        c1, c2 = st.columns(2)
        c1.page_link(PAGES["summary"], label="Ler o resumo de cada notebook", icon=":material/description:")
        c2.page_link(PAGES["items"], label="Cadastrar, editar ou atualizar preços", icon=":material/laptop:")


def spec_table_html(ctx, columns: list[str]) -> str:
    names = ctx.order
    ev, rank = ctx.ev, ctx.rank.set_index("Notebook")
    head = ['<th class="corner">Especificação</th>']
    for name in names:
        r = rank.loc[name]
        status = "" if r["Atende"] else ' <span class="nd-chip bad">não atende</span>'
        head.append(f'<th><div class="nd-h-name">{esc(ctx.short[name])}</div><div class="nd-h-sub">{esc(config_of(name))}</div>'
                    f'<div class="nd-h-score"><span class="nd-chip blue">{r["Posição"]}º · nota {fmt_score(r["Nota"])}</span>{status}</div></th>')
    body = []
    wanted = set(columns)
    for group, cols in GROUPS.items():
        group_cols = [c for c in cols if c in wanted]
        if not group_cols:
            continue
        body.append(f'<tr class="grp"><td colspan="{len(names) + 1}"><span>{esc(group)}</span></td></tr>')
        for col in group_cols:
            key = PRIMARY_SOURCE.get(col)
            label = esc(col) + (f'<span class="nd-crit">critério: {esc(sc.CRITERIA_BY_KEY[key].label)}</span>' if key else "")
            cells = [f'<th class="rowh">{label}</th>']
            for name in names:
                value = ctx.by_name[name].get(col, "N/D")
                if col in URL_FIELDS:
                    url = safe_url(value)
                    text = f'<a href="{esc(url)}" target="_blank" rel="noopener">abrir ↗</a>' if url else "—"
                elif col == PRICE_COL:
                    text = esc(sc.fmt_brl(sc.number_field(ctx.by_name[name], col))) if not sc.is_unknown(value) else "N/D"
                else:
                    text = esc(fmt_value(value))
                style = ""
                if key:
                    score = ev.final.loc[name, key]
                    mark = " ✎" if ev.manual.loc[name, key] else " ?" if pd.isna(ev.auto.loc[name, key]) else ""
                    style = f' style="background:{MISSING_BG if mark == " ?" else score_tint(score)}"'
                    text += f'<span class="nd-badge" title="Nota no critério {esc(sc.CRITERIA_BY_KEY[key].label)}">{fmt_score(score)}{mark}</span>'
                cells.append(f"<td{style}>{text}</td>")
            body.append("<tr>" + "".join(cells) + "</tr>")
    return (f'<div class="nd-table-wrap"><table class="nd-spec"><thead><tr>{"".join(head)}</tr></thead>'
            f'<tbody>{"".join(body)}</tbody></table></div>')


def page_compare(ctx) -> None:
    header("Fichas lado a lado",
           "Colunas em ordem de ranking. Linhas ligadas a um critério ganham cor e nota: "
           "<b style='color:#1c5cab'>azul</b> = bom, <b style='color:#b42727'>vermelho</b> = fraco.")
    if not ctx.rows:
        st.info("Escolha ao menos um notebook na barra lateral.")
        return
    tab_specs, tab_duel = st.tabs([":material/table_chart: Especificações", ":material/swords: Duelo entre dois"])
    with tab_specs:
        c1, c2, c3 = st.columns([1.1, 1.4, 1], vertical_alignment="bottom")
        view = c1.segmented_control("Ficha", ["Essencial", "Completa"], default="Essencial", required=True, key="cmp_view")
        group = c2.selectbox("Grupo", ["Todos os grupos"] + list(GROUPS), key="cmp_group")
        only_diff = c3.toggle("Só o que muda", value=False, key="cmp_diff", help="Esconde linhas iguais em todos os itens.")
        columns = [c for c in SPEC_COLUMNS if view == "Completa" or c in ESSENTIAL_COLUMNS]
        if group != "Todos os grupos":
            columns = [c for c in columns if c in GROUPS[group]]
        columns = [c for c in columns if c != MODEL_COL]
        if only_diff and len(ctx.rows) > 1:
            columns = [c for c in columns if len({sc.norm(ctx.by_name[n].get(c)) for n in ctx.order}) > 1]
        if not columns:
            st.info("Nenhuma diferença neste grupo.")
        else:
            st.html(spec_table_html(ctx, columns))
            st.caption("Nota no critério (0–10) ao lado do valor · ✎ nota ajustada manualmente · ? dado ausente (recebe a nota padrão definida em Pesos).")
            table = pd.DataFrame({ctx.short[n]: [fmt_value(ctx.by_name[n].get(c, "N/D")) for c in columns] for n in ctx.order}, index=columns)
            st.download_button("Baixar tabela (CSV)", table.to_csv().encode("utf-8-sig"), "comparativo.csv", "text/csv",
                               icon=":material/download:")
    with tab_duel:
        render_duel(ctx)


def render_duel(ctx) -> None:
    if len(ctx.order) < 2:
        st.info("Escolha ao menos dois notebooks na barra lateral.")
        return
    c1, c2 = st.columns(2)
    a = c1.selectbox("Notebook A", ctx.order, index=0, format_func=lambda n: ctx.short[n], key="duel_a")
    b = c2.selectbox("Notebook B", ctx.order, index=1, format_func=lambda n: ctx.short[n], key="duel_b")
    if a == b:
        st.info("Escolha dois notebooks diferentes.")
        return
    ev = ctx.ev
    active = ev.active
    total_w = ev.weights[active].sum() if active else 1
    rows = []
    for key in active:
        sa, sb = ev.final.loc[a, key], ev.final.loc[b, key]
        rows.append({"key": key, "Critério": sc.CRITERIA_BY_KEY[key].label, "pts": (sa - sb) * ev.weights[key] / total_w * 10,
                     "A": sc.spec_text(ctx.by_name[a], key, compact=True), "nota A": sa,
                     "B": sc.spec_text(ctx.by_name[b], key, compact=True), "nota B": sb})
    df = pd.DataFrame(rows)
    wins_a, wins_b = int((df["pts"] > 0.05).sum()), int((df["pts"] < -0.05).sum())
    diff = float(ev.total[a] - ev.total[b])
    winner, loser = (a, b) if diff >= 0 else (b, a)
    stat_cards([
        (f"A · {ctx.short[a]}", f"nota {fmt_score(ev.total[a])}", f"melhor em {wins_a} critério(s)"),
        (f"B · {ctx.short[b]}", f"nota {fmt_score(ev.total[b])}", f"melhor em {wins_b} critério(s)"),
        ("Diferença", f"{fmt_score(abs(diff))} pts", f"a favor de {ctx.short[winner]}" if abs(diff) >= 0.05 else "empate"),
    ])
    shown = df[df["pts"].abs() > 0.05].sort_values("pts")
    if shown.empty:
        st.info("Os dois têm as mesmas notas em todos os critérios ativos.")
        return
    colors = [COLOR_A if v > 0 else COLOR_B for v in shown["pts"]]
    fig = go.Figure(go.Bar(
        x=shown["pts"], y=shown["Critério"], orientation="h", marker=dict(color=colors, line=dict(color="white", width=2)),
        customdata=shown[["A", "B", "nota A", "nota B"]].values,
        hovertemplate="<b>%{y}</b><br>A: %{customdata[0]} → %{customdata[2]:.1f}<br>B: %{customdata[1]} → %{customdata[3]:.1f}"
                      "<br>Diferença no total: %{x:+.1f} pts<extra></extra>"))
    fig.update_layout(height=max(260, 30 * len(shown) + 90), margin=dict(l=10, r=20, t=40, b=30), showlegend=False,
                      title=dict(text=f"<span style='color:{COLOR_A}'>■</span> vantagem de A · "
                                      f"<span style='color:{COLOR_B}'>■</span> vantagem de B (pontos no total)", font_size=13, x=0),
                      xaxis=dict(zeroline=True, zerolinecolor="#c3c2b7", gridcolor=GRID, ticksuffix=" pts"),
                      yaxis=dict(automargin=True))
    plot(fig, key="duel_chart")
    table = df.assign(**{"Vantagem": df["pts"].map(lambda v: f"A +{fmt_score(v)}" if v > 0.05 else f"B +{fmt_score(-v)}" if v < -0.05 else "empate")})
    st.dataframe(table[["Critério", "A", "nota A", "B", "nota B", "Vantagem"]], hide_index=True, width="stretch",
                 column_config={"A": st.column_config.TextColumn(f"A · {ctx.short[a]}", width="large"),
                                "B": st.column_config.TextColumn(f"B · {ctx.short[b]}", width="large"),
                                "nota A": st.column_config.NumberColumn("Nota A", format="%.1f"),
                                "nota B": st.column_config.NumberColumn("Nota B", format="%.1f")})


def page_weights(ctx) -> None:
    ss = st.session_state
    header("O que importa na sua compra",
           "0 ignora o critério; 10 é importância máxima. O que for <b>eliminatório</b> (ex.: preço máximo) "
           "deve ir nos requisitos da barra lateral, não aqui. As mudanças valem na hora.")
    weights = ss.weights
    total = sum(weights.values())
    shares = {g: sum(weights[k] for k in keys) / total * 100 if total else 0 for g, keys in sc.CRITERIA_GROUPS.items()}
    segments = "".join(
        f'<div title="{esc(g)}: {v:.0f}%" style="flex:{v:.3f} 0 0;background:{GROUP_COLORS[g]}">{f"{v:.0f}%" if v >= 6 else ""}</div>'
        for g, v in shares.items() if v > 0)
    legend = "".join(f'<span><i style="background:{GROUP_COLORS[g]}"></i>{esc(g)}</span>' for g in shares)
    st.html(f'<div class="nd-share-t">Distribuição da importância por grupo</div><div class="nd-share">{segments}</div>'
            f'<div class="nd-legend">{legend}</div>')

    current = matching_preset(weights)
    c1, c2, c3 = st.columns([1.4, 1, 1], vertical_alignment="bottom")
    c1.markdown(f"Perfil atual: **{current or 'personalizado'}**")
    if c2.button("Restaurar pesos padrão", icon=":material/restart_alt:", width="stretch", disabled=current == "Equilibrado"):
        ss.weights = dict(sc.DEFAULT_WEIGHTS)
        toast("Pesos padrão restaurados.", "⚖️")
        st.rerun()
    with c3.popover("Salvar como perfil", icon=":material/bookmark_add:", width="stretch"):
        name = st.text_input("Nome do perfil", placeholder="Ex.: Trabalho remoto da Lu", key="new_preset_name").strip()
        if st.button("Salvar", type="primary", disabled=not name):
            if name in sc.PRESETS or name == CUSTOM_LABEL:
                st.error("Esse nome é reservado.")
            else:
                ss.custom_presets[name] = dict(weights)
                toast(f"Perfil “{name}” salvo.", "🔖")
                st.rerun()
        if ss.custom_presets:
            st.divider()
            victim = st.selectbox("Excluir perfil personalizado", list(ss.custom_presets), key="del_preset")
            if st.button("Excluir", icon=":material/delete:"):
                del ss.custom_presets[victim]
                st.rerun()

    st.write("")
    columns = st.columns(3, gap="small")
    load = [0, 0, 0]
    for group, keys in sc.CRITERIA_GROUPS.items():
        target = load.index(min(load))
        load[target] += len(keys) + 1
        with columns[target].container(border=True):
            st.html(f'<div style="display:flex;align-items:center;gap:8px;font-weight:700;color:{INK}">'
                    f'<span style="width:10px;height:10px;border-radius:3px;background:{GROUP_COLORS[group]}"></span>{esc(group)}'
                    f'<span style="margin-left:auto;font-weight:600;color:{MUTED};font-size:.85rem">{shares[group]:.0f}% do total</span></div>')
            for key in keys:
                c = sc.CRITERIA_BY_KEY[key]
                ss[f"w_{key}"] = int(round(weights[key]))
                st.slider(c.label, 0, 10, key=f"w_{key}", on_change=cb_weight, args=(key,), help=c.rule)

    with st.expander("Dados ausentes (N/D)", icon=":material/help:"):
        ss["w__missing"] = float(ss.missing_score)
        st.slider("Nota atribuída quando a ficha não informa o dado", 0.0, 10.0, step=0.5, key="w__missing", on_change=cb_missing,
                  help="Padrão 4: levemente conservador — fabricantes costumam omitir números que não favorecem o produto.")
        st.caption("A página Ranking mostra quanto do peso de cada notebook está apoiado em dados conhecidos.")


def scores_heatmap(ctx) -> go.Figure:
    ev, names = ctx.ev, ctx.order
    keys = list(reversed(sc.CRITERION_KEYS))
    known_z, missing_z, text, hover = [], [], [], []
    for key in keys:
        known_row, missing_row, text_row, hover_row = [], [], [], []
        for n in names:
            manual, missing = bool(ev.manual.loc[n, key]), bool(pd.isna(ev.auto.loc[n, key]))
            value = float(ev.final.loc[n, key])
            gray = missing and not manual
            known_row.append(None if gray else value)
            missing_row.append(value if gray else None)
            text_row.append(fmt_score(value) + (" ✎" if manual else " ?" if gray else ""))
            origin = "nota manual" if manual else "dado ausente → nota padrão" if gray else (ev.notes.loc[n, key] or "regra automática")
            hover_row.append(f"{esc(sc.spec_text(ctx.by_name[n], key))}<br><i>{esc(origin)}</i>")
        known_z.append(known_row)
        missing_z.append(missing_row)
        text.append(text_row)
        hover.append(hover_row)
    x = ["<br>".join(wrap_label(ctx.short[n], 13)) for n in names]
    y = [("⚪ " if ev.weights[k] == 0 else "") + sc.CRITERIA_BY_KEY[k].label for k in keys]
    common = dict(x=x, y=y, text=text, customdata=hover, texttemplate="%{text}", textfont=dict(size=12, color=INK),
                  xgap=2, ygap=2, hovertemplate="<b>%{y}</b> · %{x}<br>%{customdata}<br>Nota: <b>%{z:.1f}</b><extra></extra>")
    fig = go.Figure()
    fig.add_heatmap(z=known_z, zmin=0, zmax=10, colorscale=[[0, "#ee8a89"], [0.5, "#f4f3f0"], [1, "#6da7ec"]],
                    colorbar=dict(title=dict(text="nota", side="top"), thickness=10, len=0.45, tickvals=[0, 5, 10], y=0.75),
                    **common)
    fig.add_heatmap(z=missing_z, zmin=0, zmax=10, colorscale=[[0, MISSING_BG], [1, MISSING_BG]], showscale=False, **common)
    fig.update_layout(height=27 * len(keys) + 150, margin=dict(l=10, r=10, t=10, b=10),
                      xaxis=dict(side="top", tickangle=0, automargin=True), yaxis=dict(automargin=True))
    return fig


def wrap_label(text: str, width: int) -> list[str]:
    lines, line = [], ""
    for word in text.split():
        if line and len(line) + len(word) + 1 > width:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    return lines + ([line] if line else [])


def page_scores(ctx) -> None:
    ss = st.session_state
    header("Como cada característica foi avaliada",
           "Notas de 0 a 10 em escala absoluta, com regras explícitas. Passe o mouse para ver a especificação "
           "e a origem da nota; ajuste o que discordar logo abaixo.")
    if not ctx.rows:
        st.info("Escolha ao menos um notebook na barra lateral.")
        return
    plot(scores_heatmap(ctx), key="scores_heatmap")
    st.caption("✎ nota manual · ? e fundo cinza: dado ausente (recebe a nota padrão) · ⚪ critério com peso 0 (não entra no ranking).")

    st.subheader("Revisar ou ajustar um critério")
    key = st.selectbox("Critério", sc.CRITERION_KEYS, key="score_crit",
                       format_func=lambda k: f"{sc.CRITERIA_BY_KEY[k].group} · {sc.CRITERIA_BY_KEY[k].label}")
    crit = sc.CRITERIA_BY_KEY[key]
    callout(f"<b>Regra:</b> {esc(crit.rule)}", "info")
    ev = ctx.ev
    data = []
    for name in ctx.order:
        auto = ev.auto.loc[name, key]
        data.append({
            "Notebook": ctx.short[name], "_name": name,
            "Especificação": sc.spec_text(ctx.by_name[name], key),
            "Automática": "—" if pd.isna(auto) else fmt_score(auto),
            "Nota ✏️": float(ev.final.loc[name, key]),
            "Origem": "manual" if ev.manual.loc[name, key] else "dado ausente" if pd.isna(auto) else (ev.notes.loc[name, key] or "regra"),
        })
    frame = pd.DataFrame(data)
    form = st.form(f"form_scores_{key}_{ss.epoch}", border=False)
    edited = form.data_editor(
        frame, hide_index=True, width="stretch", key=f"ed_scores_{key}_{ss.epoch}",
        column_order=["Notebook", "Especificação", "Automática", "Nota ✏️", "Origem"],
        disabled=["Notebook", "Especificação", "Automática", "Origem"],
        column_config={
            "Especificação": st.column_config.TextColumn(width="large"),
            "Automática": st.column_config.TextColumn(help="— = dado ausente."),
            "Nota ✏️": st.column_config.NumberColumn(min_value=0.0, max_value=10.0, step=0.1, format="%.1f",
                                                    help="Clique para editar (0 a 10)."),
        })
    apply = form.form_submit_button("Aplicar notas", type="primary", icon=":material/check:")
    n_manual = sum(len(v) for v in ss.overrides.values())
    b2, b3 = st.columns(2)
    if apply:
        changed = 0
        for _, r in edited.iterrows():
            name, value = r["_name"], r["Nota ✏️"]
            if pd.isna(value):
                continue
            base = ss.missing_score if pd.isna(ev.auto.loc[name, key]) else float(ev.auto.loc[name, key])
            item = ss.overrides.setdefault(name, {})
            if abs(float(value) - base) < 0.05:
                changed += item.pop(key, None) is not None
            elif abs(item.get(key, -1) - float(value)) >= 1e-9:
                item[key] = round(float(value), 2)
                changed += 1
            if not item:
                ss.overrides.pop(name, None)
        ss.epoch += 1
        toast(f"{changed} nota(s) atualizada(s)." if changed else "Nenhuma nota mudou.", "🎚️")
        st.rerun()
    if b2.button("Restaurar automáticas deste critério", icon=":material/undo:", width="stretch",
                 disabled=not any(key in v for v in ss.overrides.values())):
        for name in list(ss.overrides):
            ss.overrides[name].pop(key, None)
            if not ss.overrides[name]:
                del ss.overrides[name]
        ss.epoch += 1
        st.rerun()
    if b3.button(f"Restaurar todas ({n_manual} manual)", icon=":material/restart_alt:", width="stretch", disabled=not n_manual):
        ss.overrides = {}
        ss.epoch += 1
        st.rerun()


def render_contrib_chart(ctx, height_per_item: int = 52) -> None:
    groups = ctx.ev.group_contrib()
    order = list(reversed(ctx.order))
    rank = ctx.rank.set_index("Notebook")
    labels = [("✕ " if not rank.loc[n, "Atende"] else "") + ctx.short[n] for n in order]
    fig = go.Figure()
    for group in sc.CRITERIA_GROUPS:
        if group not in groups.columns or groups[group].abs().sum() == 0:
            continue
        fig.add_bar(x=[groups.loc[n, group] for n in order], y=labels, orientation="h", name=group,
                    marker=dict(color=GROUP_COLORS[group], line=dict(color="white", width=2)),
                    hovertemplate=f"<b>%{{y}}</b><br>{group}: %{{x:.1f}} pts<extra></extra>")
    totals = [ctx.ev.total[n] for n in order]
    fig.add_scatter(x=totals, y=labels, mode="text", text=[fmt_score(t) for t in totals], textposition="middle right",
                    textfont=dict(size=13, color=INK, family="Inter, sans-serif"), showlegend=False, hoverinfo="skip")
    fig.update_layout(barmode="stack", height=max(240, height_per_item * len(order) + 110), margin=dict(l=10, r=10, t=10, b=10),
                      legend=dict(orientation="h", y=-0.12 if len(order) > 3 else -0.25, x=0, font_size=12, traceorder="normal"),
                      xaxis=dict(range=[0, max(100, max(totals) + 8)], gridcolor=GRID, ticksuffix="", title=None),
                      yaxis=dict(automargin=True))
    plot(fig, key=f"contrib_{height_per_item}")


def page_ranking(ctx) -> None:
    ss = st.session_state
    header("Resultado da sua ponderação",
           f"Perfil <b>{esc(matching_preset(ss.weights) or 'personalizado')}</b>. Nota de 0 a 100 = média das notas "
           "ponderada pelos pesos. Quem não atende aos requisitos fica no fim, marcado com ✕.")
    rank = ctx.rank
    if rank.empty:
        st.info("Escolha ao menos um notebook na barra lateral.")
        return
    eligible = rank[rank["Atende"]]
    podium = eligible.head(3) if not eligible.empty else rank.head(3)
    if eligible.empty:
        callout("<b>Nenhum notebook atende a todos os requisitos.</b> O pódio abaixo ignora os requisitos; revise-os na barra lateral.", "warn")
    cards = []
    medals = ["1º lugar", "2º lugar", "3º lugar"]
    for i, (_, r) in enumerate(podium.iterrows()):
        name = r["Notebook"]
        good, bad = sc.strengths_weaknesses(ctx.ev, name, 2)
        price = sc.fmt_brl(r["Preço"]) if pd.notna(r["Preço"]) else "preço não informado"
        cards.append(
            f'<div class="nd-pod{" first" if i == 0 else ""}"><div class="pos">{medals[i]}</div>'
            f'<div class="name">{esc(ctx.short[name])}</div><div class="cfg">{esc(config_of(name))}</div>'
            f'<div class="sc">{fmt_score(r["Nota"])} <span>/ 100</span></div>'
            f'<div class="meta">{esc(price)} · técnica {fmt_score(r["Nota técnica"])} · dados {r["Dados conhecidos"]}%</div>'
            + "".join(chip("+ " + g, "good") for g in good) + "".join(chip("− " + b, "bad") for b in bad) + "</div>")
    st.html(f'<div class="nd-podium">{"".join(cards)}</div>')

    notes = []
    if len(eligible) > 1:
        margin = float(eligible.iloc[0]["Nota"] - eligible.iloc[1]["Nota"])
        if margin < 2:
            notes.append(("warn", f"<b>Empate técnico:</b> só {fmt_score(margin)} ponto(s) separam os dois primeiros. "
                                  "Use preço, garantia, reputação do vendedor e o Duelo (em Comparar) para desempatar."))
    if not rank["Preço"].notna().any():
        notes.append(("info", "<b>Sem preços cadastrados:</b> o critério Preço dá a mesma nota a todos. "
                              "A coluna <b>Nota técnica</b> já desconsidera o preço."))
    low = rank[rank["Dados conhecidos"] < 85]
    if not low.empty:
        verb = "tem" if len(low) == 1 else "têm"
        notes.append(("info", f"<b>Ficha incompleta:</b> {', '.join(esc(ctx.short[n]) for n in low['Notebook'])} "
                              f"{verb} parte relevante do peso apoiada em dados ausentes (nota padrão)."))
    for kind, text in notes:
        callout(text, kind)

    st.subheader("De onde vem cada nota")
    st.caption("Cada barra soma os pontos que cada grupo de critérios rende ao total (peso × nota).")
    render_contrib_chart(ctx)

    table = rank.copy()
    table["Notebook"] = table["Notebook"].map(ctx.short)
    table["Situação"] = table["Atende"].map({True: "✓ Atende", False: "✕ Não atende"})
    table["Preço"] = table["Preço"].map(lambda v: sc.fmt_brl(v) if pd.notna(v) else "—")
    st.dataframe(table[["Posição", "Notebook", "Nota", "Nota técnica", "Preço", "Situação", "Pendências", "Dados conhecidos"]],
                 hide_index=True, width="stretch",
                 column_config={
                     "Posição": st.column_config.NumberColumn("#", width="small"),
                     "Nota": st.column_config.ProgressColumn("Nota", min_value=0, max_value=100, format="%.1f"),
                     "Nota técnica": st.column_config.NumberColumn("Nota técnica", format="%.1f", help="Mesma conta, sem o critério Preço."),
                     "Preço": st.column_config.TextColumn("Preço"),
                     "Dados conhecidos": st.column_config.ProgressColumn("Dados conhecidos", min_value=0, max_value=100, format="%d%%",
                                                                         help="Parcela do peso apoiada em dados informados ou notas manuais."),
                 })
    st.download_button("Baixar ranking (CSV)", table.drop(columns=["Atende"]).to_csv(index=False).encode("utf-8-sig"),
                       "ranking_notebooks.csv", "text/csv", icon=":material/download:")

    st.subheader("A decisão é robusta?")
    presets = all_presets()
    positions = sc.preset_positions(ctx.rows, presets, ss.overrides, ss.missing_score, ss.requirements)
    leader = leader_info(ctx)
    if leader:
        wins = int((positions.loc[leader["name"]] == 1).sum())
        kind = "good" if wins >= len(presets) * 0.7 else "warn"
        callout(f"<b>{esc(ctx.short[leader['name']])}</b> fica em 1º lugar em <b>{wins} de {len(presets)}</b> perfis de pesos. "
                + ("Escolha consistente: o resultado não depende de um ajuste fino dos pesos." if kind == "good"
                   else "O vencedor muda conforme o perfil — vale pensar bem no que pesa mais para você."), kind)
    view = positions.loc[ctx.order]
    view.index = [ctx.short[n] for n in view.index]
    st.dataframe(view.style.map(lambda v: "background-color:#cde2fb;font-weight:700" if v == 1 else ""),
                 width="stretch", column_config={"_index": st.column_config.TextColumn("Notebook")})
    st.caption("Posição de cada notebook ao aplicar cada perfil de pesos, mantendo requisitos e notas manuais.")

    st.subheader("Custo-benefício")
    priced = rank[rank["Preço"].notna() & (rank["Preço"] > 0)]
    if len(priced) < 2:
        callout("Cadastre o preço de pelo menos dois notebooks (Equipamentos → Preços) para ver a relação nota técnica × preço.", "info")
    else:
        render_value_chart(ctx, priced)


def render_value_chart(ctx, priced: pd.DataFrame) -> None:
    pts = priced.sort_values("Preço")
    frontier, best = [], -1.0
    for _, r in pts.iterrows():
        if r["Nota técnica"] > best + 1e-9:
            frontier.append(r["Notebook"])
            best = r["Nota técnica"]
    on = pts["Notebook"].isin(frontier)
    fig = go.Figure()
    fr = pts[on]
    fig.add_scatter(x=fr["Preço"], y=fr["Nota técnica"], mode="lines", line=dict(color=COLOR_A, width=2, dash="dot"),
                    hoverinfo="skip", showlegend=False)
    for flag, name, color in ((True, "Melhor opção para o preço", COLOR_A), (False, "Existe opção melhor e mais barata", "#9a9aa3")):
        sub = pts[on == flag]
        if sub.empty:
            continue
        fig.add_scatter(x=sub["Preço"], y=sub["Nota técnica"], mode="markers+text", name=name,
                        text=[ctx.short[n] for n in sub["Notebook"]], textposition="top center", textfont=dict(size=12, color=INK_2),
                        marker=dict(size=13, color=color, line=dict(color="white", width=2)),
                        customdata=[[sc.fmt_brl(p), t / (p / 1000)] for p, t in zip(sub["Preço"], sub["Nota técnica"])],
                        hovertemplate="<b>%{text}</b><br>%{customdata[0]} · nota técnica %{y:.1f}"
                                      "<br>%{customdata[1]:.2f} pts por R$ 1.000<extra></extra>")
    span_x = float(pts["Preço"].max() - pts["Preço"].min()) or float(pts["Preço"].max()) * 0.1
    span_y = float(pts["Nota técnica"].max() - pts["Nota técnica"].min()) or 5.0
    fig.update_layout(height=460, margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=-0.2, x=0),
                      xaxis=dict(title="Preço (R$)", gridcolor=GRID, tickprefix="R$ ", separatethousands=True, automargin=True,
                                 range=[pts["Preço"].min() - span_x * 0.18, pts["Preço"].max() + span_x * 0.18]),
                      yaxis=dict(title="Nota técnica (sem preço)", gridcolor=GRID, automargin=True,
                                 range=[pts["Nota técnica"].min() - span_y * 0.15, pts["Nota técnica"].max() + span_y * 0.2]))
    plot(fig, key="value_chart")
    st.caption("A linha liga as opções que nenhum outro notebook supera sendo mais barato (fronteira de Pareto). "
               "Fora dela, há alternativa melhor por menos.")


def page_summary(ctx) -> None:
    header("Cada notebook em um cartão",
           "Ordem do ranking atual. Pontos fortes e fracos são relativos aos demais notebooks em análise, "
           "considerando o peso de cada critério.")
    if not ctx.rows:
        st.info("Escolha ao menos um notebook na barra lateral.")
        return
    rank = ctx.rank.set_index("Notebook")
    cards = []
    for name in ctx.order:
        row, r = ctx.by_name[name], rank.loc[name]
        good, bad = sc.strengths_weaknesses(ctx.ev, name)
        summary = row.get("Resumo")
        if sc.is_unknown(summary):
            hi, lo = row.get("Destaques objetivos"), row.get("Limitações / ressalvas")
            summary = " ".join(x for x in (None if sc.is_unknown(hi) else f"{hi}.", None if sc.is_unknown(lo) else f"Atenção: {lo}.") if x) \
                or "Sem resumo cadastrado."
        ram = sc.number_field(row, "RAM instalada (GB)")
        ssd = sc.number_field(row, "SSD instalado (GB)")
        specs = [
            ("CPU", str(row.get("CPU"))), ("GPU", str(row.get("GPU"))),
            ("RAM", f"{fmt_value(ram)} GB {row.get('Tipo RAM', '')}".strip() if ram else "N/D"),
            ("SSD", (f"{fmt_value(ssd / 1024)} TB" if ssd and ssd >= 1000 else f"{fmt_value(ssd)} GB") if ssd else "N/D"),
            ("Tela", f"{fmt_value(row.get('Tela (pol.)'))}\" {row.get('Proporção', '')} {row.get('Painel', '')}".strip()),
            ("Bateria · peso", f"{fmt_value(row.get('Bateria (Wh)'))} Wh · {fmt_value(row.get('Peso (kg)'))} kg"),
        ]
        price = sc.fmt_brl(r["Preço"]) if pd.notna(r["Preço"]) else "preço não informado"
        links = [(lbl, safe_url(row.get(col))) for lbl, col in (("Anúncio ↗", "Link do anúncio"), ("Ficha técnica ↗", "Fonte técnica principal"))]
        cards.append(
            f'<div class="nd-card{"" if r["Atende"] else " out"}"><div class="nd-card-head"><div class="nd-rank">{r["Posição"]}º</div>'
            f'<div><div class="nd-card-title">{esc(ctx.short[name])}</div><div class="nd-card-sub">{esc(config_of(name))}</div></div>'
            f'<div class="nd-score">{fmt_score(r["Nota"])}<small>de 100</small></div></div>'
            f'<div>{status_chip(r["Atende"], r["Pendências"])}{chip(price, "blue")}{chip("dados " + str(r["Dados conhecidos"]) + "%")}</div>'
            f'<p>{esc(str(summary))}</p>'
            '<div class="nd-specs">' + "".join(f'<div><div class="k">{esc(k)}</div><div class="v">{esc(v)}</div></div>' for k, v in specs) + "</div>"
            '<div class="nd-pc"><div class="pro"><div class="h">Pontos fortes</div><ul>'
            + ("".join(f"<li>{esc(g)}</li>" for g in good) or "<li>—</li>") + '</ul></div><div class="con"><div class="h">Pontos fracos</div><ul>'
            + ("".join(f"<li>{esc(b)}</li>" for b in bad) or "<li>—</li>") + "</ul></div></div>"
            + ('<div class="nd-links">' + "".join(f'<a href="{esc(u)}" target="_blank" rel="noopener">{lbl}</a>' for lbl, u in links if u) + "</div>"
               if any(u for _, u in links) else "")
            + "</div>")
    st.html(f'<div class="nd-cards">{"".join(cards)}</div>')
    with st.expander("Como interpretar", icon=":material/info:"):
        st.markdown(
            "1. **Requisitos mínimos** eliminam opções incompatíveis.\n"
            "2. **Pesos** representam suas prioridades; **notas** medem cada característica em escala absoluta.\n"
            "3. **Dados conhecidos** mostra quanto do peso está apoiado em informação real — e não na nota padrão de dado ausente.\n"
            "4. O ranking organiza a decisão, mas não substitui preço atualizado, garantia, reputação do vendedor e a leitura do anúncio.")


# ---------------------------------------------------------------------------
# Equipamentos
# ---------------------------------------------------------------------------
def save_item(original: str | None) -> None:
    """Callback do formulário: valida e grava o item (novo ou editado)."""
    ss = st.session_state
    prefix = ss.get("_form_prefix", "")
    parsed = {}
    for col in SPEC_COLUMNS:
        text = str(ss.get(f"{prefix}{col}", "")).strip()
        if not text:
            parsed[col] = "N/D"
        elif col in NUMERIC_FIELDS:
            number = sc.parse_number(text, money=(col == PRICE_COL))
            parsed[col] = (int(number) if float(number).is_integer() else number) if number is not None else text
        else:
            parsed[col] = text
    if sc.is_unknown(parsed.get("GPU")):
        parsed["GPU"] = sc.resolved_gpu(parsed)
    new_name = str(parsed[MODEL_COL]).strip()
    if sc.is_unknown(new_name):
        ss.form_error = "Preencha **Modelo / configuração** — é o identificador do notebook."
        return
    names = [str(r[MODEL_COL]) for r in ss.inventory]
    if new_name in names and new_name != original:
        ss.form_error = "Já existe um notebook com esse Modelo / configuração."
        return
    ss.form_error = None
    item = sc.normalize_item(parsed, SPEC_COLUMNS)
    if original and original in names:
        old = ss.inventory[names.index(original)]
        ss.inventory[names.index(original)] = item
        kept = {}
        for key, value in ss.overrides.pop(original, {}).items():
            if all(sc.norm(old.get(src)) == sc.norm(item.get(src)) for src in sc.CRITERIA_BY_KEY[key].sources):
                kept[key] = value  # nota manual só sobrevive se a especificação de origem não mudou
        if kept:
            ss.overrides[new_name] = kept
        if original in ss.excluded:
            ss.excluded = (ss.excluded - {original}) | {new_name}
        toast(f"“{new_name}” atualizado.")
    else:
        ss.inventory.append(item)
        toast(f"“{new_name}” cadastrado.")
    ss.edit_choice = new_name
    ss.epoch += 1


def page_items(ctx) -> None:
    ss = st.session_state
    header("Cadastro de notebooks",
           "Cadastre, edite, atualize preços e faça backup. Campos vazios viram N/D; números aceitam vírgula decimal.")
    t_list, t_prices, t_form, t_backup = st.tabs([":material/list: Cadastrados", ":material/sell: Preços",
                                                  ":material/edit: Cadastrar / editar", ":material/save: Backup"])
    with t_list:
        overview = pd.DataFrame([{
            "Notebook": ctx.short[str(r[MODEL_COL])], "Configuração": config_of(str(r[MODEL_COL])),
            "Preço": sc.fmt_brl(sc.number_field(r, PRICE_COL)), "CPU": r.get("CPU"),
            "RAM (GB)": sc.number_field(r, "RAM instalada (GB)"), "SSD (GB)": sc.number_field(r, "SSD instalado (GB)"),
            "Tela (pol.)": sc.number_field(r, "Tela (pol.)"), "Peso (kg)": sc.number_field(r, "Peso (kg)"),
            "Em análise": str(r[MODEL_COL]) not in ss.excluded,
        } for r in ctx.inventory])
        st.dataframe(overview, hide_index=True, width="stretch",
                     column_config={"Tela (pol.)": st.column_config.NumberColumn(format="localized"),
                                    "Peso (kg)": st.column_config.NumberColumn(format="localized")})
        with st.expander("Remover um notebook", icon=":material/delete:"):
            victim = st.selectbox("Notebook", ctx.all_names, format_func=lambda n: ctx.short[n], key="remove_item", index=None,
                                  placeholder="Escolha…")
            confirm = st.checkbox("Confirmo a remoção (não dá para desfazer, exceto restaurando um backup).", key="confirm_remove")
            if st.button("Remover", type="primary", disabled=not (victim and confirm), icon=":material/delete:"):
                ss.inventory = [r for r in ss.inventory if str(r[MODEL_COL]) != victim]
                ss.overrides.pop(victim, None)
                ss.excluded.discard(victim)
                ss.confirm_remove = False
                toast(f"“{ctx.short[victim]}” removido.", "🗑️")
                st.rerun()

    with t_prices:
        st.caption("Atualize preços e links de uma vez. O preço é o único critério relativo: a opção mais barata recebe 10.")
        frame = pd.DataFrame([{"_name": str(r[MODEL_COL]), "Notebook": ctx.short[str(r[MODEL_COL])],
                               "Preço (R$)": sc.fmt_num(sc.number_field(r, PRICE_COL), 2) if sc.number_field(r, PRICE_COL) else "",
                               "Link do anúncio": safe_url(r.get("Link do anúncio")) or ""} for r in ctx.inventory])
        form = st.form(f"form_prices_{ss.epoch}", border=False)
        edited = form.data_editor(frame, hide_index=True, width="stretch", key=f"ed_prices_{ss.epoch}",
                                column_order=["Notebook", "Preço (R$)", "Link do anúncio"], disabled=["Notebook"],
                                column_config={
                                    "Preço (R$)": st.column_config.TextColumn(help="Ex.: 3.499,90 ou 3499. Vazio = sem preço."),
                                    "Link do anúncio": st.column_config.LinkColumn(width="large", validate=r"^https?://.*",
                                                                                   display_text=r"https?://(?:www\.)?([^/]+)"),
                                })
        if form.form_submit_button("Salvar preços e links", type="primary", icon=":material/check:"):
            by_name = {str(r[MODEL_COL]): r for r in ss.inventory}
            invalid = []
            for _, r in edited.iterrows():
                item = by_name.get(r["_name"])
                if item is None:
                    continue
                text = str(r["Preço (R$)"] or "").strip()
                price = sc.parse_number(text, money=True) if text else None
                if text and not price:
                    invalid.append(r["Notebook"])
                    continue
                item[PRICE_COL] = "N/D" if not price else (int(price) if float(price).is_integer() else round(price, 2))
                link = str(r["Link do anúncio"] or "").strip()
                item["Link do anúncio"] = link if safe_url(link) else "N/D"
            if invalid:
                st.error("Preço não reconhecido em: " + ", ".join(invalid) + ". Use, por exemplo, 3.499,90.")
            else:
                ss.epoch += 1
                toast("Preços e links salvos.", "🏷️")
                st.rerun()

    with t_form:
        new_blank, new_copy = "➕ Novo (em branco)", "📄 Novo a partir de outro"
        options = [new_blank, new_copy] + ctx.all_names
        if ss.get("edit_choice") not in options:
            ss.edit_choice = new_blank
        c1, c2 = st.columns(2)
        choice = c1.selectbox("O que deseja fazer?", options, key="edit_choice",
                              format_func=lambda n: n if n in (new_blank, new_copy) else f"Editar: {ctx.short.get(n, n)}")
        base_name = None
        if choice == new_copy:
            base_name = c2.selectbox("Copiar dados de", ctx.all_names, format_func=lambda n: ctx.short[n], key="copy_from")
        elif choice != new_blank:
            base_name = choice
        base = ctx.by_name.get(base_name) if base_name else None
        original = choice if choice not in (new_blank, new_copy) else None
        prefix = f"f_{ss.epoch}_{hashlib.md5(f'{choice}|{base_name}'.encode()).hexdigest()[:8]}_"
        ss._form_prefix = prefix
        if ss.get("form_error"):
            st.error(ss.form_error)
        st.caption("Dica: **GPU** é o campo usado na pontuação — se ficar vazio, usa a dedicada (se houver) ou a integrada. "
                   "Informe o **PassMark** da CPU (cpubenchmark.net) para uma nota de processador precisa.")
        with st.form(f"item_form_{prefix}", border=False):
            for group, cols in GROUPS.items():
                with st.expander(group, expanded=group in {"Identificação", "Compra"}):
                    grid = st.columns(2)
                    for i, col in enumerate(cols):
                        value = "" if base is None else form_value(base.get(col, "N/D"))
                        if base is not None and col == MODEL_COL and choice == new_copy:
                            value = f"{value} (cópia)"
                        target = st if col in LONG_TEXT_FIELDS else grid[i % 2]
                        if col in LONG_TEXT_FIELDS:
                            target.text_area(col, value=value, key=f"{prefix}{col}", help=FIELD_HELP.get(col), height=90)
                        else:
                            target.text_input(col, value=value, key=f"{prefix}{col}", help=FIELD_HELP.get(col))
            st.form_submit_button("Salvar notebook", type="primary", icon=":material/save:", width="stretch",
                                  on_click=save_item, args=(original,))

    with t_backup:
        st.markdown("**Backup completo** — notebooks, pesos, perfis, requisitos e notas manuais.")
        payload = json.dumps(storage.to_backup(current_state()), ensure_ascii=False, indent=1)
        st.download_button("Baixar backup (JSON)", payload.encode("utf-8"), "notedalu_backup.json", "application/json",
                           icon=":material/download:")
        uploaded = st.file_uploader("Restaurar backup", type=["json"], help="Aceita também o backup antigo (só a lista de notebooks).")
        if uploaded is not None:
            try:
                state = storage.parse_backup(json.load(uploaded))
                n_items = len(state["inventory"])
                st.info(f"Arquivo válido: {n_items} notebook(s)" + (" e configurações de decisão." if len(state) > 1 else "."))
                if st.button("Substituir dados atuais pelo backup", type="primary", icon=":material/upload:"):
                    merged = {**current_state(), **state}
                    if len(state) == 1:  # formato antigo: notas manuais não se aplicam aos novos itens
                        merged["overrides"] = {}
                    apply_state(merged)
                    toast("Backup restaurado.", "♻️")
                    st.rerun()
            except (ValueError, UnicodeDecodeError) as exc:
                st.error(f"Não foi possível ler o arquivo: {exc}")
        st.divider()
        st.markdown("**Recomeçar do zero** — volta à base original de notebooks e às configurações padrão.")
        sure = st.checkbox("Entendo que cadastros, pesos e notas manuais atuais serão descartados.", key="confirm_reset")
        if st.button("Restaurar dados originais", disabled=not sure, icon=":material/restart_alt:"):
            apply_state(default_state())
            ss.excluded = set()
            ss.confirm_reset = False
            toast("Dados originais restaurados.", "♻️")
            st.rerun()
        if storage.data_file() is None:
            st.caption("A persistência em disco está desligada (NOTEDALU_PERSIST=0): faça backup para não perder alterações.")
        else:
            st.caption(f"Os dados também são salvos automaticamente em `{storage.data_file()}` no servidor. "
                       "Em hospedagens com disco efêmero (ex.: Railway sem volume), um redeploy apaga esse arquivo — mantenha um backup.")


# ---------------------------------------------------------------------------
# Execução
# ---------------------------------------------------------------------------
init_state()
for _icon, _message in st.session_state.pop("toasts", []):
    st.toast(_message, icon=_icon)
inject_css()
CTX = build_context()

PAGES = {
    "home": st.Page(lambda: page_home(CTX), title="Início", icon=":material/home:", url_path="inicio", default=True),
    "compare": st.Page(lambda: page_compare(CTX), title="Comparar", icon=":material/compare_arrows:", url_path="comparar"),
    "weights": st.Page(lambda: page_weights(CTX), title="Pesos", icon=":material/tune:", url_path="pesos"),
    "scores": st.Page(lambda: page_scores(CTX), title="Notas", icon=":material/grading:", url_path="notas"),
    "ranking": st.Page(lambda: page_ranking(CTX), title="Ranking", icon=":material/leaderboard:", url_path="ranking"),
    "summary": st.Page(lambda: page_summary(CTX), title="Resumo", icon=":material/description:", url_path="resumo"),
    "items": st.Page(lambda: page_items(CTX), title="Equipamentos", icon=":material/laptop:", url_path="equipamentos"),
}
LEGACY_PAGES = {"comparativo": "compare", "pesos": "weights", "notas": "scores", "ranking": "ranking",
                "itens": "items", "resumo": "summary", "inicio": "home"}

render_sidebar(CTX)
navigation = st.navigation(list(PAGES.values()), position="top")
legacy = st.query_params.get("page")
if legacy in LEGACY_PAGES:
    del st.query_params["page"]
    st.switch_page(PAGES[LEGACY_PAGES[legacy]])
try:
    navigation.run()
finally:
    autosave()
