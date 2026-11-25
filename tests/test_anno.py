"""L'anno intero e gli errori di configurazione (anno.py): l'anno pulito non dà falsi allarmi, un errore nella
regola si vede dal primo mese e ogni mese, un errore nell'anagrafica una volta o mai."""
import pandas as pd
import pytest

import anno
import config as C
import regole as R


@pytest.fixture(scope="module")
def a():
    return anno.run()


def test_tranche_in_vigore_a_settembre_e_quella_dei_controlli():
    for k in C.CCNL:
        assert R.colonna_in_vigore(k, C.MESE) == R.regola(k)["minimo"]
        assert R.colonna_in_vigore(k, C.MESE_PRECEDENTE) == R.regola(k)["minimo"]


@pytest.mark.parametrize("ccnl, mese, colonna", [
    ("terziario", "2026-10", "minimo_2025_11"), ("terziario", "2026-11", "minimo_2026_11"),
    ("turismo", "2026-05", "totale_2025_06"), ("turismo", "2026-06", "totale_2026_06"),
    ("metalmeccanico", "2026-05", "minimo_2025_06"), ("metalmeccanico", "2026-06", "minimo_2026_06"),
    ("logistica", "2026-12", "totale_2026_01"),
])
def test_tranche_nel_mese(ccnl, mese, colonna):
    assert R.colonna_in_vigore(ccnl, mese) == colonna


def test_anno_pulito_senza_falsi_allarmi(a):
    assert a["segnalazioni"].empty
    assert list(a["mesi"]["mese"]) == anno.MESI
    assert (a["mesi"]["segnalazioni"] == 0).all()
    # la quattordicesima solo dove il CCNL la prevede, la tredicesima per tutti
    ex = a["extra"]
    assert set(ex.loc[ex["voce"] == "quattordicesima", "cliente"]) == {"A", "B", "C", "E", "F"}
    assert (ex["voce"] == "tredicesima").sum() == (a["cedolini"]["mese"] == "2026-12").sum()


def test_eventi_non_registrati_li_vede_c10(a):
    s = a["senza_evento"]
    assert set(s["matricola"]) == set(a["eventi"])
    assert (s["controllo"] == "C10").sum() == len(a["eventi"])


def test_errori_di_regola_dal_primo_mese_e_ogni_mese(a):
    e = a["errori"]
    r = e[e["tipo"] == "regola"]
    assert len(r) == 6
    assert (r["primo_segnalato"] == r["primo_esposto"]).all()
    assert (r["falsi_allarmi"] == 0).all()
    k = e.set_index("codice")
    assert k.loc["K1", "mesi_segnalati"] == 7                     # da giugno a dicembre
    assert k.loc["K2", "segnalati"] == k.loc["K2", "esposti"] == 240
    assert set(k.loc["K3", "controlli"].split(", ")) == {"C04", "C11", "C20"}
    assert k.loc["K3", "mensilita_aggiuntive"] < 0                # la quattordicesima non pagata


def test_errori_di_anagrafica_una_volta_o_mai(a):
    k = a["errori"].set_index("codice")
    assert k.loc["K7", "segnalati"] == 0 and k.loc["K7", "esposti"] > 12
    for c in ("K8", "K9"):
        assert k.loc[c, "segnalati"] == 1 and k.loc[c, "controlli"] == "C10"
        assert k.loc[c, "primo_segnalato"] == k.loc[c, "dal"]
        assert k.loc[c, "falsi_allarmi"] == 0


def test_csv_del_rapporto_aggiornati(a):
    salvato = pd.read_csv(C.REPORT / "anno_errori.csv", keep_default_na=False)
    assert list(salvato["codice"]) == list(a["errori"]["codice"])
    assert list(salvato["segnalati"]) == list(a["errori"]["segnalati"])
