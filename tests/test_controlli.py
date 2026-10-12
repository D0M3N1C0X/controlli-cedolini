"""I controlli fanno quello che dicono: trovano gli errori inseriti, non segnalano i casi legittimi,
rispettano le regole del contratto, e non vedono l'errore coerente dichiarato come limite."""
from datetime import date

import pandas as pd
import pytest

import codice_fiscale
import config as C
import regole as R
import robustezza


def test_tabella_ccnl_coerente():
    t = R.tabella()
    assert len(t) == 8
    somma = (t["paga_base"] + t["contingenza"] + t["altri_elementi"]).round(2)
    assert (somma == t["minimo_2025_11"]).all()
    # le tranche crescono, e il 4° livello è quello noto: 1.781,68 € da novembre 2025, +35 € a novembre 2026
    assert (t["minimo_2025_03"] < t["minimo_2025_11"]).all() and (t["minimo_2025_11"] < t["minimo_2026_11"]).all()
    assert t.loc["4", "minimo_2025_11"] == 1781.68
    assert t.loc["4", "minimo_2026_11"] - t.loc["4", "minimo_2025_11"] == pytest.approx(35)
    assert t.loc["4", "scatto"] == 20.66


@pytest.mark.parametrize("assunzione, mese, attesi", [
    (date(2023, 8, 10), "2026-08", 0),     # il triennio si compie ad agosto: niente ancora
    (date(2023, 8, 10), "2026-09", 1),     # dal mese dopo
    (date(2023, 8, 31), "2026-09", 1),
    (date(1990, 1, 1), "2026-09", 10),     # massimo 10
    (date(2026, 2, 8), "2026-09", 0),
])
def test_scatti_maturati(assunzione, mese, attesi):
    assert R.scatti_maturati(assunzione, mese) == attesi


@pytest.mark.parametrize("assunzione, mese, r13, r14", [
    (date(2015, 5, 4), "2026-09", 9, 3),      # in forza da prima del periodo: tutti i mesi
    (date(2026, 2, 18), "2026-09", 7, 3),     # febbraio con 11 giorni di servizio non matura
    (date(2026, 3, 17), "2026-09", 7, 3),     # marzo con 15 giorni esatti matura
    (date(2026, 9, 1), "2026-09", 1, 1),      # assunto nel mese: un dodicesimo per ciascuna
    (date(2026, 7, 20), "2026-09", 2, 2),     # luglio con 12 giorni non matura, né per la 13ª né per la 14ª
    (date(2015, 5, 4), "2026-06", 6, 12),     # a giugno la quattordicesima ha l'anno intero, da luglio 2025
    (date(2025, 12, 10), "2026-02", 2, 3),    # la 13ª riparte a gennaio; la 14ª conta dicembre (22 giorni)
])
def test_ratei_tredicesima_e_quattordicesima(assunzione, mese, r13, r14):
    assert (R.ratei_13(assunzione, mese), R.ratei_14(assunzione, mese)) == (r13, r14)


def test_arrotondamento_come_excel():
    assert R.centesimi(34.245) == 34.25
    assert R.centesimi(22.83 * 2 * 0.75) == 34.25
    assert R.centesimi(2.675) == 2.68


def test_contributi_su_imponibile_arrotondato_all_euro():
    # F10: 1.779,00 x 9,19% = 163,49 (esempio ODCEC Torino); 1.549,91 si arrotonda a 1.550
    assert R.euro(1549.5) == 1550 and R.euro(1549.49) == 1549
    assert R.contributi(1779.0) == 163.49
    assert R.contributi(1549.91) == 142.45      # sul lordo non arrotondato sarebbe 142,44


def test_codice_fiscale():
    assert codice_fiscale.valido("RSSMRA85T10A562S")
    assert not codice_fiscale.valido("RSSMRA85T10A562T")
    assert not codice_fiscale.valido("RSSMRA85T10A562")


def test_trova_tutti_gli_errori_inseriti_senza_falsi_allarmi(out):
    v = out["valutazione"]
    assert (v["mancati"] == 0).all() and (v["falsi_allarmi"] == 0).all()
    assert v["inseriti"].sum() == len(pd.read_csv(C.ERRORI))


def test_casi_legittimi_non_segnalati(out):
    m, an = out["mese"], out["anomalie"]
    legittimi = m.loc[m["evento"] != "", "matricola"]
    assert len(legittimi) >= 8
    assert an[an["matricola"].isin(legittimi)].empty


def test_novembre(out):
    n = out["novembre"]
    assert (n["aumento"] > 0).all()
    assert (n["assorbito"] <= n["superminimo"] + 1e-9).all() and (n["assorbito"] <= n["aumento"] + 1e-9).all()
    assert (n.loc[~n["superminimo_assorbibile"], "assorbito"] == 0).all()
    assert (n["da_pagare"] - (n["aumento"] - n["assorbito"])).abs().max() < 1e-9


def test_alterazioni_sopra_la_tolleranza_sempre_trovate():
    r = robustezza.run(seed=3, prove=150)
    assert r[r["ampiezza"] > C.TOLLERANZA]["trovato"].all()


def test_limite_dichiarato_errore_coerente():
    c = robustezza.errore_coerente()
    assert c["segnalazioni"] == [] and c["netto_pagato"] < c["netto_giusto"]


def test_le_regole_battono_il_rilevatore_statistico():
    import statistica
    v = statistica.valutazione()
    regole = v[v["metodo"].str.startswith("Regole")].iloc[0]
    stat = v[v["metodo"].str.startswith("Statistico")]
    assert regole["richiamo"] == 1.0 and regole["falsi_allarmi"] == 0
    assert (stat["richiamo"] < 0.5).all() and (stat["falsi_allarmi"] > 0).all()
    pt = statistica.per_tipo().set_index("tipo")
    assert pt.loc["inps", "trovati_statistico"] == pt.loc["inps", "errori"]        # vede i rapporti
    assert pt.loc["minimo", "trovati_statistico"] == 0                             # non vede il contratto
