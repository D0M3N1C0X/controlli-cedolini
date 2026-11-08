"""IRPEF 2026: le regole lette nei testi (F24-F29) danno i numeri che si calcolano a mano, e il conguaglio pareggia
le ritenute dei mesi."""
import pytest

import config as C
import regole as R


def test_scaglioni_2026_con_il_33():
    # 28.000 al 23%, 22.000 al 33%, il resto al 43%
    assert R.imposta_lorda(60000) == pytest.approx(28000 * 0.23 + 22000 * 0.33 + 10000 * 0.43)
    assert R.imposta_lorda(28000) == pytest.approx(6440)
    # ragguagliati al mese: lo stesso reddito diviso dodici dà un dodicesimo dell'imposta
    assert R.imposta_lorda(5000, 12) == pytest.approx(R.imposta_lorda(60000) / 12)
    # la tabella del 2025 resta solo per gli errori inseriti: 2 punti in più sul secondo scaglione
    assert R.imposta_lorda(50000, scaglioni=C.SCAGLIONI_IRPEF_2025) - R.imposta_lorda(50000) == pytest.approx(440)


@pytest.mark.parametrize("reddito, attesa", [
    (12000, 1955), (15000, 1955), (20000, 1910 + 1190 * 0.6154), (26000, 1910 + 1190 * 0.1538 + 65),
    (28000, 1910 + 65), (36000, 1910 * 0.6364), (50000, 0), (60000, 0)])
def test_detrazione_lavoro_art_13(reddito, attesa):
    assert R.detrazione_lavoro(reddito) == pytest.approx(attesa)


def test_cuneo_somma_e_detrazione():
    assert [R.percentuale_cuneo(x) for x in (8000, 8500, 12000, 19000)] == [0.071, 0.071, 0.053, 0.048]
    assert R.detrazione_cuneo(20000) == 0 and R.detrazione_cuneo(25000) == 1000
    assert R.detrazione_cuneo(36000) == pytest.approx(500) and R.detrazione_cuneo(40000) == 0


def test_trattamento_integrativo():
    # sotto 15.000 spetta se l'imposta supera la detrazione meno 75 €; rapportato al periodo
    assert R.trattamento_integrativo(14000, 3220, 1955, 1.0) == 1200
    assert R.trattamento_integrativo(14000, 3220, 1955, 0.5) == 600
    assert R.trattamento_integrativo(7000, 1610, 1955, 1.0) == 0          # incapiente: l'imposta non basta
    assert R.trattamento_integrativo(30000, 7100, 1955, 1.0) == 0


def test_mese_e_conguaglio_pareggiano_su_un_anno_intero():
    """Un anno intero di mesi uguali, senza mensilità aggiuntive tassate a parte: il conguaglio vale (quasi) zero."""
    for imponibile in (900, 1500, 1900, 2600, 4200):
        mese = R.irpef_mese(imponibile, mensilita=12)
        prec = {k: R.centesimi(mese[k] * 11) for k in mese}
        c = R.conguaglio_cessazione(imponibile * 12, C.GIORNI_ANNO, prec["irpef"], prec["bonus_cuneo"],
                                    prec["trattamento_integrativo"])
        for k in ("irpef", "bonus_cuneo", "trattamento_integrativo"):
            assert c[k] == pytest.approx(mese[k], abs=0.12), (imponibile, k)


def test_conguaglio_rapporta_le_detrazioni_ai_giorni():
    pieno = R.conguaglio_cessazione(20000, 273, 0, 0, 0, rapporta=False)
    giorni = R.conguaglio_cessazione(20000, 273, 0, 0, 0)
    assert giorni["imposta_netta"] > pieno["imposta_netta"]
    assert giorni["imposta_netta"] - pieno["imposta_netta"] == pytest.approx(
        (R.detrazione_lavoro(20000)) * (1 - 273 / 365), abs=0.02)


def test_errori_irpef_inseriti_trovati(out):
    v = out["valutazione"].set_index("controllo")
    for codice in ("C20", "C21"):
        assert v.loc[codice, "inseriti"] > 0 and v.loc[codice, "trovati"] == v.loc[codice, "inseriti"]
        assert v.loc[codice, "falsi_allarmi"] == 0
