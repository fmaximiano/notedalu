"""Testes de fumaça da interface: cada página roda sem exceção."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")

LEGACY_PAGES = ["inicio", "comparativo", "pesos", "notas", "ranking", "resumo", "itens"]


@pytest.fixture(autouse=True)
def no_disk(monkeypatch):
    monkeypatch.setenv("NOTEDALU_PERSIST", "0")


def run_page(page: str) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=90)
    at.query_params["page"] = page
    return at.run()


@pytest.mark.parametrize("page", LEGACY_PAGES)
def test_pages_render(page):
    at = run_page(page)
    assert not at.exception, [e.value for e in at.exception]


def test_requirement_moves_items_to_the_end():
    at = run_page("ranking")
    at.number_input(key="req_min_ram").set_value(16).run()
    assert not at.exception
    assert at.session_state.requirements["min_ram"] == 16


def test_weight_slider_updates_weights():
    at = run_page("pesos")
    at.slider(key="w_preco").set_value(2).run()
    assert not at.exception
    assert at.session_state.weights["preco"] == 2


@pytest.mark.parametrize("scenario", ["nenhum_selecionado", "cadastro_vazio", "ninguem_atende"])
@pytest.mark.parametrize("page", ["inicio", "comparativo", "notas", "ranking", "resumo"])
def test_edge_cases_render(scenario, page):
    at = AppTest.from_file(APP, default_timeout=90).run()
    names = {r["Modelo / configuração"] for r in at.session_state.inventory}
    if scenario == "nenhum_selecionado":
        at.session_state.excluded = names
    elif scenario == "cadastro_vazio":
        at.session_state.inventory = []
    else:
        at.session_state.requirements = dict(at.session_state.requirements, min_ram=64, max_price=100.0)
    at.query_params["page"] = page
    at.run()
    assert not at.exception, [e.value for e in at.exception]
