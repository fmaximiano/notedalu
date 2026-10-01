import json

import pytest

from notedalu import scoring as sc
from notedalu import storage
from notedalu.data import GROUPS, MODEL_COL, NOTEBOOKS, PRICE_COL, SPEC_COLUMNS


def item(**specs):
    base = {col: "N/D" for col in SPEC_COLUMNS}
    base.update({MODEL_COL: specs.pop("name", "Teste"), "Marca": "Marca"})
    base.update({k.replace("__", " "): v for k, v in specs.items()})
    return base


def rows():
    return [sc.normalize_item(r, SPEC_COLUMNS) for r in NOTEBOOKS]


# --- leitura de dados -------------------------------------------------------
@pytest.mark.parametrize("text, money, expected", [
    ("3.499,90", True, 3499.90), ("3499.90", True, 3499.90), ("R$ 3.499", True, 3499.0),
    ("3,499.90", True, 3499.90), ("1,69", False, 1.69), ("1.69", False, 1.69), ("abc", False, None), ("", True, None),
])
def test_parse_number(text, money, expected):
    assert sc.parse_number(text, money=money) == (pytest.approx(expected) if expected is not None else None)


def test_unknown_is_not_no():
    for value in ("Não informado", "Não confirmado", "N/D", "Não determinável (família…)", "", None):
        assert sc.is_unknown(value)
        assert sc.yes_no(value) is None
    assert sc.yes_no("Não") is False
    assert sc.yes_no("Sim, Gigabit") is True


# --- critérios ---------------------------------------------------------------
def score(key, **specs):
    return sc.CRITERIA_BY_KEY[key].scorer(item(**specs), {})[0]


def test_wifi_handles_non_breaking_hyphen_and_alternatives():
    assert score("wifi", **{"Wi‑Fi": "Wi‑Fi 7 (802.11be)"}) == 10
    assert score("wifi", **{"Wi‑Fi": "Wi‑Fi 5 ou Wi‑Fi 6 conforme placa"}) == score("wifi", **{"Wi‑Fi": "Wi-Fi 5"})
    assert score("wifi", **{"Wi‑Fi": "Wi‑Fi 5 (802.11ac) 1×1"}) < score("wifi", **{"Wi‑Fi": "Wi‑Fi 5 2x2"})


def test_unconfirmed_usb_c_video_is_not_penalized_as_no():
    unknown = score("usb_c", **{"USB‑C": "1× USB-C", "USB‑C com vídeo": "Não confirmado", "USB‑C com carregamento": "Sim"})
    no = score("usb_c", **{"USB‑C": "1× USB-C", "USB‑C com vídeo": "Não", "USB‑C com carregamento": "Não"})
    assert unknown > no
    assert score("usb_c", **{"Thunderbolt / USB4": "2× Thunderbolt 4"}) == 10


def test_alternatives_use_worst_case():
    assert score("tela_brilho", **{"Brilho (nits)": "220 ou 250"}) == score("tela_brilho", **{"Brilho (nits)": 220})
    assert score("tela_painel", Painel="TN 220 nits OU IPS 250 nits") == score("tela_painel", Painel="TN")


def test_color_gamut_is_converted_to_common_space():
    assert score("tela_cores", **{"Cobertura de cores": "45% NTSC"}) == pytest.approx(
        score("tela_cores", **{"Cobertura de cores": "62,5% sRGB"}), abs=0.1)


def test_resolution_does_not_double_count_aspect_ratio():
    fhd = score("tela_resolucao", **{"Resolução": "1920×1080"})
    wuxga = score("tela_resolucao", **{"Resolução": "1920×1200"})
    assert 0 < wuxga - fhd <= 0.5
    assert score("tela_proporcao", **{"Proporção": "16:10"}) > score("tela_proporcao", **{"Proporção": "16:9"})


def test_absolute_scales_keep_small_differences_small():
    assert abs(score("peso", **{"Peso (kg)": 1.55}) - score("peso", **{"Peso (kg)": 1.63})) < 1
    assert abs(score("bateria", **{"Bateria (Wh)": 53}) - score("bateria", **{"Bateria (Wh)": 54})) < 0.5


def test_price_is_relative_to_cheapest():
    assert sc.score_price(item(**{PRICE_COL: 3000}), {"min_price": 3000})[0] == 10
    assert sc.score_price(item(**{PRICE_COL: 3600}), {"min_price": 3000})[0] == pytest.approx(6.94, abs=0.01)
    assert sc.score_price(item(), {"min_price": 3000})[0] is None


def test_single_channel_halves_integrated_graphics():
    dual = item(CPU="Intel Core i5-1335U", GPU="Intel Iris Xe Graphics", **{"Dual-channel de fábrica": "Sim"})
    single = item(CPU="Intel Core i5-1335U", GPU="Intel Iris Xe Graphics", **{"Dual-channel de fábrica": "Não"})
    assert sc.score_gpu(single, {})[0] < sc.score_gpu(dual, {})[0] - 1


