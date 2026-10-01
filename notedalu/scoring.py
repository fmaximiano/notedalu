"""Modelo de decisão: leitura das especificações, notas por critério e ranking.

Este módulo não depende do Streamlit, para poder ser testado isoladamente.

Princípios:
- Notas em ESCALA ABSOLUTA (0 a 10), definidas por âncoras explícitas. Uma diferença
  pequena entre dois equipamentos gera uma diferença pequena de nota — ao contrário da
  normalização mín-máx, que esticava qualquer diferença até 6 pontos.
- Cada característica é contada UMA vez (ex.: 16:10 pesa em "Proporção", não também em
  "Resolução"; Thunderbolt, vídeo e carga pelo USB-C formam um único critério).
- Quando a ficha traz alternativas ("Wi-Fi 5 ou Wi-Fi 6", "220 ou 250 nits"), vale a
  pior hipótese.
- Dado ausente não vira "Não": recebe a nota configurável para dados ausentes.
- Preço é o único critério relativo: a opção mais barata recebe 10.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Callable, Optional

import pandas as pd

from .data import MODEL_COL, PRICE_COL

Score = tuple[Optional[float], str]

# ---------------------------------------------------------------------------
# Leitura de texto e números
# ---------------------------------------------------------------------------
_DASHES = dict.fromkeys(map(ord, "‐‑‒–—−"), "-")

_UNKNOWN_EXACT = {
    "", "n/d", "nd", "n/a", "na", "-", "?", "none", "nan", "null", "desconhecido",
    "não informado", "não informada", "não confirmado", "não confirmada",
    "não especificado", "não especificada",
}
_UNKNOWN_PREFIXES = (
    "não informad", "não confirmad", "não especificad", "não determin", "não divulgad",
    "desconhecid", "opcional / não determin",
)


def norm(value) -> str:
    """Texto minúsculo, com hífens/traços e o sinal × padronizados."""
    if value is None:
        return ""
    s = str(value).translate(_DASHES).replace(" ", " ").replace("×", "x")
    return re.sub(r"\s+", " ", s).strip().lower()


def is_unknown(value) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    s = norm(value)
    return s in _UNKNOWN_EXACT or s.startswith(_UNKNOWN_PREFIXES) or "não determin" in s


def yes_no(value) -> Optional[bool]:
    """'Sim…' → True, 'Não…' → False; dado ausente ou ambíguo → None."""
    if is_unknown(value):
        return None
    s = norm(value)
    if s.startswith("sim"):
        return True
    if s.startswith("não") or s.startswith("nao") or s == "0":
        return False
    return None


_NUM_RE = re.compile(r"\d+(?:[.,]\d+)?")


def numbers(value) -> list[float]:
    """Todos os números presentes no valor (vírgula decimal aceita)."""
    if isinstance(value, bool):
        return []
    if isinstance(value, (int, float)):
        return [] if (isinstance(value, float) and math.isnan(value)) else [float(value)]
    if is_unknown(value):
        return []
    return [float(n.replace(",", ".")) for n in _NUM_RE.findall(norm(value))]


def conservative_number(value, higher_is_better: bool = True) -> Optional[float]:
    """Número da pior hipótese quando a ficha traz alternativas."""
    nums = numbers(value)
    if not nums:
        return None
    return min(nums) if higher_is_better else max(nums)


def parse_number(text, *, money: bool = False) -> Optional[float]:
    """Converte '3.499,90', '3499.90', 'R$ 3.499' e '1,69' em número."""
    if isinstance(text, bool):
        return None
    if isinstance(text, (int, float)):
        return None if (isinstance(text, float) and math.isnan(text)) else float(text)
    s = str(text or "").strip().lower().replace("r$", "").replace(" ", "").replace(" ", "")
    if not s or not re.fullmatch(r"[\d.,]+", s):
        return None
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        if s.count(",") > 1:
            return None
        s = s.replace(",", ".")
    elif s.count(".") > 1:
        s = s.replace(".", "")
    elif "." in s and money and len(s.split(".")[1]) == 3:
        s = s.replace(".", "")  # 3.499 → milhar
    try:
        return float(s)
    except ValueError:
        return None


def number_field(row: dict, col: str) -> Optional[float]:
    value = row.get(col)
    parsed = parse_number(value, money=(col == PRICE_COL))
    if parsed is not None:
        return parsed
    return conservative_number(value)


def interp(x: float, points: list[tuple[float, float]]) -> float:
    if x <= points[0][0]:
        return points[0][1]
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return points[-1][1]


def log_scale(x: float, low: float, high: float) -> float:
    if x <= 0:
        return 0.0
    return 10 * min(1.0, max(0.0, math.log(x / low) / math.log(high / low)))


def fmt_num(value: float, decimals: int = 0) -> str:
    text = f"{value:,.{decimals}f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_brl(value: Optional[float]) -> str:
    return "—" if value is None else f"R$ {fmt_num(value, 2)}"


# ---------------------------------------------------------------------------
# Processador: PassMark (multi + single), informado ou de referência
# ---------------------------------------------------------------------------
# Médias de cpubenchmark.net consultadas em out/2026.
CPU_REFERENCE = {
    "core i5-1335u": (13769, 3242),
    "core ultra 5 115u": (12771, 3421),
    "core i7-10510u": (6335, 2191),
    "core i7-1355u": (13840, 3368),
    "core 5 120u": (14862, 3456),
    "core i5-1334u": (12991, 3229),
}

# Estimativas aproximadas (±15%) para CPUs sem PassMark informado. Primeira regra que casar vale.
CPU_ESTIMATES: list[tuple[str, int, int]] = [
    (r"ultra 9 2\d\dhx", 60000, 4700), (r"ultra 7 2\d\dhx", 50000, 4500), (r"ultra 5 2\d\dhx", 42000, 4300),
    (r"ultra 9 2\d\dh", 34000, 4300), (r"ultra 7 2\d\dh", 31000, 4200), (r"ultra 5 2\d\dh", 26000, 4000),
    (r"ultra 9 2\d\dv", 21000, 4400), (r"ultra 7 2\d\dv", 20000, 4300), (r"ultra 5 2\d\dv", 17500, 4100),
    (r"ultra [579] 2\d\du", 15000, 3700),
    (r"ultra 9 1\d\dh", 29000, 3900), (r"ultra 7 1\d\dh", 25500, 3700), (r"ultra 5 1\d\dh", 21500, 3500),
    (r"ultra 7 1\d\du", 15500, 3600), (r"ultra 5 1\d\du", 13500, 3450),
    (r"core 7 2\d\dh", 26000, 3700), (r"core 5 2\d\dh", 21000, 3500),
    (r"core 7 1\d\du", 15500, 3600), (r"core 5 1\d\du", 14800, 3450), (r"core 3 1\d\du", 10500, 3300),
    (r"i9-1[34]\d{3}hx", 46000, 4300), (r"i7-1[34]\d{3}hx", 34000, 4000), (r"i5-1[34]\d{3}hx", 30000, 3800),
    (r"i9-1[234]\d{3}h", 29000, 3900), (r"i7-1[34]\d{3}h", 25000, 3700), (r"i7-12\d{3}h", 23500, 3500),
    (r"i5-1[234]\d{3}h", 18000, 3350),
    (r"i7-1[23]\d{2}p", 18500, 3300), (r"i5-1[23]\d{2}p", 17000, 3200),
    (r"i7-1[23]\d{2}u", 13500, 3250), (r"i5-1[23]\d{2}u", 13000, 3150), (r"i3-1[23]\d{2}u", 10000, 3000),
    (r"i7-11\d{3}h", 21000, 3200), (r"i5-11\d{3}h", 17000, 3000),
    (r"i7-11\d{2}g7", 10500, 2900), (r"i5-11\d{2}g7", 10000, 2750), (r"i3-11\d{2}g4", 6000, 2500),
    (r"i7-10\d{3}h", 12500, 2700), (r"i5-10\d{3}h", 10000, 2500),
    (r"i7-10\d{2}g7", 8800, 2500), (r"i5-10\d{2}g[14]", 7800, 2300),
    (r"i7-10\d{3}u", 6500, 2200), (r"i5-10\d{3}u", 6100, 2050), (r"i3-10\d{3}u", 3800, 2000),
    (r"i7-8\d{3}u", 6200, 2050), (r"i5-8\d{3}u", 5900, 1950), (r"i3-8\d{3}u", 3500, 1850),
    (r"i3-n3\d\d", 10000, 2050), (r"\bn[12]\d\d\b", 5500, 1950), (r"\bn[456]\d{3}\b", 2300, 1150),
    (r"ryzen ai 9 hx", 35000, 4200), (r"ryzen ai 9", 33000, 4100), (r"ryzen ai 7", 29000, 4050), (r"ryzen ai 5", 24000, 3900),
    (r"ryzen 9 [78]\d{3}hx", 55000, 4200), (r"ryzen [79] [78]\d4[05]hs?", 29000, 3950), (r"ryzen 5 [78]\d4[05]hs?", 23500, 3750),
    (r"ryzen 7 [78]\d40u", 25000, 3800), (r"ryzen 5 [78]\d40u", 20000, 3600), (r"ryzen 5 7540u", 14500, 3550),
    (r"ryzen 7 7735h", 23500, 3400), (r"ryzen 5 7535h", 19000, 3200), (r"ryzen 7 7735u", 20000, 3300),
    (r"ryzen 5 7535u", 17000, 3100), (r"ryzen 7 7730u", 18000, 3100), (r"ryzen 5 7530u", 15500, 3000),
    (r"ryzen 3 7330u", 9500, 2900), (r"ryzen 5 7520u", 9600, 2450), (r"ryzen 3 7320u", 6000, 2300),
    (r"ryzen 7 6\d00h", 23000, 3400), (r"ryzen 5 6\d00h", 19500, 3250), (r"ryzen 7 6\d00u", 18500, 3200), (r"ryzen 5 6\d00u", 15500, 3100),
    (r"ryzen 7 5\d00h", 21000, 3100), (r"ryzen 5 5\d00h", 17000, 2950),
    (r"ryzen 7 5825u", 17500, 3000), (r"ryzen 5 5625u", 14500, 2950), (r"ryzen 7 5700u", 15500, 2600),
    (r"ryzen 5 5500u", 13000, 2550), (r"ryzen 3 5425u", 9500, 2900), (r"ryzen 3 5300u", 10500, 2500),
    (r"ryzen 7 4\d00u", 13500, 2450), (r"ryzen 5 4\d00u", 11000, 2350), (r"ryzen [57] 3\d00u", 7000, 1900),
    (r"apple m4 max", 50000, 5000), (r"apple m4 pro", 38000, 4900), (r"apple m4", 23000, 4800),
    (r"apple m3 max", 40000, 4600), (r"apple m3 pro", 27000, 4500), (r"apple m3", 19000, 4600),
    (r"apple m2", 15500, 4000), (r"apple m1", 14500, 3700),
    (r"snapdragon x elite|x1e", 26000, 4000), (r"snapdragon x plus|x1p", 22000, 3800),
    (r"ryzen 9", 30000, 3800), (r"ryzen 7", 18000, 3200), (r"ryzen 5", 14000, 3000), (r"ryzen 3", 8000, 2600),
    (r"celeron|pentium|athlon", 2500, 1300),
]


def _cpu_key(cpu) -> str:
    s = norm(cpu)
    s = re.sub(r"[®™]|\(r\)|\(tm\)|processador|processor|@ ?\d+(?:[.,]\d+)? ?ghz", "", s)
    s = re.sub(r"^(intel|amd)\s+", "", s.strip())
    return re.sub(r"\s+", " ", s).strip()


def cpu_performance(row: dict) -> tuple[Optional[float], Optional[float], str]:
    """(PassMark multi, PassMark single, origem)."""
    multi = number_field(row, "CPU PassMark (multi)")
    single = number_field(row, "CPU PassMark (single)")
    key = _cpu_key(row.get("CPU"))
    if multi:
        return multi, single, "PassMark do cadastro"
    if key in CPU_REFERENCE:
        m, s = CPU_REFERENCE[key]
        return m, s, "PassMark de referência"
    for pattern, m, s in CPU_ESTIMATES:
        if re.search(pattern, key):
            return m, s, "estimativa pelo nome da CPU (informe o PassMark para precisão)"
    return None, None, "CPU sem referência: informe o PassMark no cadastro"


def score_cpu(row: dict, ctx: dict) -> Score:
    multi, single, origin = cpu_performance(row)
    if not multi:
        return None, origin
    multi_score = log_scale(multi, 2000, 40000)
    if single:
        return 0.6 * multi_score + 0.4 * log_scale(single, 1500, 5000), origin
    return multi_score, origin


# ---------------------------------------------------------------------------
# GPU: estimativa de 3DMark Time Spy (escala logarítmica)
# ---------------------------------------------------------------------------
GPU_ESTIMATES: list[tuple[str, int]] = [
    (r"rtx 5090", 23000), (r"rtx 5080", 20000), (r"rtx 5070 ti", 16500), (r"rtx 5070", 13500),
    (r"rtx 5060", 12000), (r"rtx 5050", 10000),
    (r"rtx 4090", 20000), (r"rtx 4080", 17500), (r"rtx 4070", 12000), (r"rtx 4060", 10500), (r"rtx 4050", 8700),
    (r"rtx 3080", 12000), (r"rtx 3070", 10500), (r"rtx 3060", 8500), (r"rtx 3050 ti", 5300), (r"rtx 3050", 5000),
    (r"rtx 2050", 3400), (r"rtx 20[678]0", 7000), (r"gtx 1660", 5800), (r"gtx 1650", 3500),
    (r"mx ?5[57]0", 2600), (r"mx ?4[5]0", 2300), (r"mx ?3[35]0", 1300), (r"mx ?[12]\d0", 1000),
    (r"rx 7900m", 18000), (r"rx 7800m", 15000), (r"rx 7700s", 11000), (r"rx 7600m xt", 10500), (r"rx 7600s|rx 7600m", 9000),
    (r"rx 6800m", 12000), (r"rx 6700m", 10000), (r"rx 6600m", 8500), (r"rx 65[05]0m", 5600), (r"rx 5500m", 4500),
    (r"radeon 890m", 3900), (r"radeon 880m", 3300), (r"radeon 780m", 2900), (r"radeon 760m", 2300),
    (r"radeon 740m", 1500), (r"radeon 680m", 2500), (r"radeon 660m", 1800), (r"radeon 610m", 600),
    (r"rx 640", 1300), (r"radeon 625|radeon 6[23]0\b", 900),
    (r"arc 140v", 4000), (r"arc 130v", 3300), (r"arc a7\d0m", 9500), (r"arc a5\d0m", 7000),
    (r"arc a370m", 4500), (r"arc a350m", 3300),
    (r"adreno", 2000),
]


def _dual_channel(row: dict) -> Optional[bool]:
    dual = yes_no(row.get("Dual-channel de fábrica"))
    if dual is None and "lpddr" in norm(row.get("Tipo RAM")):
        return True  # LPDDR soldada opera sempre em múltiplos canais
    return dual


def _intel_igpu(gpu: str, cpu: str, dual: Optional[bool]) -> Optional[tuple[int, str]]:
    if re.search(r"ultra [579] 2\d\dv", cpu):
        return (4000 if re.search(r"ultra [79]", cpu) else 3300), "Arc 130V/140V"
    if re.search(r"ultra [579] 1\d\dh|ultra [579] 2\d\dh", cpu) or ("arc" in gpu and "ultra" in cpu):
        return 3300, "Arc integrada (Meteor/Arrow Lake H)"
    if re.search(r"ultra [579] 1\d\du|ultra [579] 2\d\du", cpu):
        xe3 = re.search(r"ultra 5 115u", cpu) or "3 xe" in gpu
        base = 1750 if xe3 else 2100
        return (base if dual is not False else int(base * 0.6)), "Intel Graphics (Meteor Lake)"
    modern = re.search(r"i[3579]-1[1-4]\d{2,3}|core [357] [12]\d\du", cpu) or "iris xe" in gpu
    if modern:
        eu = 96 if re.search(r"i7-1[1-3]\d{2}[ug]|core 7 1\d\du|i7-1[1-3]65", cpu) else 64 if re.search(r"i3-|core 3 ", cpu) else 80
        if dual is False:
            return int(850 * eu / 80), "Iris Xe limitada a modo UHD (RAM single-channel)"
        base = {96: 1800, 80: 1500, 64: 1100}[eu]
        if dual is None and "iris xe" not in gpu:
            return int(base * 0.8), "Iris Xe (dual-channel não confirmado)"
        return base, f"Iris Xe {eu} EU"
    if "iris plus" in gpu:
        return 1100, "Iris Plus"
    if re.search(r"\bn[12]\d\d\b|i3-n3", cpu):
        return 550, "UHD (Alder Lake-N)"
    if "uhd" in gpu or "hd graphics" in gpu or "intel" in gpu:
        return 500, "UHD 620/630 (geração antiga)"
    return None


def _amd_igpu(cpu: str) -> Optional[tuple[int, str]]:
    table = [
        (r"ryzen ai 9 hx", 3900), (r"ryzen ai 9", 3600), (r"ryzen ai 7", 3300), (r"ryzen ai 5", 2000),
        (r"ryzen [79] [78]\d4[05]", 2900), (r"ryzen 5 [78]\d4[05]", 2300), (r"ryzen [79] 7\d35|ryzen [79] 6\d00", 2500),
        (r"ryzen 5 7\d35|ryzen 5 6\d00", 1800), (r"ryzen [3579] 7\d20", 600), (r"ryzen [3579] [57]\d[23]\d", 1300),
        (r"ryzen [3579] 4\d00", 1100), (r"ryzen [3579] 3\d00", 800),
    ]
    for pattern, value in table:
        if re.search(pattern, cpu):
            return value, "Radeon integrada"
    return None


def gpu_performance(row: dict) -> tuple[Optional[int], str]:
    gpu = norm(row.get("GPU"))
    if is_unknown(gpu):
        return None, "GPU não informada"
    for pattern, value in GPU_ESTIMATES:
        if re.search(pattern, gpu):
            return value, "estimativa pelo modelo da GPU"
    cpu = _cpu_key(row.get("CPU"))
    if "apple" in cpu:
        level = {"m4": 4000, "m3": 3400, "m2": 2600, "m1": 2000}
        for chip, value in level.items():
            if chip in cpu:
                factor = 2.5 if ("max" in cpu) else 1.6 if ("pro" in cpu) else 1.0
                return int(value * factor), "GPU Apple (estimativa)"
    if "intel" in gpu or "iris" in gpu or "uhd" in gpu:
        found = _intel_igpu(gpu, cpu, _dual_channel(row))
        if found:
            return found[0], f"estimativa: {found[1]}"
    if "radeon" in gpu or "amd" in gpu:
        found = _amd_igpu(cpu)
        if found:
            dual = _dual_channel(row)
            value = found[0] if dual is not False else int(found[0] * 0.6)
            return value, f"estimativa: {found[1]}" + (" em single-channel" if dual is False else "")
    return None, "GPU sem referência: ajuste a nota manualmente"


def score_gpu(row: dict, ctx: dict) -> Score:
    value, note = gpu_performance(row)
    if value is None:
        return None, note
    return log_scale(value, 300, 20000), note


# ---------------------------------------------------------------------------
# Demais critérios
# ---------------------------------------------------------------------------
def score_price(row: dict, ctx: dict) -> Score:
    price = number_field(row, PRICE_COL)
    if not price or price <= 0:
        return None, "preço não informado"
    best = ctx.get("min_price") or price
    return 10 * (best / price) ** 2, ""


def score_ram(row: dict, ctx: dict) -> Score:
    gb = number_field(row, "RAM instalada (GB)")
    if not gb:
        return None, ""
    return interp(gb, [(4, 1), (8, 4), (12, 6), (16, 8), (24, 9), (32, 9.6), (64, 10)]), ""


def score_ram_speed(row: dict, ctx: dict) -> Score:
    kind = norm(row.get("Tipo RAM"))
    if "lpddr5x" in kind:
        base = 9.5
    elif "lpddr5" in kind:
        base = 9.0
    elif "ddr5" in kind:
        base = 8.5
    elif "lpddr4" in kind:
        base = 7.0
    elif "ddr4" in kind:
        base = 6.0
    elif "ddr3" in kind:
        base = 3.0
    else:
        return None, ""
    dual = _dual_channel(row)
    if dual is False:
        return base - 3.5, "single-channel de fábrica"
    if dual is None:
        return base - 1.5, "dual-channel não confirmado"
    return base, ""


def ram_ceiling(row: dict) -> Optional[float]:
    """Maior quantidade de RAM alcançável (de fábrica ou com upgrade oficial)."""
    installed = number_field(row, "RAM instalada (GB)")
    official_max = number_field(row, "RAM máxima oficial (GB)")
    expandable = yes_no(row.get("Expansão de RAM"))
    soldered = yes_no(row.get("RAM soldada"))
    if official_max is None:
        if expandable is False or soldered is True:
            return installed
        return None
    ceiling = installed if expandable is False else official_max
    return max(x for x in (ceiling, installed) if x is not None)


def score_ram_ceiling(row: dict, ctx: dict) -> Score:
    ceiling = ram_ceiling(row)
    if not ceiling:
        return None, ""
    return interp(ceiling, [(4, 0), (8, 1.5), (12, 3.5), (16, 5), (24, 7), (32, 8.5), (48, 9.3), (64, 10)]), f"teto de {fmt_num(ceiling)} GB"


def score_ssd(row: dict, ctx: dict) -> Score:
    gb = number_field(row, "SSD instalado (GB)")
    if not gb:
        return None, ""
    return interp(gb, [(128, 1), (256, 3.5), (512, 6.5), (1024, 8.5), (2048, 10)]), ""


def score_storage_expansion(row: dict, ctx: dict) -> Score:
    free = number_field(row, "Slots M.2 livres")
    if free is None:
        return None, ""
    if free >= 2:
        return 10.0, ""
    if free >= 1:
        return 8.5, "slot M.2 livre"
    obs = norm(row.get("Armazenamento máx./observação"))
    if re.search(r"2[,.]5|sata", obs):
        return 5.5, "baia 2,5\" conforme configuração"
    return 4.0, "ampliar exige trocar o SSD"


_RES_WORDS = [("4k", 2160), ("uhd", 2160), ("3k", 1800), ("2.8k", 1800), ("2,8k", 1800), ("wqxga", 1600),
              ("qhd", 1440), ("2k", 1440), ("wuxga", 1200), ("fhd", 1080), ("full hd", 1080), ("hd+", 900), ("hd", 768)]


def _resolutions(value) -> list[tuple[int, int]]:
    s = norm(value)
    return [(int(a), int(b)) for a, b in re.findall(r"(\d{3,4})\s*x\s*(\d{3,4})", s)]


def score_resolution(row: dict, ctx: dict) -> Score:
    res = _resolutions(row.get("Resolução"))
    if res:
        vertical = min(min(w, h) for w, h in res)
    else:
        s = norm(row.get("Resolução"))
        vertical = next((v for word, v in _RES_WORDS if word in s), None)
        if vertical is None:
            return None, ""
    return interp(vertical, [(720, 1), (768, 2), (900, 4.5), (1080, 7), (1200, 7.5), (1440, 8.5), (1600, 9), (1800, 9.5), (2160, 10)]), ""


def score_aspect(row: dict, ctx: dict) -> Score:
    s = norm(row.get("Proporção"))
    if "16:10" in s or "3:2" in s:
        return 9.0, ""
    if "4:3" in s:
        return 8.0, ""
    if "16:9" in s:
        return 6.0, ""
    if "21:9" in s:
        return 5.0, ""
    res = _resolutions(row.get("Resolução"))
    if res:
        w, h = res[0]
        return (9.0 if max(w, h) / min(w, h) < 1.7 else 6.0), "derivada da resolução"
    return None, ""


def _panel_option(s: str) -> Optional[float]:
    if "oled" in s:
        return 10.0
    if "mini" in s and "led" in s:
        return 9.5
    if "ips-level" in s or "ips level" in s:
        return 7.5
    if re.search(r"\bips\b", s):
        return 8.0
    if "wva" in s:
        return 7.0
    if re.search(r"\bva\b", s):
        return 6.5
    if re.search(r"\btn\b", s):
        return 3.0
    return None


def score_panel(row: dict, ctx: dict) -> Score:
    s = norm(row.get("Painel"))
    options = [v for v in (_panel_option(part) for part in re.split(r"\bou\b", s)) if v is not None]
    if not options:
        return None, ""
    return min(options), ("varia por submodelo: pior hipótese" if len(options) > 1 else "")


def score_brightness(row: dict, ctx: dict) -> Score:
    nits = conservative_number(row.get("Brilho (nits)"))
    if not nits:
        return None, ""
    note = "pior hipótese" if len(numbers(row.get("Brilho (nits)"))) > 1 else ""
    return interp(nits, [(200, 2), (220, 3), (250, 4.5), (300, 6.5), (350, 7.5), (400, 8.5), (500, 9.5), (600, 10)]), note


def srgb_equivalent(value) -> Optional[float]:
    """Converte a cobertura informada para um equivalente aproximado em sRGB."""
    s = norm(value)
    if is_unknown(s):
        return None
    found = re.findall(r"(\d+(?:[.,]\d+)?)\s*%\s*(srgb|ntsc|dci-p3|p3|adobe)?", s)
    if not found:
        return None
    values = []
    for number, space in found:
        pct = float(number.replace(",", "."))
        space = space or ("ntsc" if "ntsc" in s else "srgb" if "srgb" in s else "dci-p3" if "p3" in s else "adobe" if "adobe" in s else "")
        if not space:
            space = "ntsc" if pct <= 50 else "srgb"
        factor = {"ntsc": 1.39, "srgb": 1.0, "dci-p3": 1.33, "p3": 1.33, "adobe": 1.35}[space]
        values.append(pct * factor)
    return max(values)


def score_color(row: dict, ctx: dict) -> Score:
    eq = srgb_equivalent(row.get("Cobertura de cores"))
    if not eq:
        return None, ""
    return interp(eq, [(40, 1), (50, 2.5), (62, 4), (75, 6), (90, 8), (100, 9), (130, 10)]), f"≈ {fmt_num(eq)}% sRGB"


def score_refresh(row: dict, ctx: dict) -> Score:
    hz = conservative_number(row.get("Taxa de atualização (Hz)"))
    if not hz:
        return None, ""
    return interp(hz, [(30, 1), (60, 5), (90, 7), (120, 8.5), (144, 9.2), (165, 10)]), ""


def score_webcam(row: dict, ctx: dict) -> Score:
    s = norm(row.get("Webcam"))
    if is_unknown(s):
        return None, ""
    if re.search(r"2160|4k", s):
        return 10.0, ""
    if re.search(r"1440|qhd|5 ?mp", s):
        return 9.5, ""
    if re.search(r"1080|fhd|full hd|2 ?mp", s):
        return 8.5, ""
    if re.search(r"720|\bhd\b|1 ?mp|0[,.]9 ?mp", s):
        return 5.0, ""
    if re.search(r"480|vga|0[,.]3 ?mp", s):
        return 2.0, ""
    return None, ""


_WIFI_SCORE = {"7": 10.0, "6e": 9.0, "6": 8.0, "5": 5.5, "4": 3.0}
_WIFI_80211 = {"be": "7", "ax": "6", "ac": "5", "n": "4"}


def score_wifi(row: dict, ctx: dict) -> Score:
    s = norm(row.get("Wi‑Fi"))
    gens = re.findall(r"wi-?fi ?(7|6e|6|5|4)\b", s)
    if not gens:
        gens = [_WIFI_80211[g] for g in re.findall(r"802\.11 ?(be|ax|ac|n)\b", s)]
    if not gens:
        return None, ""
    score = min(_WIFI_SCORE[g] for g in gens)
    notes = []
    if len(set(gens)) > 1:
        notes.append("varia por placa: pior hipótese")
    if re.search(r"\b1x1\b", s):
        score -= 0.7
        notes.append("antena 1×1")
    return score, "; ".join(notes)


def _feature(value, keywords: tuple[str, ...] = ()) -> Optional[bool]:
    flag = yes_no(value)
    if flag is None and not is_unknown(value) and any(k in norm(value) for k in keywords):
        return True
    return flag


def score_usb_c(row: dict, ctx: dict) -> Score:
    ports = norm(row.get("USB‑C"))
    if ports.startswith(("não", "0", "nenhum")):
        return 0.0, "sem USB‑C"
    tb = norm(row.get("Thunderbolt / USB4"))
    if re.search(r"thunderbolt|usb4", tb) and not tb.startswith("não"):
        return 10.0, "Thunderbolt/USB4"
    video = _feature(row.get("USB‑C com vídeo"), ("displayport", "dp alt"))
    charge = _feature(row.get("USB‑C com carregamento"), ("power delivery",))
    if video is None and charge is None and is_unknown(tb) and is_unknown(ports):
        return None, ""
    score = 2.0 + (3.0 if video else 0) + (3.5 if charge else 0)
    if re.search(r"10 ?gbps|gen ?2", ports):
        score += 0.5
    unknown = [name for name, flag in (("vídeo", video), ("carga", charge)) if flag is None]
    return score, (f"{' e '.join(unknown)} não confirmado(s)" if unknown else "")


def score_rj45(row: dict, ctx: dict) -> Score:
    flag = yes_no(row.get("Ethernet RJ‑45"))
    if flag is None:
        return None, ""
    return (10.0 if flag else 3.0), ""


def score_battery(row: dict, ctx: dict) -> Score:
    wh = conservative_number(row.get("Bateria (Wh)"))
    if not wh:
        return None, ""
    return interp(wh, [(30, 1.5), (40, 3.5), (45, 4.5), (50, 5.5), (55, 6.5), (60, 7.3), (70, 8.5), (80, 9.4), (100, 10)]), ""


def score_weight(row: dict, ctx: dict) -> Score:
    kg = conservative_number(row.get("Peso (kg)"), higher_is_better=False)
    if not kg:
        return None, ""
    if kg > 20:  # informado em gramas
        kg /= 1000
    return interp(kg, [(1.0, 10), (1.2, 9.3), (1.4, 8.3), (1.6, 7.0), (1.8, 5.6), (2.0, 4.3), (2.3, 2.5), (2.6, 1.0)]), ""


def score_build(row: dict, ctx: dict) -> Score:
    s = norm(row.get("Material / construção"))
    if is_unknown(s):
        return None, ""
    metal = re.search(r"alum|metál|metal|magnés|magnes", s)
    plastic = re.search(r"plást|plast|\babs\b|pc\+abs|policarbonato", s)
    uncertain = re.search(r"\bvaria|\bou\b|opcional", s)
    if metal and plastic:
        return (5.5, "varia por submodelo: pior hipótese") if uncertain else (7.0, "metal + plástico")
    if metal:
        return (7.0 if uncertain else 8.5), ""
    if plastic:
        return 5.5, ""
    return None, ""


# ---------------------------------------------------------------------------
# Critérios
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Criterion:
    key: str
    label: str
    group: str
    sources: tuple[str, ...]
    weight: float
    rule: str
    scorer: Callable[[dict, dict], Score]


CRITERIA: list[Criterion] = [
    Criterion("preco", "Preço", "Preço", (PRICE_COL,), 9,
              "Único critério relativo: a opção mais barata entre as analisadas recebe 10; as demais, 10 × (menor preço ÷ preço)². "
              "Ex.: 20% mais cara ≈ 6,9; 50% mais cara ≈ 4,4.", score_price),
    Criterion("cpu", "Processador", "Desempenho", ("CPU", "CPU PassMark (multi)", "CPU PassMark (single)"), 9,
              "PassMark em escala logarítmica: 60% multinúcleo (2 mil = 0, 40 mil = 10) + 40% núcleo único (1.500 = 0, 5.000 = 10). "
              "Sem PassMark informado, usa a referência interna ou uma estimativa pelo nome.", score_cpu),
    Criterion("gpu", "Gráficos (GPU)", "Desempenho", ("GPU", "CPU", "Dual-channel de fábrica"), 3,
              "Estimativa de 3DMark Time Spy em escala logarítmica (300 = 0, 20 mil = 10). GPU integrada Intel depende da CPU "
              "e da RAM: em single-channel a Iris Xe opera como UHD, com cerca de metade do desempenho.", score_gpu),
    Criterion("ram", "RAM instalada", "Memória", ("RAM instalada (GB)",), 9,
              "4 GB = 1 · 8 GB = 4 · 16 GB = 8 · 24 GB = 9 · 32 GB ≈ 9,6.", score_ram),
    Criterion("ram_velocidade", "Velocidade da RAM", "Memória", ("Tipo RAM", "Velocidade RAM", "Dual-channel de fábrica"), 5,
              "Tipo (DDR4 = 6 · LPDDR4x = 7 · DDR5 = 8,5 · LPDDR5 = 9) menos 3,5 se vier em single-channel "
              "(ou 1,5 se o canal não for confirmado).", score_ram_speed),
    Criterion("ram_teto", "Teto de RAM (upgrade)", "Memória",
              ("RAM máxima oficial (GB)", "Expansão de RAM", "RAM soldada", "Slots RAM livres"), 6,
              "Maior RAM alcançável oficialmente: 8 GB = 1,5 · 16 GB = 5 · 24 GB = 7 · 32 GB = 8,5 · 64 GB = 10. "
              "RAM soldada sem expansão fica no que vem de fábrica.", score_ram_ceiling),
    Criterion("ssd", "SSD instalado", "Armazenamento", ("SSD instalado (GB)",), 5,
              "256 GB = 3,5 · 512 GB = 6,5 · 1 TB = 8,5 · 2 TB = 10.", score_ssd),
    Criterion("ssd_expansao", "Expansão de armazenamento", "Armazenamento",
              ("Slots M.2 livres", "Armazenamento máx./observação"), 3,
              "2 slots M.2 livres = 10 · 1 livre = 8,5 · baia 2,5\" = 5,5 · nenhum (troca do SSD) = 4.", score_storage_expansion),
    Criterion("tela_resolucao", "Resolução", "Tela", ("Resolução", "Tela (pol.)"), 5,
              "Pelas linhas verticais: 768 = 2 · 1080 = 7 · 1200 = 7,5 · 1440 = 8,5 · 1600 = 9 · 2160 = 10. "
              "A vantagem do formato 16:10 é contada só em Proporção.", score_resolution),
    Criterion("tela_proporcao", "Proporção da tela", "Tela", ("Proporção",), 4,
              "16:10 ou 3:2 = 9 · 4:3 = 8 · 16:9 = 6 (mais área vertical útil para documentos e web).", score_aspect),
    Criterion("tela_painel", "Tipo de painel", "Tela", ("Painel",), 7,
              "OLED = 10 · Mini-LED = 9,5 · IPS = 8 · IPS-level = 7,5 · WVA = 7 · VA = 6,5 · TN = 3. "
              "Se a ficha lista alternativas, vale a pior.", score_panel),
    Criterion("tela_brilho", "Brilho", "Tela", ("Brilho (nits)",), 6,
              "200 nits = 2 · 250 = 4,5 · 300 = 6,5 · 400 = 8,5 · 500 = 9,5. Com alternativas, vale o menor valor.", score_brightness),
    Criterion("tela_cores", "Cobertura de cores", "Tela", ("Cobertura de cores",), 4,
              "Convertida para equivalente sRGB (45% NTSC ≈ 62% sRGB): 62% = 4 · 75% = 6 · 100% = 9 · DCI-P3 = 10.", score_color),
    Criterion("tela_hz", "Taxa de atualização", "Tela", ("Taxa de atualização (Hz)",), 2,
              "60 Hz = 5 · 90 Hz = 7 · 120 Hz = 8,5 · 144 Hz = 9,2 · 165 Hz+ = 10.", score_refresh),
    Criterion("webcam", "Webcam", "Conectividade", ("Webcam",), 3,
              "720p = 5 · 1080p = 8,5 · 1440p/5 MP = 9,5 · 4K = 10.", score_webcam),
    Criterion("wifi", "Wi‑Fi", "Conectividade", ("Wi‑Fi",), 4,
              "Wi‑Fi 4 = 3 · Wi‑Fi 5 = 5,5 · Wi‑Fi 6 = 8 · 6E = 9 · Wi‑Fi 7 = 10; −0,7 para antena 1×1. "
              "Se a placa varia, vale a pior.", score_wifi),
    Criterion("usb_c", "Recursos do USB‑C", "Conectividade",
              ("USB‑C", "Thunderbolt / USB4", "USB‑C com vídeo", "USB‑C com carregamento"), 6,
              "Thunderbolt/USB4 = 10. Sem eles: 2 (dados) + 3 se tiver vídeo + 3,5 se carregar o notebook + 0,5 se for 10 Gbps. "
              "Recurso não confirmado não soma.", score_usb_c),
    Criterion("rj45", "Rede cabeada (RJ‑45)", "Conectividade", ("Ethernet RJ‑45",), 2,
              "Possui = 10 · não possui = 3 (dá para usar adaptador USB).", score_rj45),
    Criterion("bateria", "Bateria", "Mobilidade e construção", ("Bateria (Wh)",), 8,
              "40 Wh = 3,5 · 50 Wh = 5,5 · 60 Wh = 7,3 · 70 Wh = 8,5 · 80 Wh+ ≈ 9,4.", score_battery),
    Criterion("peso", "Peso", "Mobilidade e construção", ("Peso (kg)",), 7,
              "1,0 kg = 10 · 1,4 kg = 8,3 · 1,6 kg = 7 · 1,8 kg = 5,6 · 2,0 kg = 4,3 · 2,3 kg = 2,5.", score_weight),
    Criterion("construcao", "Construção", "Mobilidade e construção", ("Material / construção",), 4,
              "Metal = 8,5 · metal + plástico = 7 · plástico = 5,5. Se varia por submodelo, vale a pior hipótese.", score_build),
]

CRITERIA_BY_KEY = {c.key: c for c in CRITERIA}
CRITERION_KEYS = [c.key for c in CRITERIA]
CRITERIA_GROUPS: dict[str, list[str]] = {}
for _c in CRITERIA:
    CRITERIA_GROUPS.setdefault(_c.group, []).append(_c.key)

DEFAULT_WEIGHTS = {c.key: float(c.weight) for c in CRITERIA}


def _preset(**changes: float) -> dict[str, float]:
    unknown = set(changes) - set(DEFAULT_WEIGHTS)
    if unknown:
        raise KeyError(unknown)
    return {**DEFAULT_WEIGHTS, **{k: float(v) for k, v in changes.items()}}


PRESETS: dict[str, dict[str, float]] = {
    "Equilibrado": dict(DEFAULT_WEIGHTS),
    "Custo-benefício": _preset(preco=10, cpu=8, gpu=1, ram=8, ram_velocidade=3, ram_teto=4, ssd=4, ssd_expansao=2,
                               tela_resolucao=4, tela_proporcao=3, tela_painel=6, tela_brilho=5, tela_cores=2, tela_hz=1,
                               webcam=2, wifi=3, usb_c=4, rj45=1, bateria=6, peso=5, construcao=2),
    "Mobilidade": _preset(preco=6, bateria=10, peso=10, usb_c=8, construcao=6, tela_brilho=7, tela_hz=1, rj45=0,
                          ssd_expansao=1, wifi=6),
    "Trabalho / produtividade": _preset(preco=7, ram=10, ram_teto=8, tela_painel=8, tela_proporcao=7, tela_resolucao=6,
                                        webcam=6, wifi=6, usb_c=7, bateria=7, rj45=3),
    "Desempenho": _preset(preco=5, cpu=10, gpu=8, ram=10, ram_velocidade=8, ssd=7, tela_hz=6, bateria=5, peso=4),
    "Tela e multimídia": _preset(preco=5, tela_painel=10, tela_resolucao=9, tela_brilho=9, tela_cores=10, tela_hz=7, gpu=5),
    "Expansão / longevidade": _preset(preco=6, ram_teto=10, ssd_expansao=9, ram=8, construcao=7, usb_c=7),
}

DEFAULT_MISSING_SCORE = 4.0

DEFAULT_REQUIREMENTS = {
    "max_price": 0.0, "min_ram": 0, "min_ram_ceiling": 0, "min_ssd": 0, "max_weight": 0.0,
    "min_screen": 0.0, "max_screen": 0.0, "usb_c_charge": False, "rj45": False,
}


def clean_weights(weights: dict | None) -> dict[str, float]:
    out = dict(DEFAULT_WEIGHTS)
    for key, value in (weights or {}).items():
        if key in out:
            try:
                out[key] = float(min(10.0, max(0.0, float(value))))
            except (TypeError, ValueError):
                pass
    return out


# ---------------------------------------------------------------------------
# Itens: normalização e nomes curtos
# ---------------------------------------------------------------------------
def resolved_gpu(row: dict) -> str:
    dedicated = row.get("GPU dedicada", "N/D")
    if yes_no(dedicated) is None and not is_unknown(dedicated):
        return str(dedicated).strip()
    return str(row.get("GPU integrada", "N/D")).strip()


def normalize_item(row: dict, columns: list[str]) -> dict:
    item = {}
    for col in columns:
        value = row.get(col, "N/D")
        if value is None or (isinstance(value, float) and math.isnan(value)) or (isinstance(value, str) and not value.strip()):
            value = "N/D"
        item[col] = value
    if is_unknown(item.get("GPU")):
        item["GPU"] = resolved_gpu(item)
    return item


def short_names(rows: list[dict]) -> dict[str, str]:
    """Nome curto (marca + modelo, sem a configuração) para gráficos e colunas."""
    out = {}
    for row in rows:
        full = str(row.get(MODEL_COL, "")).strip()
        base = full.split(" — ")[0].strip()
        brand = str(row.get("Marca", "")).strip()
        label = base if (not brand or is_unknown(brand) or base.lower().startswith(brand.lower())) else f"{brand} {base}"
        out[full] = label
    counts = pd.Series(list(out.values())).value_counts()
    for full, label in list(out.items()):
        if counts.get(label, 0) > 1:
            out[full] = full
    return out


# ---------------------------------------------------------------------------
# Avaliação
# ---------------------------------------------------------------------------
@dataclass
class Evaluation:
    names: list[str]
    auto: pd.DataFrame          # nota automática (NaN = dado ausente)
    notes: pd.DataFrame         # observações sobre a nota
    final: pd.DataFrame         # nota usada no ranking
    manual: pd.DataFrame        # True quando há nota manual
    weights: pd.Series          # pesos de todos os critérios
    total: pd.Series            # 0–100
    technical: pd.Series        # 0–100 sem o critério de preço
    contrib: pd.DataFrame       # pontos (0–100) que cada critério soma ao total
    coverage: pd.Series         # % do peso ativo apoiado em dados conhecidos

    @property
    def active(self) -> list[str]:
        return [k for k in CRITERION_KEYS if self.weights.get(k, 0) > 0]

    def group_contrib(self) -> pd.DataFrame:
        groups = {k: CRITERIA_BY_KEY[k].group for k in self.contrib.columns}
        return self.contrib.T.groupby(groups, sort=False).sum().T


def _weighted_mean(scores: pd.DataFrame, weights: pd.Series) -> pd.Series:
    active = weights[weights > 0]
    if active.empty or scores.empty:
        return pd.Series(0.0, index=scores.index)
    return scores[active.index].mul(active, axis=1).sum(axis=1) / active.sum() * 10


def evaluate(rows: list[dict], weights: dict, overrides: dict | None = None,
             missing_score: float = DEFAULT_MISSING_SCORE) -> Evaluation:
    names = [str(r.get(MODEL_COL)) for r in rows]
    prices = [p for p in (number_field(r, PRICE_COL) for r in rows) if p and p > 0]
    ctx = {"min_price": min(prices) if prices else None}

    auto = pd.DataFrame(index=names, columns=CRITERION_KEYS, dtype=float)
    notes = pd.DataFrame("", index=names, columns=CRITERION_KEYS)
    for name, row in zip(names, rows):
        for c in CRITERIA:
            value, note = c.scorer(row, ctx)
            auto.loc[name, c.key] = float("nan") if value is None else round(min(10.0, max(0.0, value)), 2)
            notes.loc[name, c.key] = note

    final = auto.fillna(float(missing_score))
    manual = pd.DataFrame(False, index=names, columns=CRITERION_KEYS)
    for name, values in (overrides or {}).items():
        if name not in final.index:
            continue
        for key, value in values.items():
            if key in final.columns and value is not None:
                final.loc[name, key] = float(min(10.0, max(0.0, value)))
                manual.loc[name, key] = True

    w = pd.Series(clean_weights(weights), dtype=float)
    active = w[w > 0]
    total = _weighted_mean(final, w)
    tech_w = w.copy()
    tech_w["preco"] = 0.0
    technical = _weighted_mean(final, tech_w)
    if active.empty:
        contrib = pd.DataFrame(0.0, index=names, columns=CRITERION_KEYS)
        coverage = pd.Series(0.0, index=names)
    else:
        contrib = final.mul(w, axis=1) / active.sum() * 10
        known = auto.notna() | manual
        coverage = known[active.index].mul(active, axis=1).sum(axis=1) / active.sum() * 100

    return Evaluation(names, auto, notes, final, manual, w, total, technical, contrib, coverage)


def check_requirements(row: dict, req: dict) -> list[str]:
    """Lista de requisitos mínimos não atendidos (vazia = atende)."""
    fails = []
    req = {**DEFAULT_REQUIREMENTS, **(req or {})}

    def need(limit, value, ok, label, unit=""):
        if not limit:
            return
        if value is None:
            fails.append(f"{label} não informado")
        elif not ok(value, limit):
            fails.append(f"{label} {fmt_num(value, 2 if unit in {'kg', 'pol.'} else 0)}{(' ' + unit) if unit else ''}")

    price = number_field(row, PRICE_COL)
    if req["max_price"]:
        if not price:
            fails.append("preço não informado")
        elif price > req["max_price"]:
            fails.append(f"preço {fmt_brl(price)}")
    need(req["min_ram"], number_field(row, "RAM instalada (GB)"), lambda v, l: v >= l, "RAM", "GB")
    need(req["min_ram_ceiling"], ram_ceiling(row), lambda v, l: v >= l, "teto de RAM", "GB")
    need(req["min_ssd"], number_field(row, "SSD instalado (GB)"), lambda v, l: v >= l, "SSD", "GB")
    need(req["max_weight"], conservative_number(row.get("Peso (kg)"), higher_is_better=False), lambda v, l: v <= l, "peso", "kg")
    screen = number_field(row, "Tela (pol.)")
    need(req["min_screen"], screen, lambda v, l: v >= l, "tela", "pol.")
    need(req["max_screen"], screen, lambda v, l: v <= l, "tela", "pol.")
    if req["usb_c_charge"] and not _feature(row.get("USB‑C com carregamento"), ("power delivery",)):
        fails.append("sem carga via USB‑C confirmada")
    if req["rj45"] and yes_no(row.get("Ethernet RJ‑45")) is not True:
        fails.append("sem RJ‑45")
    return fails


def ranking_table(rows: list[dict], ev: Evaluation, req: dict) -> pd.DataFrame:
    by_name = {str(r.get(MODEL_COL)): r for r in rows}
    data = []
    for name in ev.names:
        fails = check_requirements(by_name[name], req)
        data.append({
            "Notebook": name,
            "Nota": round(float(ev.total[name]), 1),
            "Nota técnica": round(float(ev.technical[name]), 1),
            "Preço": number_field(by_name[name], PRICE_COL),
            "Atende": not fails,
            "Pendências": ", ".join(fails),
            "Dados conhecidos": round(float(ev.coverage[name])),
        })
    table = pd.DataFrame(data, columns=["Notebook", "Nota", "Nota técnica", "Preço", "Atende", "Pendências", "Dados conhecidos"])
    if table.empty:
        return table
    table["Preço"] = pd.to_numeric(table["Preço"], errors="coerce").astype("float64")
    table = table.sort_values(["Atende", "Nota", "Nota técnica"], ascending=[False, False, False]).reset_index(drop=True)
    table.insert(0, "Posição", range(1, len(table) + 1))
    return table


def preset_positions(rows: list[dict], presets: dict[str, dict], overrides: dict, missing_score: float, req: dict) -> pd.DataFrame:
    """Posição de cada notebook sob cada perfil de pesos (teste de robustez)."""
    out = {}
    for name, weights in presets.items():
        table = ranking_table(rows, evaluate(rows, weights, overrides, missing_score), req)
        out[name] = table.set_index("Notebook")["Posição"]
    return pd.DataFrame(out)


def strengths_weaknesses(ev: Evaluation, name: str, limit: int = 3) -> tuple[list[str], list[str]]:
    """Critérios em que o item se destaca (ou fica para trás) em relação à média, ponderados pelo peso."""
    if len(ev.names) < 2:
        return [], []
    diffs = []
    known = ev.auto.notna() | ev.manual
    for key in ev.active:
        if not known.loc[name, key]:
            continue  # dado ausente não vira ponto fraco nem forte
        mean = ev.final.loc[known[key], key].mean()
        delta = ev.final.loc[name, key] - mean
        if abs(delta) >= 1.0:
            diffs.append((delta * ev.weights[key], key))
    diffs.sort(reverse=True)
    good = [CRITERIA_BY_KEY[k].label for d, k in diffs if d > 0][:limit]
    bad = [CRITERIA_BY_KEY[k].label for d, k in sorted(diffs) if d < 0][:limit]
    return good, bad


SPEC_UNITS = {
    "ram": "{} GB", "ssd": "{} GB", "ram_teto": "até {} GB", "ssd_expansao": "{} slot(s) M.2 livre(s)",
    "tela_brilho": "{} nits", "tela_hz": "{} Hz", "bateria": "{} Wh", "peso": "{} kg",
}
COMPACT_FULL = {"usb_c", "ram_velocidade", "ram_teto"}


def _display(value) -> str:
    if isinstance(value, float):
        return str(int(value)) if value.is_integer() else str(value).replace(".", ",")
    return str(value)


def spec_text(row: dict, key: str, compact: bool = False) -> str:
    """Especificação que originou a nota. compact=True mostra só o essencial."""
    c = CRITERIA_BY_KEY[key]
    sources = c.sources if (not compact or key in COMPACT_FULL) else c.sources[:1]
    parts = []
    for col in sources:
        value = row.get(col, "N/D")
        if is_unknown(value):
            if col == c.sources[0]:
                parts.append("N/D")
            continue
        if col == PRICE_COL:
            parts.append(fmt_brl(number_field(row, col)))
        elif col == c.sources[0]:
            text = _display(value)
            parts.append(SPEC_UNITS[key].format(text) if key in SPEC_UNITS and numbers(value) and text.replace(",", "").isdigit() else text)
        else:
            parts.append(f"{col}: {_display(value)}")
    return " · ".join(parts)
