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
    "C01": ("Minimo tabellare", "Tabellare diverso dal minimo del livello (paga base, altri elementi, contingenza), "
                                 "part-time compreso", "alta"),
    "C02": ("Scatti di anzianità", "Importo degli scatti diverso da quelli maturati dalla data di assunzione", "alta"),
    "C03": ("Contributi INPS",
            "Contributo a carico del dipendente diverso da imponibile arrotondato all'euro × aliquota", "alta"),
    "C04": ("Quota TFR", "Rateo TFR diverso da retribuzione ordinaria × 14 / 13,5 / 12", "media"),
    "C05": ("Residuo ferie", "Residuo diverso da residuo del mese prima + maturate - godute", "media"),
    "C06": ("Quadratura", "Lordo diverso dalla somma delle voci, o netto diverso da lordo meno trattenute", "alta"),
    "C07": ("Variazione del netto",
            "Netto oltre il 20% sopra o sotto il mese prima, senza un evento che lo spieghi", "media"),
    "C08": ("Riconciliazione F24", "Ritenute o contributi in F24 diversi dalla somma dei cedolini del cliente", "alta"),
    "C09": ("Codice fiscale", "Carattere di controllo non valido", "alta"),
    "C10": ("Anagrafica",
            "Livello, part-time, superminimo o data di assunzione diversi dal mese prima, senza un evento", "alta"),
    "C11": ("Ratei 13ª e 14ª",
            "Dodicesimi maturati diversi dai mesi di servizio nel periodo (frazione di 15 giorni intera)", "media"),
    "C12": ("Tredicesima e quattordicesima pagate",
            "Importo diverso dalla retribuzione mensile per i dodicesimi maturati, a dicembre o alla cessazione",
            "alta"),
    "C13": ("Ferie non godute",
            "Alla cessazione, ferie residue pagate diversamente da 1/26 della retribuzione mensile al giorno", "alta"),
    "C14": ("Preavviso",
            "Alla cessazione, giorni di preavviso sotto il minimo del CCNL per livello e anni di servizio", "alta"),
}
TIPO_CONTROLLO = {"minimo": "C01", "scatto": "C02", "inps": "C03", "tfr": "C04", "ferie": "C05", "netto": "C06",
                  "variazione": "C07", "f24": "C08", "codice_fiscale": "C09",
                  "anagrafica": "C10", "ratei": "C11", "tredicesima": "C12", "ferie_liquidate": "C13",
                  "preavviso": "C14"}

CESSAZIONE = ["data_cessazione", "tipo_cessazione", "preavviso_giorni", "tredicesima", "quattordicesima",
              "ferie_liquidate"]


def carica() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ced = pd.read_csv(C.CEDOLINI, dtype={"livello": str, "evento": str, **{c: str for c in CESSAZIONE}},
                      keep_default_na=False)
    return (ced[ced["mese"] == C.MESE].reset_index(drop=True), ced[ced["mese"] == C.MESE_PRECEDENTE],
            pd.read_csv(C.F24))


def attesi(m: pd.DataFrame, prec: pd.DataFrame) -> pd.DataFrame:
    """Il valore atteso di ogni voce controllata, calcolato dalle regole e non dal cedolino."""
    t = R.tabella()
    a = m[["matricola", "cliente", "livello", "part_time"]].copy()
    a["tabellare"] = [R.centesimi(t.loc[lv, C.COLONNA_MINIMO] * p)
                      for lv, p in zip(m["livello"], m["part_time"], strict=True)]
    a["scatti_n"] = [R.scatti_maturati(date.fromisoformat(d), C.MESE) for d in m["data_assunzione"]]
    a["scatti"] = [R.centesimi(t.loc[lv, "scatto"] * n * p)
                   for lv, n, p in zip(m["livello"], a["scatti_n"], m["part_time"], strict=True)]
    a["contributi_inps"] = m["lordo"].map(R.contributi)
    ordinaria = m["tabellare"] + m["scatti"] + m["superminimo"]
    a["quota_tfr"] = ordinaria.map(R.quota_tfr)
    residuo_prec = m["matricola"].map(prec.set_index("matricola")["ferie_residuo"]).fillna(0.0)
    a["ferie_residuo"] = (residuo_prec + R.ferie_mese() - m["ferie_godute"]).round(4)
    extra = sum(pd.to_numeric(m[c], errors="coerce").fillna(0.0) if c in m else 0.0
                for c in ("tredicesima", "quattordicesima", "ferie_liquidate"))
    a["lordo"] = (ordinaria + m["straordinari"] + extra).map(R.centesimi)
    a["netto"] = (m["lordo"] - m["contributi_inps"] - m["irpef"] - m["altre_trattenute"]).map(R.centesimi)
    a["netto_prec"] = m["matricola"].map(prec.set_index("matricola")["netto"])
    a["variazione"] = m["netto"] / a["netto_prec"] - 1
    assunti = [date.fromisoformat(d) for d in m["data_assunzione"]]
    uscite = (m["data_cessazione"] if "data_cessazione" in m else pd.Series([""] * len(m), index=m.index))
    ratei = [R.ratei_al(d, C.MESE, None if _vuoto(c) else date.fromisoformat(str(c)))
             for d, c in zip(assunti, uscite, strict=True)]
    a["ratei_13"] = [r[0] for r in ratei]
    a["ratei_14"] = [r[1] for r in ratei]
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

    def segnala(i, codice, atteso, trovato) -> None:
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
        if not (_vuoto(m.loc[i, "ratei_13"]) or _vuoto(m.loc[i, "ratei_14"])):      # facoltative: tutte e due
            r13, r14 = int(float(m.loc[i, "ratei_13"])), int(float(m.loc[i, "ratei_14"]))
            e13, e14 = int(a.loc[i, "ratei_13"]), int(a.loc[i, "ratei_14"])
            if (r13, r14) != (e13, e14):
                segnala(i, "C11", f"13ª {e13}; 14ª {e14}", f"13ª {r13}; 14ª {r14}")
        _cessazione(m.loc[i], segnala, i)
        p = prev_by.get(m.loc[i, "matricola"])
        if p is not None and m.loc[i, "evento"] == "":
            cambi = [(c, p[c], m.loc[i, c]) for c in ANAGRAFICA if _diverso(p[c], m.loc[i, c])]
            if cambi:
                segnala(i, "C10", "; ".join(f"{c} {_fmt(a)}" for c, a, _ in cambi),
                        "; ".join(f"{c} {_fmt(b)}" for c, _, b in cambi))

    somme = m.groupby("cliente")[["irpef", "contributi_inps"]].sum().map(R.centesimi)
    rec = f24.set_index("cliente").join(somme)
    rec[["irpef", "contributi_inps"]] = rec[["irpef", "contributi_inps"]].fillna(0.0)   # un F24 senza cedolini
    rec["diff_ritenute"] = (rec["ritenute_1001"] - rec["irpef"]).map(R.centesimi)
    rec["diff_contributi"] = (rec["contributi_dipendente"] - rec["contributi_inps"]).map(R.centesimi)
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


