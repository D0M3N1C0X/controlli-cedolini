"""
I controlli sui cedolini del mese, l'adeguamento alla tranche di novembre 2026 e la misura di
quanto funzionano i controlli sugli errori inseriti nei dati sintetici.

    python src/controlli.py

Ogni controllo ricalcola un valore atteso in modo indipendente dal software paghe e lo confronta
con quello sul cedolino: non serve sapere come il software l'ha calcolato.
"""
from datetime import date

import pandas as pd

import codice_fiscale
import config as C
import regole as R

CONTROLLI = {
    "C01": ("Minimo tabellare", "Paga base + contingenza diversa dal minimo del livello, part-time compreso", "alta"),
    "C02": ("Scatti di anzianità", "Importo degli scatti diverso da quelli maturati dalla data di assunzione", "alta"),
    "C03": ("Contributi INPS", "Contributo a carico del dipendente diverso da imponibile × aliquota", "alta"),
    "C04": ("Quota TFR", "Rateo TFR diverso da retribuzione ordinaria × 14 / 13,5 / 12", "media"),
    "C05": ("Residuo ferie", "Residuo diverso da residuo del mese prima + maturate - godute", "media"),
    "C06": ("Quadratura", "Lordo diverso dalla somma delle voci, o netto diverso da lordo meno trattenute", "alta"),
    "C07": ("Variazione del netto", "Netto oltre il 20% sopra o sotto il mese prima, senza un evento che lo spieghi", "media"),
    "C08": ("Riconciliazione F24", "Ritenute o contributi in F24 diversi dalla somma dei cedolini del cliente", "alta"),
    "C09": ("Codice fiscale", "Carattere di controllo non valido", "alta"),
    "C10": ("Anagrafica", "Livello, part-time, superminimo o data di assunzione diversi dal mese prima, senza un evento", "alta"),
}
TIPO_CONTROLLO = {"minimo": "C01", "scatto": "C02", "inps": "C03", "tfr": "C04", "ferie": "C05", "netto": "C06",
                  "variazione": "C07", "f24": "C08", "codice_fiscale": "C09",
                  "anagrafica": "C10"}


def carica() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ced = pd.read_csv(C.CEDOLINI, dtype={"livello": str, "evento": str}, keep_default_na=False)
    return (ced[ced["mese"] == C.MESE].reset_index(drop=True), ced[ced["mese"] == C.MESE_PRECEDENTE],
            pd.read_csv(C.F24))


def attesi(m: pd.DataFrame, prec: pd.DataFrame) -> pd.DataFrame:
    """Il valore atteso di ogni voce controllata, calcolato dalle regole e non dal cedolino."""
    t = R.tabella()
    a = m[["matricola", "cliente", "livello", "part_time"]].copy()
    a["tabellare"] = [R.centesimi(t.loc[l, C.COLONNA_MINIMO] * p) for l, p in zip(m["livello"], m["part_time"])]
    a["scatti_n"] = [R.scatti_maturati(date.fromisoformat(d), C.MESE) for d in m["data_assunzione"]]
    a["scatti"] = [R.centesimi(t.loc[l, "scatto"] * n * p) for l, n, p in zip(m["livello"], a["scatti_n"], m["part_time"])]
    a["contributi_inps"] = (m["lordo"] * C.ALIQUOTA_DIPENDENTE).map(R.centesimi)
    ordinaria = m["tabellare"] + m["scatti"] + m["superminimo"]
    a["quota_tfr"] = ordinaria.map(R.quota_tfr)
    residuo_prec = m["matricola"].map(prec.set_index("matricola")["ferie_residuo"]).fillna(0.0)
    a["ferie_residuo"] = (residuo_prec + R.ferie_mese() - m["ferie_godute"]).round(4)
    a["lordo"] = (ordinaria + m["straordinari"]).round(2)
    a["netto"] = (m["lordo"] - m["contributi_inps"] - m["irpef"] - m["altre_trattenute"]).round(2)
    a["netto_prec"] = m["matricola"].map(prec.set_index("matricola")["netto"])
    a["variazione"] = m["netto"] / a["netto_prec"] - 1
    return a


