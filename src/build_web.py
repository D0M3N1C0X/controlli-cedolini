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
VOCI = ["tabellare", "scatti", "superminimo", "straordinari", "lordo", "contributi_inps", "irpef",
        "altre_trattenute", "netto", "quota_tfr", "ferie_residuo", "ferie_godute"]


def cfg() -> dict:
    return {"mese": C.MESE, "mese_precedente": C.MESE_PRECEDENTE, "colonna_minimo": C.COLONNA_MINIMO,
            "colonna_minimo_prossimo": C.COLONNA_MINIMO_PROSSIMO, "aliquota": C.ALIQUOTA_DIPENDENTE,
            "divisore_tfr": C.DIVISORE_TFR, "mensilita": C.MENSILITA, "ferie_annue": C.FERIE_ANNUE,
            "soglia": C.SOGLIA_VARIAZIONE, "tolleranza": C.TOLLERANZA, "tolleranza_ferie": C.TOLLERANZA_FERIE,
            "scatti_max": C.SCATTI_MAX, "scatti_anni": C.SCATTI_ANNI}


def ccnl() -> dict:
    t = R.tabella()
    return {lv: {k: float(v) for k, v in row.items()} for lv, row in t.iterrows()}


def write_inputs() -> None:
    WEB.mkdir(exist_ok=True)
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
