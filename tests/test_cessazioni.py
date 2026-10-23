"""C12-C14: mensilità aggiuntive, ferie non godute e preavviso alla cessazione. Gli stessi casi limite sono in
tests/js/check_controlli.mjs, perché lo strumento nel browser dia gli stessi numeri."""
from datetime import date

import pandas as pd
import pytest

import config as C
import controlli
import regole as R


@pytest.mark.parametrize("assunzione, cessazione, n13, n14", [
    (date(2015, 5, 4), date(2026, 9, 30), 9, 3),
    (date(2015, 5, 4), date(2026, 9, 14), 8, 2),       # ultimo mese con 14 giorni: non conta
    (date(2015, 5, 4), date(2026, 9, 15), 9, 3),       # con 15 sì
    (date(2026, 3, 18), date(2026, 9, 30), 6, 3),      # primo mese con 14 giorni
    (date(2026, 3, 17), date(2026, 9, 30), 7, 3),
    (date(2026, 9, 10), date(2026, 9, 24), 1, 1),      # entrato e uscito nello stesso mese, 15 giorni
    (date(2026, 9, 10), date(2026, 9, 23), 0, 0),
    (date(2020, 1, 1), date(2026, 3, 31), 3, 9),       # quattordicesima da luglio dell'anno prima
    (date(2026, 10, 1), date(2026, 9, 30), 0, 0),
])
def test_dodicesimi_alla_cessazione(assunzione, cessazione, n13, n14):
    assert R.dodicesimi_alla_cessazione(assunzione, cessazione, R.inizio_13(cessazione)) == n13
    assert R.dodicesimi_alla_cessazione(assunzione, cessazione, R.inizio_14(cessazione)) == n14


@pytest.mark.parametrize("tipo, livello, assunzione, cessazione, giorni", [
    ("dimissioni", "4", date(2021, 10, 1), date(2026, 9, 30), 15),      # 4 anni compiuti
    ("dimissioni", "4", date(2021, 9, 30), date(2026, 9, 30), 20),      # 5 anni: dal 6° anno
    ("licenziamento", "Quadri", date(2016, 9, 30), date(2026, 9, 30), 120),
    ("licenziamento", "Quadri", date(2016, 10, 1), date(2026, 9, 30), 90),
    ("licenziamento", "7", date(2000, 1, 1), date(2026, 9, 30), 20),
])
def test_preavviso_minimo(tipo, livello, assunzione, cessazione, giorni):
    assert R.preavviso_minimo(tipo, livello, assunzione, cessazione) == giorni


def test_importi():
    assert R.mensilita_aggiuntiva(2000.0, 9) == 1500.0
    assert R.ferie_non_godute(2080.0, 5.5) == 440.0                     # 80 € al giorno
    assert C.DIVISORE_GIORNALIERO == 26


def _riga(**voci) -> pd.Series:
    base = {"data_assunzione": "2015-05-04", "tabellare": 1800.0, "scatti": 100.0, "superminimo": 0.0,
            "livello": "4", "ferie_residuo": 5.0, "data_cessazione": "2026-09-30", "tipo_cessazione": "dimissioni",
            "preavviso_giorni": "30", "tredicesima": "", "quattordicesima": "", "ferie_liquidate": ""}
    return pd.Series({**base, **voci})


def _segnalazioni(r: pd.Series) -> list:
    out = []
    controlli._cessazione(r, lambda i, codice, atteso, trovato: out.append((codice, atteso, trovato)), 0)
    return out


def test_cessazione_corretta_non_segnalata():
    r = _riga(tredicesima="1425.00", quattordicesima="475.00", ferie_liquidate="365.38")
    assert _segnalazioni(r) == []


def test_ogni_errore_di_cessazione_trovato():
    assert _segnalazioni(_riga(quattordicesima="1425.00")) == [("C12", 475.0, 1425.0)]
    assert _segnalazioni(_riga(ferie_liquidate="316.67")) == [("C13", 365.38, 316.67)]
    assert _segnalazioni(_riga(preavviso_giorni="15")) == [("C14", 30.0, 15.0)]


def test_colonne_vuote_o_tipo_sconosciuto_non_si_applicano():
    assert _segnalazioni(_riga(preavviso_giorni="")) == []
    assert _segnalazioni(_riga(tipo_cessazione="giusta causa", preavviso_giorni="0")) == []
    assert _segnalazioni(_riga(data_cessazione="", tipo_cessazione="", preavviso_giorni="")) == []


def test_tredicesima_di_dicembre_con_i_ratei(monkeypatch):
    """Senza cessazione, la mensilità pagata si confronta con i dodicesimi maturati al mese del cedolino."""
    monkeypatch.setattr(C, "MESE", "2026-12")
    r = _riga(data_cessazione="", tipo_cessazione="", preavviso_giorni="", tredicesima="1900.00")
    assert _segnalazioni(r) == []
    assert _segnalazioni(r.copy().set_axis(r.index).replace({"1900.00": "1583.33"})) == [("C12", 1900.0, 1583.33)]


def test_chi_lascia_prima_di_novembre_non_riceve_la_tranche(out):
    usciti = set(out["mese"].loc[out["mese"]["data_cessazione"] != "", "matricola"])
    assert len(usciti) == 5
    assert usciti.isdisjoint(out["novembre"]["matricola"])
