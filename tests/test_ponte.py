"""Il ponte (ponte.py): l'estratto per il kit della trasparenza dice le stesse cose al kit e a noi, e i conti
italiani di INPS e TFR sono quelli di workforce-cost-model."""
import json

import pandas as pd
import pytest

import anno
import config as C
import ponte
import regole as R


@pytest.fixture(scope="module")
def p():
    return ponte.run()


def test_ogni_voce_ha_una_natura_e_una_colonna_del_kit(p):
    d = p["dizionario"]
    assert d["voce"].is_unique
    assert set(d["natura"]) <= {"fissa e continuativa", "variabile", "esclusa", "sostitutiva"}
    assert (d.loc[d["natura"] == "esclusa", "colonna_ptk"] == "").all()
    assert set(d["colonna_ptk"]) - {""} <= set(ponte.COLONNE)
    # le voci fisse del cedolino non finiscono fra le componenti variabili
    assert set(d.loc[d["colonna_ptk"] == "bonus", "voce"]) == {"straordinari"}


def test_estratto_salvato_e_coerente(p):
    e = p["estratto"]
    salvato = pd.read_csv(ponte.ESTRATTO, keep_default_na=False)
    assert list(salvato.columns) == ponte.COLONNE and len(salvato) == len(e)
    assert (e["payroll_total"] - e[["base_pay", "bonus", "commission", "shift_allowance", "car_allowance"]]
            .sum(axis=1)).abs().max() < 0.02
    assert set(e["gender"]) == {"F", "M"} and (e["annual_hours"] > 0).all()
    # un tempo pieno tutto l'anno: 40 ore per 52 settimane
    pieno = e[(e["period_status"] == "whole period") & (e["weekly_hours"] == ponte.ORE)]
    assert len(pieno) and (pieno["annual_hours"] == ponte.ORE * ponte.SETTIMANE).all()


def test_il_kit_calcola_gli_stessi_indicatori(p):
    """data/ponte/indicatori_ptk.json è scritto dal codice del kit (tools/ptk_indicatori.py, rifatto nella CI)."""
    ptk = json.loads(ponte.INDICATORI_PTK.read_text(encoding="utf-8"))
    assert ptk["kit_commit"].startswith(ponte.PTK_COMMIT)
    ind = p["indicatori"].set_index("country")
    assert sorted(ptk["clienti"]) == sorted(ind.index)
    for c, valori in ptk["clienti"].items():
        for k, v in valori.items():
            nostro = ind.loc[c, k]
            if v is None:
                assert pd.isna(nostro), (c, k)
            else:
                assert nostro == pytest.approx(v, abs=1e-9), (c, k)


def test_categorie_dai_livelli_del_ccnl(p):
    cat = p["categorie"]
    assert (cat["donne"] + cat["uomini"]).sum() == len(p["estratto"])
    flag = cat[cat["stato"] == "da giustificare"]
    assert (flag["divario_orario"].abs() >= ponte.SOGLIA).all()


def test_ivs_datore_piu_dipendente_e_il_33_per_cento(p):
    assert p["wcm"]["IT_IVS"] + C.ALIQUOTA_DIPENDENTE == pytest.approx(ponte.IVS_TOTALE, abs=1e-9)
    assert p["wcm"]["TFR_DIVISOR"] == C.DIVISORE_TFR


def test_tfr_stessa_formula_a_retribuzione_costante():
    """Dodici quote mensili dei cedolini = la quota annua del modello di costo, a meno dei centesimi."""
    for ccnl, mensile in (("terziario", 1781.68), ("metalmeccanico", 2100.0), ("turismo", 1650.5)):
        mensilita = R.regola(ccnl)["mensilita"]
        dodici = 12 * R.quota_tfr(mensile, 0.0, ccnl)
        assert abs(dodici - mensile * mensilita / ponte.wcm()["TFR_DIVISOR"]) <= 12 * 0.005


def test_tfr_sui_cedolini_dell_anno(p):
    t = p["tfr"]
    assert len(t) > 100
    assert abs(t["differenza"].median()) < 5           # di calendario, non di formula
    # sopra 5 euro solo chi è entrato dopo il 1° luglio 2025: la quattordicesima di luglio copre meno di 12 mesi
    assunti = anno.dipendenti().set_index("matricola")["data_assunzione"]
    grandi = t.loc[t["differenza"].abs() > 5, "matricola"]
    assert len(grandi) and (grandi.map(assunti) > "2025-07-01").all()


def test_checksum_del_modello_di_costo(tmp_path, monkeypatch):
    finto = tmp_path / "wcm.txt"
    finto.write_text(ponte.WCM_CONFIG.read_text(encoding="utf-8").replace("13.5", "14"), encoding="utf-8")
    monkeypatch.setattr(ponte, "WCM_CONFIG", finto)
    with pytest.raises(SystemExit):
        ponte.wcm()


def test_l_estratto_segue_l_anno():
    ced, extra = anno.genera_anno()
    e = ponte.estratto(ced, extra)
    assert set(e["worker_id"]) == set(ced.loc[ced["mese"].isin(anno.MESI), "matricola"])