ANAGRAFICA = ["livello", "part_time", "superminimo", "data_assunzione"]


def _diverso(a, b) -> bool:
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) > C.TOLLERANZA
    return str(a) != str(b)


def _fmt(v) -> str:
    return f"{v:g}" if isinstance(v, float) else str(v)


def esegui(m: pd.DataFrame, prec: pd.DataFrame, f24: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    a = attesi(m, prec)
    prev_by = {r["matricola"]: r for r in prec.to_dict("records")}
    out = []

    def segnala(i, codice, atteso, trovato):
        diff = trovato - atteso if isinstance(atteso, (int, float)) and isinstance(trovato, (int, float)) else None
        out.append({"matricola": m.loc[i, "matricola"], "cliente": m.loc[i, "cliente"], "controllo": codice,
                    "voce": CONTROLLI[codice][0], "atteso": atteso, "trovato": trovato, "differenza": diff,
                    "priorita": CONTROLLI[codice][2]})

    for i in m.index:
        for codice, voce, tol in (("C01", "tabellare", C.TOLLERANZA), ("C02", "scatti", C.TOLLERANZA),
                                  ("C03", "contributi_inps", C.TOLLERANZA), ("C04", "quota_tfr", C.TOLLERANZA),
                                  ("C05", "ferie_residuo", C.TOLLERANZA_FERIE)):
            if abs(m.loc[i, voce] - a.loc[i, voce]) > tol:
                segnala(i, codice, float(a.loc[i, voce]), float(m.loc[i, voce]))
        if abs(m.loc[i, "lordo"] - a.loc[i, "lordo"]) > C.TOLLERANZA:
            segnala(i, "C06", float(a.loc[i, "lordo"]), float(m.loc[i, "lordo"]))
        elif abs(m.loc[i, "netto"] - a.loc[i, "netto"]) > C.TOLLERANZA:
            segnala(i, "C06", float(a.loc[i, "netto"]), float(m.loc[i, "netto"]))
        v = a.loc[i, "variazione"]
        if pd.notna(v) and abs(v) > C.SOGLIA_VARIAZIONE and m.loc[i, "evento"] == "":
            segnala(i, "C07", float(a.loc[i, "netto_prec"]), float(m.loc[i, "netto"]))
        if not codice_fiscale.valido(m.loc[i, "codice_fiscale"]):
            segnala(i, "C09", "valido", m.loc[i, "codice_fiscale"])
        p = prev_by.get(m.loc[i, "matricola"])
        if p is not None and m.loc[i, "evento"] == "":
            cambi = [(c, p[c], m.loc[i, c]) for c in ANAGRAFICA if _diverso(p[c], m.loc[i, c])]
            if cambi:
                segnala(i, "C10", "; ".join(f"{c} {_fmt(a)}" for c, a, _ in cambi),
                        "; ".join(f"{c} {_fmt(b)}" for c, _, b in cambi))

    somme = m.groupby("cliente")[["irpef", "contributi_inps"]].sum().round(2)
    rec = f24.set_index("cliente").join(somme)
    rec["diff_ritenute"] = (rec["ritenute_1001"] - rec["irpef"]).round(2)
    rec["diff_contributi"] = (rec["contributi_dipendente"] - rec["contributi_inps"]).round(2)
    for cliente, r in rec.iterrows():
        if abs(r["diff_ritenute"]) > C.TOLLERANZA or abs(r["diff_contributi"]) > C.TOLLERANZA:
            voce = "ritenute_1001" if abs(r["diff_ritenute"]) > C.TOLLERANZA else "contributi_dipendente"
            atteso = float(r["irpef"] if voce == "ritenute_1001" else r["contributi_inps"])
            out.append({"matricola": "", "cliente": cliente, "controllo": "C08", "voce": CONTROLLI["C08"][0],
                        "atteso": atteso, "trovato": float(r[voce]), "differenza": float(r[voce]) - atteso,
                        "priorita": "alta"})
    anomalie = pd.DataFrame(out, columns=["matricola", "cliente", "controllo", "voce", "atteso", "trovato",
                                          "differenza", "priorita"])
    return anomalie.sort_values(["controllo", "cliente", "matricola"]).reset_index(drop=True), rec.reset_index()


def valutazione(anomalie: pd.DataFrame) -> pd.DataFrame:
    """Per ogni controllo: errori inseriti, trovati, mancati, falsi allarmi."""
    err = pd.read_csv(C.ERRORI, keep_default_na=False)
    err["controllo"] = err["tipo"].map(TIPO_CONTROLLO)
    chiave = lambda d: set(zip(d["controllo"], d["cliente"], d["matricola"]))
    attesi_, trovati = chiave(err), chiave(anomalie)
    rows = []
    for codice in CONTROLLI:
        e = {k for k in attesi_ if k[0] == codice}
        t = {k for k in trovati if k[0] == codice}
        rows.append({"controllo": codice, "voce": CONTROLLI[codice][0], "inseriti": len(e), "trovati": len(e & t),
                     "mancati": len(e - t), "falsi_allarmi": len(t - e)})
    return pd.DataFrame(rows)


def novembre(m: pd.DataFrame) -> pd.DataFrame:
    """La tranche del 1° novembre 2026: aumento per dipendente, quanto ne assorbe il superminimo
    assorbibile, e quanto resta da pagare. L'assorbibilità va verificata sulla lettera di assunzione."""
    t = R.tabella()
    n = m[["matricola", "cliente", "livello", "part_time", "superminimo", "superminimo_assorbibile"]].copy()
    n["superminimo_assorbibile"] = n["superminimo_assorbibile"].astype(str).str.lower() == "true"
    n["aumento"] = [R.centesimi((t.loc[l, C.COLONNA_MINIMO_PROSSIMO] - t.loc[l, C.COLONNA_MINIMO]) * p)
                    for l, p in zip(n["livello"], n["part_time"])]
    n["assorbito"] = [min(s, a) if ok else 0.0 for s, a, ok in zip(n["superminimo"], n["aumento"],
                                                                    n["superminimo_assorbibile"])]
    n["da_pagare"] = (n["aumento"] - n["assorbito"]).round(2)
    n["nuovo_tabellare"] = [R.centesimi(t.loc[l, C.COLONNA_MINIMO_PROSSIMO] * p) for l, p in zip(n["livello"], n["part_time"])]
    n["nuovo_superminimo"] = (n["superminimo"] - n["assorbito"]).round(2)
    return n


def riepilogo_novembre(n: pd.DataFrame) -> pd.DataFrame:
    g = n.groupby("cliente").agg(dipendenti=("matricola", "count"), aumento=("aumento", "sum"),
                                 assorbito=("assorbito", "sum"), da_pagare=("da_pagare", "sum"),
                                 con_assorbimento=("assorbito", lambda s: int((s > 0).sum())))
    g["costo_annuo"] = (g["da_pagare"] * C.MENSILITA).round(2)
    return g.round(2).reset_index()


def run() -> dict:
    m, prec, f24 = carica()
    anomalie, rec = esegui(m, prec, f24)
    n = novembre(m)
    return {"mese": m, "precedente": prec, "f24": f24, "attesi": attesi(m, prec), "anomalie": anomalie,
            "riconciliazione_f24": rec, "valutazione": valutazione(anomalie), "novembre": n,
            "riepilogo_novembre": riepilogo_novembre(n)}


def main() -> None:
    o = run()
    C.REPORT.mkdir(exist_ok=True)
    o["anomalie"].to_csv(C.REPORT / "anomalie.csv", index=False, float_format="%.2f")
    print(o["valutazione"].to_string(index=False))
    print(o["riepilogo_novembre"].to_string(index=False))


if __name__ == "__main__":
    main()
