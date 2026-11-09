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
    "C02": ("Scatti di anzianità", "Importo degli scatti diverso da quelli maturati dalla data di assunzione, con "
                                    "periodo e numero massimo del CCNL", "alta"),
    "C03": ("Contributi INPS",
            "Contributo a carico del dipendente diverso da imponibile arrotondato all'euro × aliquota della posizione "
            "(IVS, CIGS, FIS), più l'1% oltre la prima fascia pensionabile", "alta"),
    "C04": ("Quota TFR", "Rateo TFR diverso da retribuzione ordinaria × mensilità del CCNL / 13,5 / 12", "media"),
    "C05": ("Residuo ferie", "Residuo diverso da residuo del mese prima + maturate - godute, con le ferie annue del CCNL",
            "media"),
    "C06": ("Quadratura", "Lordo diverso dalla somma delle voci, o netto diverso da lordo meno trattenute", "alta"),
    "C07": ("Variazione del netto",
            "Netto oltre il 20% sopra o sotto il mese prima, senza un evento che lo spieghi", "media"),
    "C08": ("Riconciliazione F24", "Ritenute o contributi in F24 diversi dalla somma dei cedolini del cliente", "alta"),
    "C09": ("Codice fiscale", "Carattere di controllo non valido", "alta"),
    "C10": ("Anagrafica",
            "Livello, part-time, superminimo o data di assunzione diversi dal mese prima, senza un evento", "alta"),
    "C11": ("Ratei 13ª e 14ª",
            "Dodicesimi maturati diversi dai mesi di servizio nel periodo, con la regola del CCNL per la frazione di "
            "mese", "media"),
    "C12": ("Tredicesima e quattordicesima pagate",
            "Importo diverso dalla retribuzione mensile per i dodicesimi maturati, a dicembre o alla cessazione",
            "alta"),
    "C13": ("Ferie non godute",
            "Alla cessazione, ferie residue pagate diversamente dalla quota giornaliera del CCNL (1/26 della "
            "retribuzione mensile, 1/22 nella Logistica)", "alta"),
    "C14": ("Preavviso",
            "Alla cessazione, giorni di preavviso sotto il minimo del CCNL per livello e anni di servizio", "alta"),
    "C15": ("Indennità di malattia INPS",
            "Indennità anticipata diversa dal 50% (4°-20° giorno) e 66,66% (21°-180°) della retribuzione media "
            "giornaliera del mese prima; 80% nei pubblici esercizi, nessuna per gli impiegati dell'industria", "alta"),
    "C16": ("Carenza di malattia",
            "Primi 3 giorni pagati quando il CCNL non li deve, o non pagati quando li deve", "media"),
    "C17": ("Indennità di maternità INPS",
            "Indennità anticipata diversa dall'80% della retribuzione media giornaliera del mese prima", "alta"),
    "C18": ("Permessi ROL ed ex festività",
            "Residuo ore diverso da residuo del mese prima + maturate - godute, con la maturazione del CCNL", "media"),
    "C19": ("TFR liquidato",
            "Alla cessazione, TFR diverso dal fondo rivalutato con l'indice ISTAT, al netto dell'imposta sostitutiva, "
            "più le quote dell'anno meno lo 0,50%", "alta"),
    "C20": ("IRPEF del mese",
            "Ritenuta, somma del cuneo fiscale o trattamento integrativo diversi da quelli delle regole 2026: "
            "scaglioni ragguagliati al mese, detrazioni per un dodicesimo sul reddito presunto dell'anno", "alta"),
    "C21": ("Conguaglio IRPEF alla cessazione",
            "Imposta dell'anno, detrazioni e trattamento integrativo rapportati ai giorni di lavoro, meno quanto già "
            "trattenuto o erogato: il cedolino di uscita porta una differenza diversa", "alta"),
    "C22": ("Integrazione del datore di lavoro",
            "Nel mese di malattia o maternità, integrazione sotto quella del CCNL: sul netto nel Terziario (il netto "
            "non sta sotto la quota garantita del netto normale), sul lordo nel Metalmeccanico e nella Logistica",
            "alta"),
}
TIPO_CONTROLLO = {"minimo": "C01", "scatto": "C02", "inps": "C03", "tfr": "C04", "ferie": "C05", "netto": "C06",
                  "variazione": "C07", "f24": "C08", "codice_fiscale": "C09",
                  "anagrafica": "C10", "ratei": "C11", "tredicesima": "C12", "ferie_liquidate": "C13",
                  "preavviso": "C14", "malattia": "C15", "carenza": "C16", "maternita": "C17", "permessi": "C18",
                  "tfr_liquidato": "C19", "irpef": "C20",
                  "conguaglio": "C21", "integrazione": "C22"}

