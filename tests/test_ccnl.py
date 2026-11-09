"""Le regole che cambiano da un CCNL all'altro (v2.2): ogni contratto applica le sue, sui casi limite."""
from datetime import date

import pytest

import config as C
import controlli
import regole as R

M, T, L = "metalmeccanico", "turismo", "logistica"


def test_ogni_cliente_ha_un_ccnl_con_tabella_e_regole():
    for cliente, info in C.CLIENTI.items():
        g = C.CCNL[info["ccnl"]]
        t = R.tabella(info["ccnl"])
        assert {g["minimo"], g["minimo_prec"], g["minimo_prossimo"], "scatto"} <= set(t.columns), cliente
        assert set(g["preavviso"]["dimissioni"]) == set(t.index) == set(g["preavviso"]["licenziamento"])
        assert set(g["livelli"]) <= set(t.index)


@pytest.mark.parametrize("ccnl,attesi", [("terziario", 1), (M, 2), (L, 2), (T, 1)])
def test_scatti_con_il_periodo_del_ccnl(ccnl, attesi):
    # assunto il 10 maggio 2022: a settembre 2026 un triennio, due bienni, un quadriennio
    assert R.scatti_maturati(date(2022, 5, 10), "2026-09", ccnl) == attesi


def test_il_mese_di_assunzione_con_15_giorni():
    # 16 aprile: 15 giorni di servizio. Conta nel Terziario e nel Turismo, non dove servono più di 15
    assert R.ratei_13(date(2026, 4, 16), "2026-09") == 6
    assert R.ratei_13(date(2026, 4, 16), "2026-09", T) == 6
    assert R.ratei_13(date(2026, 4, 16), "2026-09", M) == 5
    assert R.ratei_13(date(2026, 4, 16), "2026-09", L) == 5


def test_metalmeccanico_senza_quattordicesima():
    assert R.ratei_14(date(2015, 5, 4), "2026-09", M) == 0
    assert R.ratei_al(date(2015, 5, 4), "2026-09", date(2026, 9, 30), M) == (9, 0)


def test_turismo_somma_le_frazioni_di_mese():
    # 12 giorni a luglio e 10 a settembre: separati non contano, sommati (22) fanno un dodicesimo
    args = (date(2026, 7, 20), date(2026, 9, 10), date(2026, 1, 1))
    assert R.dodicesimi_alla_cessazione(*args) == 1
    assert R.dodicesimi_alla_cessazione(*args, T) == 2
    # 33 giorni: un dodicesimo per 30, il resto di 3 non conta
    assert R.dodicesimi_alla_cessazione(date(2026, 7, 10), date(2026, 9, 11), date(2026, 1, 1), T) == 2


def test_turismo_quattordicesima_e_tfr_senza_scatti():
    assert R.base_quattordicesima(2000.0, 100.0, T) == 1900.0
    assert R.base_quattordicesima(2000.0, 100.0) == 2000.0
    assert R.quota_tfr(2000.0, 100.0, T) == R.centesimi((2000 * 14 - 100) / 13.5 / 12)
    assert R.quota_tfr(2000.0, 100.0, M) == R.centesimi(2000 * 13 / 13.5 / 12)


@pytest.mark.parametrize("anni,giorni", [(9, 24), (10, 25), (17, 25), (18, 30)])
def test_ferie_del_metalmeccanico_con_l_anzianita(anni, giorni):
    assert R.ferie_annue(M, anni) == giorni
    assert R.ferie_annue("terziario", anni) == 26 and R.ferie_annue(L, anni) == 22


def test_preavviso_della_logistica_dimezzato_per_le_dimissioni():
    assert R.preavviso_minimo("licenziamento", "Quadri", date(2023, 1, 1), date(2026, 9, 30), L) == 75
    assert R.preavviso_minimo("dimissioni", "Quadri", date(2023, 1, 1), date(2026, 9, 30), L) == 37.5
    assert R.preavviso_minimo("dimissioni", "B2", date(2023, 1, 1), date(2026, 9, 30), M) == 60