def test_cpu_scores_follow_benchmarks():
    names = ["Intel Core i7-10510U", "Intel Core i5-1334U", "Intel Core 5 120U"]
    values = [sc.score_cpu(item(CPU=n), {})[0] for n in names]
    assert values == sorted(values)
    assert sc.score_cpu(item(CPU="AMD Ryzen 7 7840HS"), {})[0] > values[-1]  # estimativa pelo nome
    assert sc.score_cpu(item(CPU="CPU desconhecida"), {})[0] is None


def test_ram_ceiling():
    soldered = item(**{"RAM instalada (GB)": 8, "RAM máxima oficial (GB)": 8, "Expansão de RAM": "Não"})
    upgradable = item(**{"RAM instalada (GB)": 8, "RAM máxima oficial (GB)": 32, "Expansão de RAM": "Sim; até 32GB"})
    assert sc.ram_ceiling(soldered) == 8 and sc.ram_ceiling(upgradable) == 32


# --- avaliação e ranking -------------------------------------------------------
def test_dataset_integrity():
    names = [r[MODEL_COL] for r in NOTEBOOKS]
    assert len(names) == len(set(names))
    assert set(NOTEBOOKS[0]) == set(SPEC_COLUMNS) == {c for cols in GROUPS.values() for c in cols}
    for c in sc.CRITERIA:
        assert all(src in SPEC_COLUMNS for src in c.sources), c.key
    for preset in sc.PRESETS.values():
        assert set(preset) == set(sc.CRITERION_KEYS)


def test_builtin_items_have_no_unrecognized_specs():
    ev = sc.evaluate(rows(), sc.DEFAULT_WEIGHTS)
    # Fora preço, brilho e gamut (de fato ausentes nas fichas), tudo deve ser reconhecido.
    missing = {k for k in sc.CRITERION_KEYS if ev.auto[k].isna().any()}
    assert missing <= {"preco", "tela_brilho", "tela_cores"}


def test_adding_item_does_not_change_other_scores():
    base = rows()
    extra = dict(base[0], **{MODEL_COL: "Novo — 64GB", "RAM instalada (GB)": 64, "Peso (kg)": 0.9})
    before = sc.evaluate(base, sc.DEFAULT_WEIGHTS).final.drop(columns="preco")
    after = sc.evaluate(base + [extra], sc.DEFAULT_WEIGHTS).final.drop(columns="preco").loc[before.index]
    assert before.equals(after)


def test_overrides_and_coverage():
    data = rows()
    name = data[0][MODEL_COL]
    ev = sc.evaluate(data, sc.DEFAULT_WEIGHTS, {name: {"tela_brilho": 9.0}}, missing_score=4)
    assert ev.final.loc[name, "tela_brilho"] == 9 and ev.manual.loc[name, "tela_brilho"]
    other = data[1][MODEL_COL]
    assert ev.coverage[name] > sc.evaluate(data, sc.DEFAULT_WEIGHTS).coverage[name]
    assert 0 <= ev.total[other] <= 100


def test_requirements_and_ranking_order():
    data = rows()
    req = dict(sc.DEFAULT_REQUIREMENTS, min_ram=16, usb_c_charge=True)
    table = sc.ranking_table(data, sc.evaluate(data, sc.DEFAULT_WEIGHTS), req)
    assert table["Atende"].tolist() == sorted(table["Atende"].tolist(), reverse=True)
    failing = table[~table["Atende"]]
    assert all("RAM" in p or "USB" in p for p in failing["Pendências"])
    assert "preço não informado" in sc.check_requirements(data[0], {"max_price": 4000})


def test_short_names_are_unique():
    names = sc.short_names(rows())
    assert len(set(names.values())) == len(names)


# --- persistência -----------------------------------------------------------------
def test_backup_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("NOTEDALU_DATA_DIR", str(tmp_path))
    state = {"inventory": rows(), "weights": sc.DEFAULT_WEIGHTS, "custom_presets": {}, "requirements": {},
             "overrides": {}, "missing_score": 4.0}
    assert storage.save(state) > 0
    loaded, mtime = storage.load()
    assert loaded["inventory"][0][MODEL_COL] == state["inventory"][0][MODEL_COL] and mtime > 0


def test_legacy_backup_and_invalid_files():
    assert storage.parse_backup([{"Marca": "X"}]) == {"inventory": [{"Marca": "X"}]}
    with pytest.raises(ValueError):
        storage.parse_backup({"foo": 1})
    with pytest.raises(ValueError):
        storage.parse_backup(json.loads("[]"))


def test_persistence_can_be_disabled(monkeypatch):
    monkeypatch.setenv("NOTEDALU_PERSIST", "0")
    assert storage.data_file() is None and storage.save({"inventory": []}) == 0.0