CESSAZIONE = ["data_cessazione", "tipo_cessazione", "preavviso_giorni", "tredicesima", "quattordicesima",
              "ferie_liquidate"]
# Voci facoltative: vuote se nel mese non c'è l'evento (F16-F23)
ASSENZE = ["malattia_dal", "malattia_al", "malattia_evento_n", "malattia_esente", "malattia_inps", "malattia_carenza",
           "maternita_dal", "maternita_al", "maternita_inps"]
TFR_USCITA = ["fondo_tfr_prec", "tfr_quote_anno", "imponibile_anno", "tfr_liquidato"]
# IRPEF: le somme del cuneo e il trattamento integrativo in ogni cedolino (0 se non spettano); alla cessazione
# l'imponibile fiscale da gennaio, i giorni di lavoro e quanto già trattenuto o erogato nei mesi prima (F24-F29)
FISCO = ["bonus_cuneo", "trattamento_integrativo"]
CONGUAGLIO = ["imponibile_fiscale_anno", "giorni_lavoro_anno", "ritenute_anno_prec", "cuneo_anno_prec",
              "ti_anno_prec"]
PERMESSI = ["permessi_maturati", "permessi_goduti", "permessi_residuo"]
# Il mese con un'assenza (v2.2): la retribuzione tolta per i giorni di assenza e l'integrazione del datore di lavoro
INTEGRAZIONE = ["assenza_trattenuta", "integrazione_datore"]
# Voci del lordo oltre alla retribuzione del mese, con il segno; le indennità INPS non sono imponibile previdenziale
VOCI_LORDO = (("tredicesima", 1), ("quattordicesima", 1), ("ferie_liquidate", 1), ("assenza_trattenuta", -1),
              ("malattia_inps", 1), ("malattia_carenza", 1), ("maternita_inps", 1), ("integrazione_datore", 1))
INDENNITA_INPS = ("malattia_inps", "maternita_inps")


def _num(m: pd.DataFrame, c: str) -> pd.Series:
    return pd.to_numeric(m[c], errors="coerce").fillna(0.0) if c in m else pd.Series(0.0, index=m.index)


def carica() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ced = pd.read_csv(C.CEDOLINI, dtype={"livello": str, "evento": str,
                                         **{c: str for c in CESSAZIONE + ASSENZE + TFR_USCITA + CONGUAGLIO + INTEGRAZIONE}},
                      keep_default_na=False)
    return (ced[ced["mese"] == C.MESE].reset_index(drop=True), ced[ced["mese"] == C.MESE_PRECEDENTE],
            pd.read_csv(C.F24))


