"""Le fonti al mese chiuso (fonti.py): ogni parametro con una data copre il mese controllato e l'anno della
simulazione, e gli indici FOI sono quelli della tavola ISTAT."""
import pytest

import anno
import config as C
import fonti
import regole as R


def test_ogni_parametro_copre_il_mese_controllato():
    assert fonti.copertura(C.MESE) == [] and fonti.copertura(C.MESE_PRECEDENTE) == []


@pytest.mark.parametrize("mese", anno.MESI)
def test_i_parametri_annuali_coprono_tutto_il_2026(mese):
    """Il FOI di novembre e dicembre non esiste ancora: C19 in quei mesi non controlla (coefficiente_tfr dà None)."""
    mancano = [x.fonte for x in fonti.copertura(mese)]
    if mese <= fonti.ULTIMO_MESE_CHIUSO:
        assert mancano == []
    else:
        assert mancano == ["F20"]


def test_foi_uguale_alla_tavola_istat():
    assert fonti.foi_istat() == C.FOI_MESI
    assert max(C.FOI_MESI) == fonti.ULTIMO_MESE_CHIUSO


def test_dicembre_2025_e_raccordo_dalla_tavola():
    import csv
    with open(fonti.FOI_ISTAT, encoding="utf-8") as f:
        dic = {r["mese"]: float(r["indice"]) for r in csv.DictReader(f)}["2025-12"]
    assert dic == C.FOI_DICEMBRE and C.FOI_RACCORDO == 1.214


@pytest.mark.parametrize("giorno, coefficiente", [
    ("2026-09-15", 4.285617),       # settembre: pubblicato (F20)
    ("2026-10-20", 5.234938),       # ottobre: 1,5 x 10/12 + 75% di (105,4 x 1,214 / 121,5 - 1)
    ("2026-11-14", 5.234938),       # fino al 14 novembre vale ottobre
])
def test_coefficiente_tfr_al_mese_chiuso(giorno, coefficiente):
    from datetime import date
    assert R.coefficiente_tfr(date.fromisoformat(giorno)) == pytest.approx(coefficiente, abs=1e-6)


def test_dopo_l_ultimo_indice_il_tfr_non_si_controlla():
    from datetime import date
    assert R.coefficiente_tfr(date(2026, 11, 20)) is None


def test_prima_scadenza_annuale():
    s = fonti.prima_scadenza()
    assert s.al == "2026-12" and s.fonte != "F20"
