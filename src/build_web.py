"""
Scrive gli input dello strumento nel browser (web/inputs.json) e i casi con cui il suo JavaScript
viene verificato (tests/fixtures/js_vectors.json): i dati di esempio e varianti con alterazioni
casuali, ognuna con le segnalazioni calcolate qui in Python. tests/js/check_controlli.mjs rifà i
conti con web/controlli.js e fallisce alla prima differenza.
"""
import json
import random

import pandas as pd

import config as C
import controlli
import regole as R

WEB = C.ROOT / "web"
VECTORS = C.ROOT / "tests" / "fixtures" / "js_vectors.json"
VOCI = ["tabellare", "scatti", "superminimo", "straordinari", "lordo", "contributi_inps", "imponibile_irpef", "irpef",
        "bonus_cuneo", "trattamento_integrativo", "altre_trattenute", "netto", "quota_tfr", "ferie_residuo",
        "ferie_godute", "permessi_residuo", "permessi_goduti"]


def regole(k: str) -> dict:
    """Le regole di un CCNL con i nomi che usa web/controlli.js: sopra i parametri comuni, per ogni riga."""
    g = C.CCNL[k]
    return {"colonna_minimo": g["minimo"], "colonna_minimo_prossimo": g["minimo_prossimo"],
            "tranche_ccnl": g["prossima_tranche"].isoformat(), "scatti_max": g["scatti_max"],
            "scatti_anni": g["scatti_anni"], "mensilita": g["mensilita"],
            "quattordicesima_senza_scatti": g["quattordicesima_senza_scatti"],
            "giorni_mese_intero": g["giorni_mese_intero"], "somma_frazioni": g["somma_frazioni"],
            "ferie": [list(f) for f in g["ferie"]], "divisore_giornaliero": g["divisore_giornaliero"],
            "rol_fino_a_15": g["rol"]["fino_a_15"], "rol_oltre_15": g["rol"]["oltre_15"],
            "ex_festivita": g["ex_festivita"], "rol_nuovi_assunti": g["rol_nuovi_assunti"],
            "preavviso": {tipo: {lv: list(v) for lv, v in t.items()} for tipo, t in g["preavviso"].items()},
            "malattia_inps": g["malattia_inps"], "p1": g["malattia_fasce"][0][1], "p2": g["malattia_fasce"][1][1],
            "regola_carenza": g["carenza"],
            "integrazione": None if g["integrazione"] is None else {"base": g["integrazione"]["base"],
                                                                    "quote": list(g["integrazione"]["quote"])},
            "maternita_netto": g["maternita_netto"]}