def attesi(m: pd.DataFrame, prec: pd.DataFrame) -> pd.DataFrame:
    """Il valore atteso di ogni voce controllata, calcolato dalle regole e non dal cedolino."""
    a = m[["matricola", "cliente", "livello", "part_time"]].copy()
    k = [R.ccnl_cliente(c) for c in m["cliente"]]
    a["tabellare"] = [R.centesimi(R.tabella(c).loc[lv, R.regola(c)["minimo"]] * p)
                      for lv, p, c in zip(m["livello"], m["part_time"], k, strict=True)]
    a["scatti_n"] = [R.scatti_maturati(date.fromisoformat(d), C.MESE, c)
                     for d, c in zip(m["data_assunzione"], k, strict=True)]
    a["scatti"] = [R.centesimi(R.tabella(c).loc[lv, "scatto"] * n * p)
                   for lv, n, p, c in zip(m["livello"], a["scatti_n"], m["part_time"], k, strict=True)]
    previdenziale = (m["lordo"] - sum(_num(m, c) for c in INDENNITA_INPS)).map(R.centesimi)
    a["contributi_inps"] = [R.contributi_cliente(x, c) for x, c in zip(previdenziale, m["cliente"], strict=True)]
    ordinaria = m["tabellare"] + m["scatti"] + m["superminimo"]
    a["quota_tfr"] = [R.quota_tfr(o, sc, c) for o, sc, c in zip(ordinaria, m["scatti"], k, strict=True)]
    residuo_prec = m["matricola"].map(prec.set_index("matricola")["ferie_residuo"]).fillna(0.0)
    assunti = [date.fromisoformat(d) for d in m["data_assunzione"]]
    fine = R.ultimo_del_mese(C.MESE)
    a["ferie_maturate"] = [R.ferie_mese(c, R.anni_di_servizio(d, fine)) for d, c in zip(assunti, k, strict=True)]
    a["ferie_residuo"] = (residuo_prec + a["ferie_maturate"] - m["ferie_godute"]).round(4)
    extra = sum(s_ * _num(m, c) for c, s_ in VOCI_LORDO)
    a["lordo"] = (ordinaria + m["straordinari"] + extra).map(R.centesimi)
    somme = sum(m.get(c, 0.0) for c in FISCO)
    a["netto"] = (m["lordo"] - m["contributi_inps"] - m["irpef"] - m["altre_trattenute"] + somme).map(R.centesimi)
    a["netto_prec"] = m["matricola"].map(prec.set_index("matricola")["netto"])
    a["variazione"] = m["netto"] / a["netto_prec"] - 1
    uscite = (m["data_cessazione"] if "data_cessazione" in m else pd.Series([""] * len(m), index=m.index))
    ratei = [R.ratei_al(d, C.MESE, None if _vuoto(u) else date.fromisoformat(str(u)), c)
             for d, u, c in zip(assunti, uscite, k, strict=True)]
    a["ratei_13"] = [r[0] for r in ratei]
    a["ratei_14"] = [r[1] for r in ratei]
    if "permessi_residuo" in m:
        res_prec = m["matricola"].map(prec.set_index("matricola")["permessi_residuo"]).fillna(0.0)
        a["permessi_maturati"] = [R.permessi_mese(d, C.MESE, C.CLIENTI[cl]["dipendenti"], p, c)
                                  for d, cl, p, c in zip(assunti, m["cliente"], m["part_time"], k, strict=True)]
        a["permessi_residuo"] = (res_prec + a["permessi_maturati"] - m["permessi_goduti"]).round(4)
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
        _fisco(m.loc[i], segnala, i)
        _assenze(m.loc[i], prev_by.get(m.loc[i, "matricola"]), segnala, i)
        if "permessi_residuo" in m and abs(m.loc[i, "permessi_residuo"]
                                           - a.loc[i, "permessi_residuo"]) > C.TOLLERANZA_ORE:
            segnala(i, "C18", float(a.loc[i, "permessi_residuo"]), float(m.loc[i, "permessi_residuo"]))
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
    k = R.ccnl_cliente(r.get("cliente"))
    assunzione = date.fromisoformat(str(r["data_assunzione"]))
    mensile = R.centesimi(r["tabellare"] + r["scatti"] + r["superminimo"])
    ces = None if _vuoto(r.get("data_cessazione")) else date.fromisoformat(str(r["data_cessazione"]))
    for voce, inizio, ratei, base in (("tredicesima", R.inizio_13, R.ratei_13, mensile),
                                      ("quattordicesima", R.inizio_14, R.dodicesimi_14_pagata,
                                       R.base_quattordicesima(mensile, r["scatti"], k))):
        if _vuoto(r.get(voce)):
            continue
        n = R.dodicesimi_alla_cessazione(assunzione, ces, inizio(ces), k) if ces else ratei(assunzione, C.MESE, k)
        if voce == "quattordicesima" and not R.ha_quattordicesima(k):
            n = 0
        atteso, trovato = R.mensilita_aggiuntiva(base, n), float(r[voce])
        if abs(trovato - atteso) > C.TOLLERANZA:
            segnala(i, "C12", atteso, trovato)
            break
    if ces is None:
        return
    if not _vuoto(r.get("ferie_liquidate")):
        atteso, trovato = R.ferie_non_godute(mensile, r["ferie_residuo"], k), float(r["ferie_liquidate"])
        if abs(trovato - atteso) > C.TOLLERANZA:
            segnala(i, "C13", atteso, trovato)
    tipo = str(r.get("tipo_cessazione", "")).strip().lower()
    if tipo in C.PREAVVISO and not _vuoto(r.get("preavviso_giorni")):
        minimo = R.preavviso_minimo(tipo, str(r["livello"]), assunzione, ces, k)
        if int(float(r["preavviso_giorni"])) < minimo:
            segnala(i, "C14", float(minimo), float(r["preavviso_giorni"]))
    if all(not _vuoto(r.get(c)) for c in TFR_USCITA):
        atteso = R.tfr_liquidato(float(r["fondo_tfr_prec"]), float(r["tfr_quote_anno"]),
                                 float(r["imponibile_anno"]), ces)
        if atteso is not None and abs(float(r["tfr_liquidato"]) - atteso) > C.TOLLERANZA:
            segnala(i, "C19", atteso, float(r["tfr_liquidato"]))