@pytest.mark.parametrize("ccnl,evento,durata,quota", [
    (T, 1, 5, 0.0), (T, 1, 6, 1.0), (M, 3, 3, 1.0), (M, 4, 3, 0.66), (M, 6, 5, 0.5), (M, 6, 6, 1.0),
    (L, 9, 2, 1.0), ("terziario", 5, 3, 0.0)])
def test_carenza_con_la_regola_del_ccnl(ccnl, evento, durata, quota):
    assert R.carenza_percentuale(evento, False, ccnl, durata) == quota


def test_indennita_inps_per_settore():
    dal, al = date(2026, 9, 1), date(2026, 9, 14)
    assert R.indennita_malattia(2000.0, dal, al, "2026-09", ccnl=M) == 0.0          # impiegato dell'industria
    g = R.rmgg(2000.0, 0.0, T)
    assert R.indennita_malattia(2000.0, dal, al, "2026-09", ccnl=T) == R.centesimi(g * 0.8 * 11 + g * 0.8 * 0)
    g = R.rmgg(2000.0)
    assert R.indennita_malattia(2000.0, dal, al, "2026-09") == R.centesimi(g * 0.5 * 11)


def test_industria_senza_fis():
    assert R.aliquota_cliente("D") == pytest.approx(C.ALIQUOTA_DIPENDENTE + C.CIGS_DIPENDENTE)
    assert R.aliquota_cliente("F") > R.aliquota_cliente("D")


def test_quota_del_netto_garantita():
    malattia = (date(2026, 9, 7), date(2026, 9, 20))           # 14 giorni: 3 di carenza, 11 al 75%
    attesa = (30 - 14 + 3 + 11 * 0.75) / 30
    assert R.quota_netto_garantita("2026-09", "terziario", malattia, 1.0) == pytest.approx(attesa)
    assert R.quota_netto_garantita("2026-09", M, malattia, 1.0) is None              # sul lordo
    assert R.quota_netto_garantita("2026-09", T) == 1.0                              # maternità del Turismo
    assert R.quota_netto_garantita("2026-09", L) is None


def test_integrazione_lorda():
    dal, al = date(2026, 9, 3), date(2026, 9, 17)              # 15 giorni, 12 dopo la carenza
    assert R.integrazione_lorda(3000.0, 0.0, dal, al, "2026-09", M) == 1200.0
    assert R.integrazione_lorda(3000.0, 500.0, dal, al, "2026-09", L) == 700.0
    assert R.integrazione_lorda(3000.0, 0.0, dal, al, "2026-09") is None


def test_un_mese_di_malattia_torna_in_ogni_voce(out):
    """Retribuzione tolta, indennità, carenza e integrazione nel lordo; contributi senza l'indennità INPS: i cedolini
    di malattia corretti non hanno segnalazioni."""
    m, an = out["mese"], out["anomalie"]
    sbagliati = set(__import__("pandas").read_csv(C.ERRORI, keep_default_na=False)["matricola"])
    malati = m[(m["evento"] == "malattia") & ~m["matricola"].isin(sbagliati)]
    assert len(malati) >= 6 and set(malati["cliente"]) >= {"A", "D", "E", "F"}
    assert an["matricola"].isin(malati["matricola"]).sum() == 0
    for r in malati.itertuples(index=False):
        assert float(r.assenza_trattenuta) > 0 and r.lordo < r.tabellare + r.scatti + r.superminimo + 0.01 + float(
            r.malattia_inps) + float(r.malattia_carenza) + float(r.integrazione_datore)


def test_la_tranche_di_novembre_e_del_solo_terziario(out):
    assert set(out["novembre"]["cliente"]) == set(C.CLIENTI_V1)
    assert "C22" in controlli.CONTROLLI