def cfg() -> dict:
    return {**regole(R.T),          # il Terziario anche al primo livello, per chi chiama le funzioni senza un cliente
            "regole": {k: regole(k) for k in C.CCNL}, "ccnl_default": R.T,
            "mese": C.MESE, "mese_precedente": C.MESE_PRECEDENTE, "aliquota": C.ALIQUOTA_DIPENDENTE,
            "divisore_tfr": C.DIVISORE_TFR,
            "soglia": C.SOGLIA_VARIAZIONE, "tolleranza": C.TOLLERANZA, "tolleranza_ferie": C.TOLLERANZA_FERIE,
            "prossima_tranche": C.PROSSIMA_TRANCHE.isoformat(),
            # contributi per posizione INPS (F14, F15) e CCNL: l'esempio ha i suoi clienti; per i file dell'utente
            # valgono i campi della pagina, che partono da questi valori
            "posizioni": {c: {"media_semestre": v["media_semestre"], "dipendenti": v["dipendenti"],
                              "ccnl": v["ccnl"], "fis": v.get("fis", True)} for c, v in C.CLIENTI.items()},
            "media_default": 20.0, "dipendenti_default": 20,
            "carenza_metalmeccanico": {**C.CARENZA_METALMECCANICO, "quote": list(C.CARENZA_METALMECCANICO["quote"])},
            "carenza_turismo_durata": C.CARENZA_TURISMO_DURATA,
            "cigs": C.CIGS_DIPENDENTE, "cigs_soglia": C.CIGS_SOGLIA, "fis_fino_a_5": C.FIS_ALIQUOTA["fino_a_5"],
            "fis_oltre_5": C.FIS_ALIQUOTA["oltre_5"], "fis_soglia": C.FIS_SOGLIA, "fis_quota": C.FIS_QUOTA_DIPENDENTE,
            "aggiuntiva": C.ALIQUOTA_AGGIUNTIVA, "prima_fascia": C.PRIMA_FASCIA_MENSILE,
            # assenze e permessi (F16-F18, F23)
            "divisore_rmgg": C.DIVISORE_RMGG, "carenza": C.MALATTIA_CARENZA, "f1": C.MALATTIA_FASCE[0][0],
            "f2": C.MALATTIA_FASCE[1][0],
            "maternita": C.MATERNITA_PERCENTUALE, "carenza_percentuali": list(C.CARENZA_PERCENTUALI),
            "rol_soglia": C.ROL_SOGLIA, "tolleranza_ore": C.TOLLERANZA_ORE,
            # TFR alla cessazione (F19-F22)
            "tfr_fisso": C.TFR_TASSO_FISSO, "tfr_quota": C.TFR_QUOTA_INFLAZIONE, "foi_dicembre": C.FOI_DICEMBRE,
            "foi_raccordo": C.FOI_RACCORDO, "foi_mesi": C.FOI_MESI, "imposta_tfr": C.IMPOSTA_SOSTITUTIVA_TFR,
            "contributo_tfr": C.CONTRIBUTO_TFR,
            # IRPEF 2026 (F24-F29)
            "scaglioni_irpef": [list(s) for s in C.SCAGLIONI_IRPEF], "detrazione_lavoro": C.DETRAZIONE_LAVORO,
            "decimali_rapporto": C.DECIMALI_RAPPORTO, "cuneo_somma_soglia": C.CUNEO_SOMMA_SOGLIA,
            "cuneo_somma_fasce": [list(s) for s in C.CUNEO_SOMMA_FASCE], "cuneo_detrazione": C.CUNEO_DETRAZIONE,
            "trattamento_integrativo": C.TRATTAMENTO_INTEGRATIVO, "giorni_anno": C.GIORNI_ANNO}


def ccnl() -> dict:
    """Le tabelle dei quattro CCNL: CCNL, livello, colonna."""
    return {k: {lv: {c: float(v) for c, v in row.items()} for lv, row in R.tabella(k).iterrows()} for k in C.CCNL}


def write_templates(rows: int = 2) -> None:
    """The two template files the page offers for download, in the format of an Italian Excel export (semicolon,
    decimal comma), rebuilt from the data so they never drift from the columns the checks read."""
    ced = pd.read_csv(C.CEDOLINI, dtype={"livello": str, "evento": str}, keep_default_na=False)
    f24 = pd.read_csv(C.F24)
    for df, name in ((ced[ced["mese"] == C.MESE_PRECEDENTE].head(rows), "modello_cedolini.csv"), (f24, "modello_f24.csv")):
        text = df.to_csv(sep=";", index=False, float_format="%.4f", decimal=",")
        (WEB / name).write_text(text, encoding="utf-8")


def texts() -> dict:
    """Name, description, what to do and priority of every check, in Italian and in English."""
    import build_rapporto
    from testi_en import CONTROLLI_EN, PRIORITA_EN
    out = {"it": {}, "en": {}}
    for codice, (nome, descrizione, priorita) in controlli.CONTROLLI.items():
        out["it"][codice] = {"nome": nome, "descrizione": descrizione, "cosa_fare": build_rapporto.COSA_FARE[codice],
                             "priorita": priorita}
        nome_en, descrizione_en, cosa_fare_en = CONTROLLI_EN[codice]
        out["en"][codice] = {"nome": nome_en, "descrizione": descrizione_en, "cosa_fare": cosa_fare_en,
                             "priorita": PRIORITA_EN[priorita]}
    return out