def _fisco(r: pd.Series, segnala, i: int) -> None:
    """C20 sul cedolino di un mese qualsiasi, C21 su quello di uscita quando riporta i dati del conguaglio. Una sola
    segnalazione per cedolino, sulla prima voce che non torna: ritenuta, poi cuneo, poi trattamento integrativo."""
    if any(c not in r for c in FISCO):
        return
    trovato = {"irpef": float(r["irpef"]), **{c: float(r[c]) for c in FISCO}}
    if _vuoto(r.get("data_cessazione")):
        codice, atteso = "C20", R.irpef_mese(float(r["imponibile_irpef"]),
                                             R.regola(R.ccnl_cliente(r.get("cliente")))["mensilita"])
    elif all(not _vuoto(r.get(c)) for c in CONGUAGLIO):
        codice, atteso = "C21", R.conguaglio_cessazione(*(float(r[c]) for c in CONGUAGLIO))
    else:
        return
    for voce in ("irpef", *FISCO):
        if abs(trovato[voce] - atteso[voce]) > C.TOLLERANZA:
            segnala(i, codice, atteso[voce], trovato[voce])
            return


def _si(v) -> bool:
    return str(v).strip().lower() in ("true", "vero", "1", "si", "sì", "yes", "x")


def _assenze(r: pd.Series, prec, segnala, i: int) -> None:
    """C15-C17: le indennità anticipate per conto dell'INPS e la carenza, quando il cedolino riporta l'evento. La
    base è la retribuzione del mese prima: senza il suo cedolino, o per un evento iniziato prima, non si controlla.
    C22: l'integrazione del datore di lavoro, con le regole del CCNL del cliente."""
    k = R.ccnl_cliente(r.get("cliente"))
    inizio = R.primo_del_mese(C.MESE)
    base = None if prec is None else R.centesimi(prec["tabellare"] + prec["scatti"] + prec["superminimo"])
    scatti_prec = 0.0 if prec is None else float(prec["scatti"])
    mensile = R.centesimi(r["tabellare"] + r["scatti"] + r["superminimo"])
    malattia, quota = None, 0.0
    if not _vuoto(r.get("malattia_dal")):
        dal, al = date.fromisoformat(str(r["malattia_dal"])), date.fromisoformat(str(r["malattia_al"]))
        if base is not None and dal >= inizio and not _vuoto(r.get("malattia_inps")):
            atteso = R.indennita_malattia(base, dal, al, C.MESE, scatti_prec, k)
            if abs(float(r["malattia_inps"]) - atteso) > C.TOLLERANZA:
                segnala(i, "C15", atteso, float(r["malattia_inps"]))
        carenza, _, _ = R.giorni_malattia(dal, al, C.MESE, k)
        if carenza and not _vuoto(r.get("malattia_evento_n")):
            quota = R.carenza_percentuale(int(float(r["malattia_evento_n"])), _si(r.get("malattia_esente")), k,
                                          (al - dal).days + 1)
            pagata = 0.0 if _vuoto(r.get("malattia_carenza")) else float(r["malattia_carenza"])
            if (quota == 0 and pagata > C.TOLLERANZA) or (quota > 0 and pagata <= C.TOLLERANZA):
                segnala(i, "C16", f"{quota:.0%}" if quota else "non dovuta", pagata)
        if dal >= inizio:
            malattia = (dal, al)
    maternita = False
    if not _vuoto(r.get("maternita_dal")) and not _vuoto(r.get("maternita_inps")) and base is not None:
        dal, al = date.fromisoformat(str(r["maternita_dal"])), date.fromisoformat(str(r["maternita_al"]))
        if dal >= inizio:
            maternita = True
            atteso = R.indennita_maternita(base, dal, al, C.MESE, scatti_prec, k)
            if abs(float(r["maternita_inps"]) - atteso) > C.TOLLERANZA:
                segnala(i, "C17", atteso, float(r["maternita_inps"]))
    # C22: solo se il cedolino porta la retribuzione tolta per l'assenza, cioè è un cedolino del mese con l'assenza
    if (malattia is None and not maternita) or _vuoto(r.get("assenza_trattenuta")):
        return
    integrazione = 0.0 if _vuoto(r.get("integrazione_datore")) else float(r["integrazione_datore"])
    q = R.quota_netto_garantita(C.MESE, k, malattia, quota) if malattia else R.quota_netto_garantita(C.MESE, k)
    if q is not None:
        garantito = R.netto_garantito(mensile, r["cliente"], q)
        effettivo = R.centesimi(float(r["netto"]) + float(r["altre_trattenute"]))
        if effettivo < garantito - C.TOLLERANZA:
            segnala(i, "C22", garantito, effettivo)
    elif malattia:
        inps = 0.0 if _vuoto(r.get("malattia_inps")) else float(r["malattia_inps"])
        attesa = R.integrazione_lorda(mensile, inps, *malattia, C.MESE, k)
        if attesa is not None and integrazione < attesa - C.TOLLERANZA:
            segnala(i, "C22", attesa, integrazione)


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
    # solo i clienti con un CCNL che ha una tranche alla data (nei dati d'esempio: il Terziario)
    m = m[[R.regola(R.ccnl_cliente(c))["prossima_tranche"] == C.PROSSIMA_TRANCHE for c in m["cliente"]]]
    if "data_cessazione" in m:          # chi lascia prima della tranche non la riceve
        resta = [_vuoto(d) or date.fromisoformat(str(d)) >= C.PROSSIMA_TRANCHE for d in m["data_cessazione"]]
        m = m[resta]
    n = m[["matricola", "cliente", "livello", "part_time", "superminimo", "superminimo_assorbibile"]].copy()
    n["superminimo_assorbibile"] = n["superminimo_assorbibile"].astype(str).str.lower() == "true"
    n["aumento"] = [R.centesimi((t.loc[lv, R.regola(R.T)['minimo_prossimo']] - t.loc[lv, R.regola(R.T)['minimo']]) * p)
                    for lv, p in zip(n["livello"], n["part_time"], strict=True)]
    n["assorbito"] = [min(s, a) if ok else 0.0 for s, a, ok in zip(n["superminimo"], n["aumento"],
                                                                    n["superminimo_assorbibile"], strict=True)]
    n["da_pagare"] = (n["aumento"] - n["assorbito"]).map(R.centesimi)
    n["nuovo_tabellare"] = [R.centesimi(t.loc[lv, R.regola(R.T)['minimo_prossimo']] * p)
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