def _vuoto(v) -> bool:
    return v is None or (isinstance(v, float) and v != v) or str(v).strip() == ""


def _cessazione(r: pd.Series, segnala, i: int) -> None:
    """C12-C14: le voci pagate a dicembre o alla cessazione, quando il cedolino le riporta."""
    assunzione = date.fromisoformat(str(r["data_assunzione"]))
    mensile = R.centesimi(r["tabellare"] + r["scatti"] + r["superminimo"])
    ces = None if _vuoto(r.get("data_cessazione")) else date.fromisoformat(str(r["data_cessazione"]))
    for voce, inizio, ratei in (("tredicesima", R.inizio_13, R.ratei_13),
                                ("quattordicesima", R.inizio_14, R.dodicesimi_14_pagata)):
        if _vuoto(r.get(voce)):
            continue
        n = R.dodicesimi_alla_cessazione(assunzione, ces, inizio(ces)) if ces else ratei(assunzione, C.MESE)
        atteso, trovato = R.mensilita_aggiuntiva(mensile, n), float(r[voce])
        if abs(trovato - atteso) > C.TOLLERANZA:
            segnala(i, "C12", atteso, trovato)
            break
    if ces is None:
        return
    if not _vuoto(r.get("ferie_liquidate")):
        atteso, trovato = R.ferie_non_godute(mensile, r["ferie_residuo"]), float(r["ferie_liquidate"])
        if abs(trovato - atteso) > C.TOLLERANZA:
            segnala(i, "C13", atteso, trovato)
    tipo = str(r.get("tipo_cessazione", "")).strip().lower()
    if tipo in C.PREAVVISO and not _vuoto(r.get("preavviso_giorni")):
        minimo = R.preavviso_minimo(tipo, str(r["livello"]), assunzione, ces)
        if int(float(r["preavviso_giorni"])) < minimo:
            segnala(i, "C14", float(minimo), float(r["preavviso_giorni"]))


def valutazione(anomalie: pd.DataFrame) -> pd.DataFrame:
    """Per ogni controllo: errori inseriti, trovati, mancati, falsi allarmi."""
    err = pd.read_csv(C.ERRORI, keep_default_na=False)
    err["controllo"] = err["tipo"].map(TIPO_CONTROLLO)
    chiave = lambda d: set(zip(d["controllo"], d["cliente"], d["matricola"], strict=True))
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
    if "data_cessazione" in m:          # chi lascia prima della tranche non la riceve
        resta = [_vuoto(d) or date.fromisoformat(str(d)) >= C.PROSSIMA_TRANCHE for d in m["data_cessazione"]]
        m = m[resta]
    n = m[["matricola", "cliente", "livello", "part_time", "superminimo", "superminimo_assorbibile"]].copy()
    n["superminimo_assorbibile"] = n["superminimo_assorbibile"].astype(str).str.lower() == "true"
    n["aumento"] = [R.centesimi((t.loc[lv, C.COLONNA_MINIMO_PROSSIMO] - t.loc[lv, C.COLONNA_MINIMO]) * p)
                    for lv, p in zip(n["livello"], n["part_time"], strict=True)]
    n["assorbito"] = [min(s, a) if ok else 0.0 for s, a, ok in zip(n["superminimo"], n["aumento"],
                                                                    n["superminimo_assorbibile"], strict=True)]
    n["da_pagare"] = (n["aumento"] - n["assorbito"]).map(R.centesimi)
    n["nuovo_tabellare"] = [R.centesimi(t.loc[lv, C.COLONNA_MINIMO_PROSSIMO] * p)
                            for lv, p in zip(n["livello"], n["part_time"], strict=True)]
    n["nuovo_superminimo"] = (n["superminimo"] - n["assorbito"]).map(R.centesimi)
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