def write_texts() -> None:
    (WEB / "testi.json").write_text(json.dumps(texts(), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def write_inputs() -> None:
    WEB.mkdir(exist_ok=True)
    write_templates()
    write_texts()
    (WEB / "inputs.json").write_text(json.dumps({"cfg": cfg(), "ccnl": ccnl()}, indent=1, sort_keys=True,
                                                ensure_ascii=False) + "\n", encoding="utf-8")


def _records(df: pd.DataFrame) -> list:
    d = df.copy()
    d["superminimo_assorbibile"] = d["superminimo_assorbibile"].astype(str).str.lower() == "true"
    return json.loads(d.to_json(orient="records"))


def _expected(m, prec, f24) -> dict:
    an, rec = controlli.esegui(m, prec, f24)
    nov = controlli.novembre(m)
    return {"anomalie": json.loads(an.to_json(orient="records")),
            "riconciliazione": json.loads(rec[["cliente", "diff_ritenute", "diff_contributi"]].to_json(orient="records")),
            "novembre": json.loads(nov.groupby("cliente")[["aumento", "assorbito", "da_pagare"]].sum().round(2)
                                   .reset_index().to_json(orient="records"))}


def write_vectors(n: int = 8, seed: int = 11) -> int:
    m, prec, f24 = controlli.carica()
    rng = random.Random(seed)
    cases = [{"patch": [], "f24_patch": [], **_expected(m, prec, f24)}]
    for _ in range(n):
        x, f = m.copy(), f24.copy()
        patch = []
        for _ in range(rng.randint(3, 12)):
            i, voce = rng.choice(list(x.index)), rng.choice(VOCI)
            v = round(float(x.loc[i, voce]) + rng.choice([-1, 1]) * rng.choice([0.005, 0.01, 0.02, 0.5, 3, 40]), 4)
            x.loc[i, voce] = v
            patch.append([int(i), voce, v])
        uscite = [k for k in x.index if x.loc[k, "data_cessazione"] != ""]
        for _ in range(rng.randint(1, 3)):                         # le voci di chi lascia, anche a mezzo centesimo
            i, voce = rng.choice(uscite), rng.choice(["tredicesima", "quattordicesima", "ferie_liquidate", "preavviso_giorni"])
            if voce == "preavviso_giorni":
                v = str(max(0, int(x.loc[i, voce]) + rng.choice([-30, -1, 0, 1])))
            else:
                v = f"{float(x.loc[i, voce]) + rng.choice([-1, 1]) * rng.choice([0.005, 0.01, 0.02, 25]):.3f}"
            x.loc[i, voce] = v
            patch.append([int(i), voce, v])
        eventi = [(k, v) for k in x.index for v in ("malattia_inps", "malattia_carenza", "maternita_inps",
                                                    "assenza_trattenuta", "integrazione_datore",
                                                    "tfr_liquidato", "imponibile_fiscale_anno", "ritenute_anno_prec",
                                                    "cuneo_anno_prec", "ti_anno_prec") if x.loc[k, v] != ""]
        for _ in range(rng.randint(1, 4)):                         # indennità, carenza e TFR, anche a mezzo centesimo
            i, voce = rng.choice(eventi)
            v = f"{float(x.loc[i, voce]) + rng.choice([-1, 1]) * rng.choice([0.005, 0.01, 0.02, 12, 300]):.3f}"
            x.loc[i, voce] = v
            patch.append([int(i), voce, v])
        i = rng.choice(list(x.index))                              # un codice fiscale trascritto male
        cf = x.loc[i, "codice_fiscale"]
        x.loc[i, "codice_fiscale"] = cf[:15] + ("Q" if cf[15] != "Q" else "R")
        patch.append([int(i), "codice_fiscale", x.loc[i, "codice_fiscale"]])
        j = rng.randrange(len(f))
        f.loc[j, "contributi_dipendente"] = round(float(f.loc[j, "contributi_dipendente"]) + rng.choice([0, 0.01, 5.0]), 2)
        cases.append({"patch": patch, "f24_patch": [[j, "contributi_dipendente", float(f.loc[j, "contributi_dipendente"])]],
                      **_expected(x, prec, f)})
    VECTORS.write_text(json.dumps({"cfg": cfg(), "ccnl": ccnl(), "mese": _records(m), "prec": _records(prec),
                                   "f24": json.loads(f24.to_json(orient="records")), "cases": cases},
                                  ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    return len(cases)


def main() -> None:
    write_inputs()
    print(f"web -> web/inputs.json; {write_vectors()} casi -> tests/fixtures/js_vectors.json")


if __name__ == "__main__":
    main()
