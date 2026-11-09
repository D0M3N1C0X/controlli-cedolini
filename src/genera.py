"""
Genera i dati sintetici: tre clienti, 119 dipendenti, i cedolini di agosto e settembre 2026 e gli
F24 di settembre. Agosto è corretto; a settembre vengono inseriti errori di tipo noto, registrati
in data/errori_inseriti.csv, così si può misurare quanti ne trovano i controlli e quanti falsi
allarmi danno. Ci sono anche casi legittimi che non devono essere segnalati: assunzioni del mese,
straordinari dichiarati, un passaggio a part-time.

    python src/genera.py
"""
import calendar
import math
import random
from datetime import date, timedelta

import pandas as pd

import codice_fiscale
import config as C
import regole as R
from controlli import ASSENZE, CONGUAGLIO, INTEGRAZIONE, TFR_USCITA

LIVELLI = C.CCNL["terziario"]["livelli"]
PESI_LIVELLO = C.CCNL["terziario"]["pesi"]


def ccnl(r) -> str:
    return R.ccnl_cliente(r["cliente"])


def mensilita(r) -> int:
    return R.regola(ccnl(r))["mensilita"]


def fisco(r: dict, **kw) -> dict:
    """Dall'imponibile fiscale: ritenuta IRPEF del mese, somma del cuneo, trattamento integrativo (C20), altre
    trattenute e netto. `kw` passa a R.irpef_mese, per gli errori inseriti."""
    r.update(R.irpef_mese(r["imponibile_irpef"], mensilita(r), **kw))
    return netto(r)


def netto(r: dict) -> dict:
    r["altre_trattenute"] = R.centesimi(r["imponibile_irpef"] * 0.015)
    r["netto"] = R.centesimi(r["imponibile_irpef"] - r["irpef"] - r["altre_trattenute"] + r["bonus_cuneo"]
                             + r["trattamento_integrativo"])
    return r


def anagrafica(rng: random.Random, clienti=C.CLIENTI_V1, n: int = 0) -> pd.DataFrame:
    rows = []
    for cliente in clienti:
        info = C.CLIENTI[cliente]
        g = R.regola(info["ccnl"])
        for _ in range(info["dipendenti"]):
            n += 1
            donna = rng.random() < 0.52
            nascita = date(rng.randint(1962, 2003), rng.randint(1, 12), rng.randint(1, 28))
            assunzione = date(rng.randint(max(nascita.year + 19, 1995), 2026), rng.randint(1, 12), rng.randint(1, 28))
            if assunzione > date(2026, 7, 31):
                assunzione = date(rng.randint(2012, 2025), rng.randint(1, 12), rng.randint(1, 28))
            livello = rng.choices(g["livelli"], g["pesi"])[0]
            pt = (rng.choices([1.0, 0.75, 0.5], [70, 20, 10])[0]
                  if livello not in ("Quadri", "Qa", "Qb", "1", "A1", "B3") else 1.0)
            superminimo = R.centesimi(rng.choice([0, 0, 0, 50, 80, 120, 150, 200, 300]) * pt)
            rows.append({"matricola": f"{cliente}{n:03d}", "cliente": cliente,
                         "codice_fiscale": codice_fiscale.sintetico(rng, nascita, donna),
                         "sesso": "F" if donna else "M", "livello": livello,
                         "data_assunzione": assunzione.isoformat(), "part_time": pt, "superminimo": superminimo,
                         "superminimo_assorbibile": rng.random() < 0.7})
    a = pd.DataFrame(rows)
    if clienti != C.CLIENTI_V1:
        return a
    # casi che il mese di settembre deve contenere: trienni compiuti ad agosto 2026 (scatto da settembre)
    for i in rng.sample(range(len(a)), 9):
        y = rng.choice([2023, 2020, 2017])
        a.loc[i, "data_assunzione"] = date(y, 8, rng.randint(1, 28)).isoformat()
    return a


def cedolino(d: pd.Series, mese: str, rng: random.Random, residuo_prec: float, straordinari: float = 0.0,
             ferie_godute: float = 0.0, part_time: float | None = None, permessi_prec: float = 0.0,
             permessi_goduti: float = 0.0) -> dict:
    pt = d["part_time"] if part_time is None else part_time
    assunzione = date.fromisoformat(d["data_assunzione"])
    k = ccnl(d)
    n = R.scatti_maturati(assunzione, mese, k)
    tab = R.tabellare(d["livello"], pt, ccnl=k)
    sc = R.scatti_importo(d["livello"], n, pt, k)
    ordinaria = R.centesimi(tab + sc + d["superminimo"])
    lordo = R.centesimi(ordinaria + straordinari)
    inps = R.contributi_cliente(lordo, d["cliente"])
    permessi = R.permessi_mese(assunzione, mese, C.CLIENTI[d["cliente"]]["dipendenti"], pt, k)
    imponibile = R.centesimi(lordo - inps)
    maturate = R.ferie_mese(k, R.anni_di_servizio(assunzione, R.ultimo_del_mese(mese)))
    return fisco({"mese": mese, "matricola": d["matricola"], "cliente": d["cliente"],
                  "codice_fiscale": d["codice_fiscale"],
            "livello": d["livello"], "data_assunzione": d["data_assunzione"], "part_time": pt,
            "superminimo_assorbibile": d["superminimo_assorbibile"], "evento": "",
            "tabellare": tab, "scatti_n": n, "scatti": sc, "superminimo": d["superminimo"],
            "straordinari": straordinari, "lordo": lordo, "contributi_inps": inps, "imponibile_irpef": imponibile,
            "quota_tfr": R.quota_tfr(ordinaria, sc, k), "ferie_maturate": maturate, "ferie_godute": ferie_godute,
            "ferie_residuo": round(residuo_prec + maturate - ferie_godute, 4),
            "ratei_13": R.ratei_13(assunzione, mese, k), "ratei_14": R.ratei_14(assunzione, mese, k),
            # voci della cessazione: vuote finché il dipendente resta
            "data_cessazione": "", "tipo_cessazione": "", "preavviso_giorni": "", "tredicesima": "",
            "quattordicesima": "", "ferie_liquidate": "",
            # assenze del mese, TFR e conguaglio alla cessazione: vuoti se non ci sono
            **{c: "" for c in ASSENZE + TFR_USCITA + CONGUAGLIO + INTEGRAZIONE},
            "permessi_maturati": permessi, "permessi_goduti": permessi_goduti,
            "permessi_residuo": round(permessi_prec + permessi - permessi_goduti, 4)})


def _importo(v) -> float:
    return 0.0 if v in ("", None) or (isinstance(v, float) and v != v) else float(v)


# voci che entrano nel lordo, con il segno: le mensilità e le ferie pagate all'uscita, e le voci del mese con
# un'assenza (v2.2): via la retribuzione dei giorni di assenza, dentro indennità INPS, carenza e integrazione
VOCI_LORDO = (("tredicesima", 1), ("quattordicesima", 1), ("ferie_liquidate", 1), ("assenza_trattenuta", -1),
              ("malattia_inps", 1), ("malattia_carenza", 1), ("maternita_inps", 1), ("integrazione_datore", 1))
INDENNITA_INPS = ("malattia_inps", "maternita_inps")       # non sono imponibile previdenziale (F41)


def ricalcola(r: dict) -> dict:
    """Dopo una modifica a monte, rifà a cascata le voci che il software paghe deriverebbe."""
    ordinaria = R.centesimi(r["tabellare"] + r["scatti"] + r["superminimo"])
    r["lordo"] = R.centesimi(ordinaria + r["straordinari"] + sum(s * _importo(r.get(k)) for k, s in VOCI_LORDO))
    previdenziale = R.centesimi(r["lordo"] - sum(_importo(r.get(k)) for k in INDENNITA_INPS))
    r["contributi_inps"] = R.contributi_cliente(previdenziale, r["cliente"])
    r["imponibile_irpef"] = R.centesimi(r["lordo"] - r["contributi_inps"])
    fisco(r)
    r["quota_tfr"] = R.quota_tfr(ordinaria, r["scatti"], ccnl(r))
    return r


def _eur(x: float) -> str:
    return f"{x:.2f}"


def chiudi_assenza(r: dict, quota_netto: float | None, integrazione: float | None = None) -> dict:
    """Integrazione del datore di lavoro e ricalcolo del cedolino del mese con un'assenza. Sul netto (Terziario): la
    più piccola integrazione, al centesimo, che porta il netto prima delle altre trattenute alla quota garantita del
    netto normale; sul lordo (Metalmeccanico, Logistica) quella delle regole; `integrazione` la impone (errori)."""
    if integrazione is None and quota_netto is not None:
        mensile = R.centesimi(r["tabellare"] + r["scatti"] + r["superminimo"])
        obiettivo = R.netto_garantito(mensile, r["cliente"], quota_netto)
        prova = lambda cent: ricalcola({**r, "integrazione_datore": _eur(cent / 100)})   # noqa: E731
        lo, hi = 0, int(mensile * 100) + 1
        while lo < hi:
            mid = (lo + hi) // 2
            t = prova(mid)
            if t["netto"] + t["altre_trattenute"] >= obiettivo:
                hi = mid
            else:
                lo = mid + 1
        integrazione = lo / 100
    r["integrazione_datore"] = _eur(integrazione or 0.0)
    return ricalcola(r)


def malattia_mese(r: dict, base: dict, dal: date, al: date, evento_n: int, esente: bool = False,
                  inps: float | None = None, carenza: float | None = None, integrazione: float | None = None,
                  quota_lorda: tuple | None = None) -> dict:
    """Il cedolino del mese con una malattia (C15, C16, C22): via la retribuzione dei giorni di assenza, dentro
    l'indennità INPS sulla retribuzione del mese prima (`base`), la carenza alla quota del CCNL e l'integrazione del
    datore. `inps`, `carenza`, `integrazione` e `quota_lorda` (quote sbagliate dell'integrazione lorda) servono agli
    errori inseriti."""
    k = ccnl(r)
    mensile = R.centesimi(r["tabellare"] + r["scatti"] + r["superminimo"])
    base_ret = R.centesimi(base["tabellare"] + base["scatti"] + base["superminimo"])
    n_car, n1, n2 = R.giorni_malattia(dal, al, C.MESE, k)
    quota = R.carenza_percentuale(evento_n, esente, k, (al - dal).days + 1)
    dovuta_inps = R.indennita_malattia(base_ret, dal, al, C.MESE, base["scatti"], k) if inps is None else inps
    r.update({"malattia_dal": dal.isoformat(), "malattia_al": al.isoformat(), "malattia_evento_n": str(evento_n),
              "malattia_esente": "true" if esente else "false", "malattia_inps": _eur(dovuta_inps),
              "malattia_carenza": _eur(R.importo_carenza(mensile, n_car, quota, C.MESE) if carenza is None
                                       else carenza),
              "assenza_trattenuta": _eur(R.trattenuta_assenza(mensile, R.giorni_assenza(dal, al, C.MESE), C.MESE)),
              "evento": "malattia"})
    if integrazione is None and quota_lorda is not None:
        q1, q2 = quota_lorda
        integrazione = R.centesimi(max(0.0, mensile * (n1 * q1 + n2 * q2) / R.giorni_del_mese(C.MESE)
                                       - dovuta_inps))
    if integrazione is None:
        integrazione = R.integrazione_lorda(mensile, dovuta_inps, dal, al, C.MESE, k)
    return chiudi_assenza(r, R.quota_netto_garantita(C.MESE, k, (dal, al), quota), integrazione)


def maternita_mese(r: dict, base: dict, dal: date, inps: float | None = None) -> dict:
    """Il cedolino del mese di congedo di maternità: via la retribuzione dei giorni, dentro l'indennità INPS all'80%
    e, nel Terziario, l'integrazione fino al 100% del netto (F18)."""
    k = ccnl(r)
    al = dal + timedelta(days=149)                       # cinque mesi di congedo obbligatorio
    mensile = R.centesimi(r["tabellare"] + r["scatti"] + r["superminimo"])
    base_ret = R.centesimi(base["tabellare"] + base["scatti"] + base["superminimo"])
    importo = R.indennita_maternita(base_ret, dal, al, C.MESE, base["scatti"], k) if inps is None else inps
    r.update({"maternita_dal": dal.isoformat(), "maternita_al": al.isoformat(), "maternita_inps": _eur(importo),
              "assenza_trattenuta": _eur(R.trattenuta_assenza(mensile, R.giorni_assenza(dal, al, C.MESE), C.MESE)),
              "evento": "maternità"})
    q = R.quota_netto_garantita(C.MESE, k)
    return chiudi_assenza(r, q, None if q is not None else 0.0)


def cessazione(r: dict, tipo: str, uscita: date, errore: str = "", preavviso: float | None = None) -> dict:
    """Il cedolino di chi lascia (C11-C14): ratei fino all'uscita, tredicesima e quattordicesima, ferie non godute e
    preavviso del CCNL. `errore` e `preavviso` servono agli errori inseriti."""
    k = ccnl(r)
    assunzione = date.fromisoformat(r["data_assunzione"])
    mensile = R.centesimi(r["tabellare"] + r["scatti"] + r["superminimo"])
    n13, n14 = R.ratei_al(assunzione, C.MESE, uscita, k)
    minimo = math.ceil(R.preavviso_minimo(tipo, r["livello"], assunzione, uscita, k))
    base14 = R.base_quattordicesima(mensile, r["scatti"], k)
    r.update({"evento": "cessazione", "data_cessazione": uscita.isoformat(), "tipo_cessazione": tipo,
              "ratei_13": n13, "ratei_14": n14,
              "preavviso_giorni": minimo if preavviso is None else preavviso,
              "tredicesima": R.mensilita_aggiuntiva(mensile, n13),
              "quattordicesima": R.mensilita_aggiuntiva(base14, n14) if R.ha_quattordicesima(k) else "",
              "ferie_liquidate": R.ferie_non_godute(mensile, r["ferie_residuo"], k)})
    if errore == "ferie":
        r["ferie_liquidate"] = R.centesimi(mensile / 30 * r["ferie_residuo"])
    elif errore == "ferie_26":
        r["ferie_liquidate"] = R.centesimi(mensile / C.DIVISORE_GIORNALIERO * r["ferie_residuo"])
    elif errore == "quattordicesima":
        r["quattordicesima"] = R.mensilita_aggiuntiva(mensile, n13)
    elif errore == "quattordicesima_scatti":
        r["quattordicesima"] = R.mensilita_aggiuntiva(mensile, n14)
    elif errore == "preavviso":
        r["preavviso_giorni"] = minimo // 2
    return ricalcola(r)


def tfr_uscita(r: dict, rng2: random.Random, errore: str = "") -> tuple[list, str]:
    """TFR alla cessazione (C19): fondo al 31 dicembre 2025, quote del 2026 fino all'uscita e imponibile dello stesso
    periodo; poi il TFR liquidato con la rivalutazione ISTAT. `errore` per gli errori inseriti."""
    assunto, uscita = date.fromisoformat(r["data_assunzione"]), date.fromisoformat(r["data_cessazione"])
    mensile = R.centesimi(r["tabellare"] + r["scatti"] + r["superminimo"])
    anni = R.anni_di_servizio(assunto, date(2025, 12, 31))
    mesi = R.dodicesimi_alla_cessazione(assunto, uscita, date(2026, 1, 1), ccnl(r))
    fondo = R.centesimi(mensile * mensilita(r) / C.DIVISORE_TFR * anni * rng2.uniform(0.96, 1.08))
    quote, imponibile = R.centesimi(r["quota_tfr"] * mesi), R.centesimi(r["lordo"] * mesi)
    liquidato = R.tfr_liquidato(fondo, quote, imponibile, uscita)
    nota = ""
    if errore == "coefficiente":       # il coefficiente del mese di uscita anche se si esce prima del 15
        c = R.coefficiente_tfr(date(uscita.year, uscita.month, 15))
        riv = R.centesimi(fondo * c / 100)
        liquidato = R.centesimi(fondo + riv - R.centesimi(riv * C.IMPOSTA_SOSTITUTIVA_TFR) + quote
                                - R.centesimi(imponibile * C.CONTRIBUTO_TFR))
        nota = "uscita prima del 15 rivalutata con il coefficiente del mese di uscita invece che del mese prima"
    elif errore == "imposta":           # rivalutazione lorda: imposta sostitutiva non tolta
        riv = R.centesimi(fondo * R.coefficiente_tfr(uscita) / 100)
        liquidato = R.centesimi(fondo + riv + quote - R.centesimi(imponibile * C.CONTRIBUTO_TFR))
        nota = "rivalutazione liquidata senza togliere l'imposta sostitutiva del 17%"
    elif errore == "contributo":        # quote dell'anno senza lo 0,50%
        riv = R.centesimi(fondo * R.coefficiente_tfr(uscita) / 100)
        liquidato = R.centesimi(fondo + riv - R.centesimi(riv * C.IMPOSTA_SOSTITUTIVA_TFR) + quote)
        nota = "quote dell'anno senza togliere il contributo dello 0,50% dell'imponibile"
    return [f"{fondo:.2f}", f"{quote:.2f}", f"{imponibile:.2f}", f"{liquidato:.2f}"], nota


def conguaglio_uscita(r: dict, agosto: dict, errore: str = "") -> tuple[dict, str]:
    """Conguaglio IRPEF alla cessazione (C21): l'imponibile da gennaio, i giorni di lavoro e quanto già trattenuto o
    erogato nei mesi prima (ogni mese come agosto, con le regole di C20); il cedolino di uscita porta la differenza."""
    inizio_anno = date(R.primo_del_mese(C.MESE).year, 1, 1)
    assunto, uscita = date.fromisoformat(r["data_assunzione"]), date.fromisoformat(r["data_cessazione"])
    dal = max(assunto, inizio_anno)
    mesi_prec = (R.primo_del_mese(C.MESE).month - dal.month) if dal.year == inizio_anno.year else 0
    g = R.irpef_mese(agosto["imponibile_irpef"], mensilita(r))
    prec = {k: R.centesimi(g[k] * mesi_prec) for k in ("irpef", "bonus_cuneo", "trattamento_integrativo")}
    imp_anno = R.centesimi(agosto["imponibile_irpef"] * mesi_prec + r["imponibile_irpef"])
    giorni = (uscita - dal).days + 1
    if errore == "non_fatto":
        r.update(R.irpef_mese(r["imponibile_irpef"], mensilita(r)))
        nota = "conguaglio non fatto alla cessazione: ritenuta calcolata come in un mese qualsiasi"
    else:
        c = R.conguaglio_cessazione(imp_anno, giorni, prec["irpef"], prec["bonus_cuneo"],
                                    prec["trattamento_integrativo"], rapporta=errore != "detrazioni")
        r.update({k: c[k] for k in ("irpef", "bonus_cuneo", "trattamento_integrativo")})
        nota = "conguaglio con le detrazioni dell'anno intero invece che rapportate ai giorni di lavoro"
    r.update(dict(zip(CONGUAGLIO, [f"{imp_anno:.2f}", str(giorni), f"{prec['irpef']:.2f}",
                                   f"{prec['bonus_cuneo']:.2f}", f"{prec['trattamento_integrativo']:.2f}"],
                      strict=True)))
    return netto(r), nota


def clienti_v22(errori: list) -> tuple[list, pd.DataFrame, pd.DataFrame]:
    """I clienti D, E e F (v2.2), uno per CCNL, con un generatore a parte: i dati dei clienti A-C non cambiano. Per
    ogni CCNL gli errori tipici di chi applica le regole di un altro contratto, e casi corretti che non vanno
    segnalati."""
    rng = random.Random(C.SEED + 2)
    a = anagrafica(rng, ("D", "E", "F"), n=300)
    speciali = {          # casi che settembre deve contenere
        "D": [("2026-04-16", "C2"),       # 15 giorni di servizio ad aprile: nel Metalmeccanico il mese non conta
              ("2022-05-10", "C3"),       # due bienni compiuti: con la regola triennale del Terziario sarebbe uno
              ("2012-03-10", "B1"),       # oltre 10 anni: un giorno di ferie in più
              ("2024-08-05", "B2")],      # biennio compiuto ad agosto: scatto da settembre
        "E": [("2023-03-01", "4"),        # assunto dopo il 2018, da 3 anni: metà della riduzione d'orario
              ("2026-07-20", "5")],       # entra a luglio, esce il 10 settembre: le frazioni si sommano
        "F": [("2025-02-03", "2")],
    }
    for cliente, casi in speciali.items():
        righe = a.index[a["cliente"] == cliente]
        for k, (data, livello) in enumerate(casi):
            a.loc[righe[k], ["data_assunzione", "livello", "part_time"]] = [data, livello, 1.0]
    ago, sett = [], []
    for _, d in a.iterrows():
        residuo = round(rng.uniform(12, 30), 4)
        g_ago = min(rng.choice([0, 5, 10]), int(residuo))
        p_res = round(rng.uniform(8, 50), 4)
        if d["data_assunzione"] >= "2026-07-01":       # entrato a luglio: un mese di ferie e permessi maturati
            residuo, g_ago, p_res = R.ferie_mese(R.ccnl_cliente(d["cliente"])), 0, 0.0
        nuovo = d["data_assunzione"] >= "2026-08-01"
        ago.append(cedolino(d, C.MESE_PRECEDENTE, rng, residuo, ferie_godute=g_ago, permessi_prec=p_res,
                            permessi_goduti=rng.choice([0, 0, 4])))
        sett.append(cedolino(d, C.MESE, rng, 0.0 if nuovo else ago[-1]["ferie_residuo"],
                             ferie_godute=rng.choice([0, 0, 1, 2]), permessi_prec=ago[-1]["permessi_residuo"],
                             permessi_goduti=rng.choice([0, 0, 0, 4])))
    S = pd.DataFrame(sett)
    for col in ASSENZE + TFR_USCITA + CONGUAGLIO + INTEGRAZIONE + ["data_cessazione", "tipo_cessazione",
                                                                    "preavviso_giorni", "tredicesima",
                                                                    "quattordicesima", "ferie_liquidate"]:
        S[col] = S[col].astype(object)
    idx = list(S.index)
    rng.shuffle(idx)
    # i casi speciali hanno già il loro ruolo: non li prende nessun altro errore
    usati: set = {S.loc[i, "matricola"] for i in S.index
                  if any(S.loc[i, "data_assunzione"] == d for casi in speciali.values() for d, _ in casi)}

    def prendi(cliente: str, cond=lambda r: True) -> int:
        for i in idx:
            r = S.loc[i]
            if r["cliente"] == cliente and r["matricola"] not in usati and r["evento"] == "" and cond(r):
                usati.add(r["matricola"])
                return i
        raise RuntimeError(f"dati insufficienti per il cliente {cliente}")

    def per_data(data: str) -> int:
        return int(S.index[S["data_assunzione"] == data][0])

    def registra(i, tipo, nota) -> None:
        errori.append({"matricola": S.loc[i, "matricola"], "cliente": S.loc[i, "cliente"], "tipo": tipo,
                       "nota": nota})

    inizio = R.primo_del_mese(C.MESE)
    giorno = lambda g: date(inizio.year, inizio.month, g)       # noqa: E731
    fine_mese = R.ultimo_del_mese(C.MESE)
    rifai = lambda i, r: S.loc.__setitem__(i, pd.Series(ricalcola(r)))     # noqa: E731

    def malattia(i, dal, al, evento_n, **kw) -> None:
        S.loc[i] = pd.Series(malattia_mese(S.loc[i].to_dict(), ago[i], giorno(dal), giorno(al), evento_n, **kw))

    def esce(i, tipo, uscita=fine_mese, errore="", preavviso=None) -> None:
        S.loc[i] = pd.Series(cessazione(S.loc[i].to_dict(), tipo, uscita, errore, preavviso))

    # D · Metalmeccanico industria, solo impiegati
    i = prendi("D")
    r = S.loc[i].to_dict()
    r["tabellare"] = R.tabellare(r["livello"], r["part_time"], "minimo_2025_06", "metalmeccanico")
    rifai(i, r)
    registra(i, "minimo", "minimo fermo a prima di giugno 2026: l'aumento IPCA e del rinnovo non applicato")
    i = per_data("2022-05-10")
    r = S.loc[i].to_dict()
    r["scatti_n"] = R.scatti_maturati(date(2022, 5, 10), C.MESE, "terziario")
    r["scatti"] = R.scatti_importo(r["livello"], r["scatti_n"], r["part_time"], "metalmeccanico")
    rifai(i, r)
    registra(i, "scatto", "scatti contati ogni tre anni come nel Terziario: nel Metalmeccanico sono biennali")
    i = per_data("2026-04-16")
    S.loc[i, "ratei_13"] += 1
    registra(i, "ratei", "mese di assunzione con 15 giorni di servizio contato: nel Metalmeccanico ne servono "
             "più di 15")
    i = per_data("2012-03-10")
    sbagliate = round(24 / 12, 4)
    S.loc[i, "ferie_residuo"] = round(S.loc[i, "ferie_residuo"] - S.loc[i, "ferie_maturate"] + sbagliate, 4)
    S.loc[i, "ferie_maturate"] = sbagliate
    registra(i, "ferie", "oltre 10 anni di servizio: il giorno di ferie in più non maturato")
    malattia(prendi("D"), 7, 12, 1)                                  # 6 giorni, primo evento: tutto al datore
    i = prendi("D")
    base = R.centesimi(ago[i]["tabellare"] + ago[i]["scatti"] + ago[i]["superminimo"])
    inps = R.indennita_malattia(base, giorno(14), giorno(25), C.MESE, ccnl="terziario")
    malattia(i, 14, 25, 2, inps=inps)
    registra(i, "malattia", "indennità INPS anticipata a un impiegato dell'industria, che non ne ha diritto")
    i = prendi("D")
    malattia(i, 3, 17, 1, quota_lorda=(0.8, 0.8))
    registra(i, "integrazione", "malattia pagata all'80%, la quota dopo i 122 giorni, dal primo giorno")
    esce(prendi("D"), "dimissioni")
    i = prendi("D", lambda r: r["livello"] in ("B2", "B3", "A1")
               and R.anni_di_servizio(date.fromisoformat(r["data_assunzione"]), fine_mese) < 5)
    esce(i, "licenziamento", preavviso=45)
    registra(i, "preavviso", "licenziamento di un B2-A1 con 1 mese e 15 giorni di preavviso: il minimo è 2 mesi")

    # E · Turismo, pubblici esercizi
    i = prendi("E")
    r = S.loc[i].to_dict()
    r["tabellare"] = R.tabellare(r["livello"], r["part_time"], "totale_2025_06", "turismo")
    rifai(i, r)
    registra(i, "minimo", "retribuzione ferma alla tranche di giugno 2025")
    malattia(prendi("E"), 2, 11, 1)                                  # 10 giorni: carenza pagata, INPS all'80%
    i = prendi("E")
    base = R.centesimi(ago[i]["tabellare"] + ago[i]["scatti"] + ago[i]["superminimo"])
    _, n1, n2 = R.giorni_malattia(giorno(15), giorno(28), C.MESE, "turismo")
    g = R.rmgg(base, ago[i]["scatti"], "turismo")
    malattia(i, 15, 28, 1, inps=R.centesimi(g * 0.5 * n1 + g * 0.6666 * n2))
    registra(i, "malattia", "indennità INPS al 50% come negli altri settori: nei pubblici esercizi è l'80%")
    i = prendi("E")
    malattia(i, 21, 27, 2, carenza=0.0)
    registra(i, "carenza", "malattia di 7 giorni: i primi 3 non pagati, ma oltre i 5 giorni il datore li deve")
    i = prendi("E", lambda r: r["scatti"] > 0 and r["ferie_residuo"] > 1)
    esce(i, "dimissioni", errore="quattordicesima_scatti")
    registra(i, "tredicesima", "quattordicesima liquidata con gli scatti: nel Turismo la base li esclude")
    esce(per_data("2026-07-20"), "dimissioni", uscita=giorno(10))    # le frazioni di luglio e settembre si sommano
    i = per_data("2023-03-01")
    r = S.loc[i]
    pieni = round((72 + 32) / 12, 4)
    S.loc[i, "permessi_residuo"] = round(r["permessi_residuo"] - r["permessi_maturati"] + pieni, 4)
    S.loc[i, "permessi_maturati"] = pieni
    registra(i, "permessi", "assunto nel 2023: matura 104 ore l'anno invece di 68 (32 più metà della riduzione)")

    # F · Logistica, trasporto merci e spedizione
    for _ in range(2):
        i = prendi("F")
        r = S.loc[i].to_dict()
        r["tabellare"] = R.tabellare(r["livello"], r["part_time"], "minimo_2026_01", "logistica")
        rifai(i, r)
        registra(i, "minimo", "minimo senza l'elemento perequativo (EPA) del rinnovo")
    malattia(prendi("F"), 9, 18, 1)                                  # integrazione fino al 100% del lordo
    i = prendi("F")
    malattia(i, 1, 24, 2, quota_lorda=(0.75, 1.0))
    registra(i, "integrazione", "integrazione al 75% dal 4° al 20° giorno, come nel Terziario: qui è il 100%")
    i = prendi("F", lambda r: r["livello"] in ("Quadri", "1", "2"))
    esce(i, "dimissioni", preavviso=15)
    registra(i, "preavviso", "dimissioni con 15 giorni di preavviso, quelli dei livelli più bassi")
    i = prendi("F", lambda r: r["ferie_residuo"] > 2)
    esce(i, "licenziamento", errore="ferie_26")
    registra(i, "ferie_liquidate", "ferie non godute pagate a 1/26: con la settimana di 5 giorni la quota è 1/22")

    for i in S.index[S["evento"] == "cessazione"]:
        S.loc[i, TFR_USCITA], _ = tfr_uscita(S.loc[i].to_dict(), rng)
        r, _ = conguaglio_uscita(S.loc[i].to_dict(), ago[i])
        S.loc[i] = pd.Series(r)
    return ago, S, a


def main() -> None:
    rng = random.Random(C.SEED)
    # un secondo generatore per i dati aggiunti dopo (permessi, assenze, TFR): così i casi già presenti non cambiano
    rng2 = random.Random(C.SEED + 1)
    a = anagrafica(rng)
    ago, set_ = [], []
    for _, d in a.iterrows():
        residuo = round(rng.uniform(12, 30), 4)
        g_ago = min(rng.choice([0, 5, 10, 10, 15]), int(residuo))
        p_res = round(rng2.uniform(8, 60), 4)
        p_ago, p_set = rng2.choice([0, 0, 4, 8]), rng2.choice([0, 0, 0, 4, 8])
        ago.append(cedolino(d, C.MESE_PRECEDENTE, rng, residuo, ferie_godute=g_ago, permessi_prec=p_res,
                            permessi_goduti=p_ago))
        set_.append(cedolino(d, C.MESE, rng, ago[-1]["ferie_residuo"], ferie_godute=rng.choice([0, 0, 0, 1, 2]),
                             permessi_prec=ago[-1]["permessi_residuo"], permessi_goduti=p_set))
    S = pd.DataFrame(set_)
    errori = []
    idx = list(S.index)
    rng.shuffle(idx)
    pool = iter(idx)

    def prendi(cond=lambda r: True) -> int:
        for i in pool:
            if cond(S.loc[i]):
                return i
        raise RuntimeError("dati insufficienti")

    def registra(i, tipo, nota) -> None:
        errori.append({"matricola": S.loc[i, "matricola"], "cliente": S.loc[i, "cliente"], "tipo": tipo, "nota": nota})

    # Casi legittimi, da NON segnalare
    for _ in range(4):        # straordinari dichiarati
        i = prendi(lambda r: r["part_time"] == 1.0)
        S.loc[i, "straordinari"] = R.centesimi(rng.uniform(400, 900))
        S.loc[i, "evento"] = "straordinari"
        S.loc[i] = pd.Series(ricalcola(S.loc[i].to_dict()))
    i = prendi(lambda r: r["part_time"] == 1.0 and r["livello"] not in ("Quadri", "1"))   # passaggio a part-time
    S.loc[i, "part_time"] = 0.5
    S.loc[i, "tabellare"] = R.tabellare(S.loc[i, "livello"], 0.5)
    S.loc[i, "scatti"] = R.scatti_importo(S.loc[i, "livello"], S.loc[i, "scatti_n"], 0.5)
    S.loc[i, "superminimo"] = R.centesimi(S.loc[i, "superminimo"] * 0.5)
    S.loc[i, "evento"] = "variazione part-time"
    prima = S.loc[i, "permessi_residuo"] - S.loc[i, "permessi_maturati"] + S.loc[i, "permessi_goduti"]
    S.loc[i, "permessi_maturati"] = R.permessi_mese(date.fromisoformat(S.loc[i, "data_assunzione"]), C.MESE,
                                                    C.CLIENTI[S.loc[i, "cliente"]]["dipendenti"], 0.5)
    S.loc[i, "permessi_residuo"] = round(prima + S.loc[i, "permessi_maturati"] - S.loc[i, "permessi_goduti"], 4)
    S.loc[i] = pd.Series(ricalcola(S.loc[i].to_dict()))
    nuovi = []
    for k in range(3):        # assunzioni di settembre: nessun cedolino ad agosto
        d = pd.Series({"matricola": f"B{200 + k}", "cliente": "B",
                       "codice_fiscale": codice_fiscale.sintetico(rng, date(2001, k + 2, 11), k == 1),
                       "livello": "5", "data_assunzione": "2026-09-01", "part_time": 1.0, "superminimo": 0.0,
                       "superminimo_assorbibile": True})
        r = cedolino(d, C.MESE, rng, 0.0)
        r["evento"] = "assunzione"
        nuovi.append(r)

    # Errori
    for _ in range(6):        # minimo non aggiornato alla tranche di novembre 2025
        i = prendi(lambda r: r["evento"] == "")
        S.loc[i, "tabellare"] = R.tabellare(S.loc[i, "livello"], S.loc[i, "part_time"], "minimo_2025_03")
        S.loc[i] = pd.Series(ricalcola(S.loc[i].to_dict()))
        registra(i, "minimo", "tabellare fermo alla tranche di marzo 2025")
    for i in S.index:         # scatto maturato ad agosto e non pagato
        nato = date.fromisoformat(S.loc[i, "data_assunzione"])
        if (nato.month == 8 and nato.year in (2023, 2020, 2017) and S.loc[i, "evento"] == ""
                and sum(e["tipo"] == "scatto" for e in errori) < 4
                and S.loc[i, "matricola"] not in {e["matricola"] for e in errori}):
            S.loc[i, "scatti_n"] -= 1
            S.loc[i, "scatti"] = R.scatti_importo(S.loc[i, "livello"], S.loc[i, "scatti_n"], S.loc[i, "part_time"])
            S.loc[i] = pd.Series(ricalcola(S.loc[i].to_dict()))
            registra(i, "scatto", "triennio compiuto ad agosto 2026, scatto non applicato da settembre")
    usati = lambda: {e["matricola"] for e in errori}
    libero = lambda r: r["evento"] == "" and r["matricola"] not in usati()

    def contributi_errati(i, importo: float) -> None:
        """Il software ha trattenuto un altro importo: imponibile fiscale, IRPEF e netto seguono."""
        r = S.loc[i].to_dict()
        r["contributi_inps"] = importo
        r["imponibile_irpef"] = R.centesimi(r["lordo"] - r["contributi_inps"])
        S.loc[i] = pd.Series(fisco(r))

    for cliente in ("B", "C", "B"):        # CIGS e FIS non trattenuti: solo l'IVS
        i = prendi(lambda r, cliente=cliente: libero(r) and r["cliente"] == cliente)
        contributi_errati(i, R.centesimi(R.euro(S.loc[i, "lordo"]) * C.ALIQUOTA_DIPENDENTE))
        registra(i, "inps", "aliquota 9,19%: CIGS (0,30%) e quota FIS (0,2667%) non trattenute")
    i = prendi(lambda r: libero(r) and r["cliente"] == "A")
    contributi_errati(i, R.contributi(S.loc[i, "lordo"], C.CLIENTI["B"]["media_semestre"]))
    registra(i, "inps", "CIGS trattenuta a un cliente con meno di 15 dipendenti di media nel semestre")
    for _ in range(3):        # TFR calcolato senza superminimo e scatti
        i = prendi(lambda r: libero(r) and (r["superminimo"] > 0 or r["scatti"] > 0))
        S.loc[i, "quota_tfr"] = R.quota_tfr(S.loc[i, "tabellare"])
        registra(i, "tfr", "quota TFR calcolata sul solo tabellare")
    for _ in range(3):        # residuo ferie non aggiornato
        i = prendi(libero)
        S.loc[i, "ferie_residuo"] = round(S.loc[i, "ferie_residuo"] - S.loc[i, "ferie_maturate"], 4)
        registra(i, "ferie", "maturazione del mese non sommata al residuo")
    for _ in range(2):        # netto che non torna
        i = prendi(libero)
        S.loc[i, "netto"] = R.centesimi(S.loc[i, "netto"] + rng.choice([-50, 37.5, 100]))
        registra(i, "netto", "netto diverso da imponibile - IRPEF - altre trattenute")
    for _ in range(2):        # straordinari pagati due volte, senza evento
        i = prendi(lambda r: libero(r) and r["part_time"] == 1.0)
        S.loc[i, "straordinari"] = R.centesimi(rng.uniform(900, 1300))
        S.loc[i] = pd.Series(ricalcola(S.loc[i].to_dict()))
        registra(i, "variazione", "straordinari inseriti senza evento: netto oltre il 20% sopra agosto")
    for _ in range(2):        # codice fiscale trascritto male
        i = prendi(libero)
        cf = S.loc[i, "codice_fiscale"]
        S.loc[i, "codice_fiscale"] = cf[:15] + ("A" if cf[15] != "A" else "B")
        registra(i, "codice_fiscale", "carattere di controllo errato")

    # anagrafica cambiata senza evento, cedolino ricalcolato in modo coerente: solo il confronto con il mese
    # prima lo vede
    i = prendi(lambda r: libero(r) and r["livello"] == "4")
    d = a.set_index("matricola").loc[S.loc[i, "matricola"]].copy()
    d["matricola"], d["livello"] = S.loc[i, "matricola"], "5"
    r = cedolino(d, C.MESE, rng, ago[i]["ferie_residuo"], ferie_godute=S.loc[i, "ferie_godute"])
    for k in ("livello", "tabellare", "scatti", "lordo", "contributi_inps", "imponibile_irpef", "irpef",
              "bonus_cuneo", "trattamento_integrativo", "altre_trattenute", "netto", "quota_tfr"):
        S.loc[i, k] = r[k]
    registra(i, "anagrafica", "livello passato da 4 a 5 senza evento: il cedolino torna, ma è più basso")
    i = prendi(lambda r: libero(r) and r["superminimo"] > 0)
    S.loc[i, "superminimo"] = 0.0
    S.loc[i] = pd.Series(ricalcola(S.loc[i].to_dict()))
    registra(i, "anagrafica", "superminimo azzerato senza evento: il cedolino torna, ma è più basso")

    # ratei di tredicesima e quattordicesima sbagliati: il cedolino torna in ogni importo, i dodicesimi no
    anno = R.primo_del_mese(C.MESE).year

    def pochi_giorni(r) -> bool:
        """Assunto quest'anno, con meno di 15 giorni di servizio nel mese di assunzione: quel mese non matura."""
        d = date.fromisoformat(r["data_assunzione"])
        return d.year == anno and calendar.monthrange(d.year, d.month)[1] - d.day + 1 < C.GIORNI_MESE_INTERO

    i = next(i for i in S.index if libero(S.loc[i]) and pochi_giorni(S.loc[i]))
    S.loc[i, "ratei_13"] += 1
    registra(i, "ratei", "mese di assunzione con meno di 15 giorni di servizio contato nella tredicesima")
    da_gennaio = lambda r: R.ratei_13(date.fromisoformat(r["data_assunzione"]), C.MESE)
    i = prendi(lambda r: libero(r) and da_gennaio(r) != r["ratei_14"])
    S.loc[i, "ratei_14"] = da_gennaio(S.loc[i])
    registra(i, "ratei", "quattordicesima contata da gennaio invece che da luglio")
    i = prendi(lambda r: libero(r) and r["ratei_13"] > 1)
    S.loc[i, "ratei_13"] -= 1
    registra(i, "ratei", "un dodicesimo di tredicesima in meno senza assenze che lo spieghino")

    # cessazioni a fine mese: due corrette, tre con un errore ciascuna
    fine_mese = date(R.primo_del_mese(C.MESE).year, R.primo_del_mese(C.MESE).month,
                     calendar.monthrange(R.primo_del_mese(C.MESE).year, R.primo_del_mese(C.MESE).month)[1])

    for col in ("data_cessazione", "tipo_cessazione", "preavviso_giorni", "tredicesima", "quattordicesima",
                "ferie_liquidate"):
        S[col] = S[col].astype(object)

    def cessa(i, tipo: str, errore: str = "", giorno: date | None = None) -> None:
        S.loc[i] = pd.Series(cessazione(S.loc[i].to_dict(), tipo, giorno or fine_mese, errore))

    pieno = lambda r: libero(r) and r["ferie_residuo"] > 1 and r["ratei_14"] != r["ratei_13"]
    cessa(prendi(pieno), "dimissioni")
    cessa(prendi(pieno), "licenziamento")
    i = prendi(pieno)
    cessa(i, "dimissioni", "ferie")
    registra(i, "ferie_liquidate", "ferie non godute pagate a 1/30 della retribuzione invece che a 1/26")
    i = prendi(pieno)
    cessa(i, "dimissioni", "quattordicesima")
    registra(i, "tredicesima", "quattordicesima liquidata con i dodicesimi da gennaio invece che da luglio")
    i = prendi(pieno)
    cessa(i, "licenziamento", "preavviso")
    registra(i, "preavviso", "licenziamento con metà del preavviso minimo del CCNL")
    # un'uscita corretta a metà mese, prima del 15: l'ultimo mese non matura né tredicesima né quattordicesima
    cessa(prendi(pieno), "licenziamento", giorno=date(fine_mese.year, fine_mese.month, 10))

    for col in ASSENZE + TFR_USCITA + INTEGRAZIONE:
        S[col] = S[col].astype(object)

    # TFR alla cessazione (C19): fondo al 31 dicembre 2025, quote del 2026 fino all'uscita e imponibile dello stesso
    # periodo; poi il TFR liquidato con la rivalutazione ISTAT. Tre uscite con un errore ciascuna.
    altri_errori = iter(["imposta", "contributo"])
    for i in S.index[S["evento"] == "cessazione"]:
        uscita = date.fromisoformat(S.loc[i, "data_cessazione"])
        errore = "coefficiente" if uscita.day < 15 else next(altri_errori, "")
        valori, nota = tfr_uscita(S.loc[i].to_dict(), rng2, errore)
        S.loc[i, TFR_USCITA] = valori
        if errore:
            registra(i, "tfr_liquidato", nota)

    # Conguaglio IRPEF alla cessazione (C21): l'imponibile da gennaio, i giorni di lavoro e quanto già trattenuto o
    # erogato nei mesi prima (ogni mese come agosto, con le regole di C20); poi il cedolino di uscita porta la
    # differenza. Due uscite con un errore: detrazioni piene invece che rapportate ai giorni, e conguaglio non fatto.
    for col in CONGUAGLIO:
        S[col] = S[col].astype(object)
    errori_conguaglio = iter(["detrazioni", "non_fatto"])
    for i in S.index[S["evento"] == "cessazione"]:
        errore = next(errori_conguaglio, "")
        r, nota = conguaglio_uscita(S.loc[i].to_dict(), ago[i], errore)
        S.loc[i] = pd.Series(r)
        if errore:
            registra(i, "conguaglio", nota)

    # Assenze di settembre (C15-C17, C22). La base dell'indennità INPS è la retribuzione di agosto; nel mese la
    # retribuzione dei giorni di assenza lascia il posto a indennità, carenza e integrazione del datore di lavoro.
    inizio = R.primo_del_mese(C.MESE)
    giorno = lambda g: date(inizio.year, inizio.month, g)       # noqa: E731

    def base_agosto(i) -> float:
        g = ago[i]
        return R.centesimi(g["tabellare"] + g["scatti"] + g["superminimo"])

    def malattia(i, dal: int, al: int, evento_n: int, esente: bool = False, **kw) -> None:
        S.loc[i] = pd.Series(malattia_mese(S.loc[i].to_dict(), ago[i], giorno(dal), giorno(al), evento_n, esente,
                                           **kw))

    def maternita(i, dal: int, inps: float | None = None) -> None:
        S.loc[i] = pd.Series(maternita_mese(S.loc[i].to_dict(), ago[i], giorno(dal), inps))

    n_originali = len(ago)             # i dipendenti con il cedolino di agosto, che dà la base
    originali = lambda r: libero(r) and r.name < n_originali
    malattia(prendi(originali), 3, 30, 1)                          # 28 giorni: carenza, 50% e 66,66%
    malattia(prendi(originali), 14, 18, 5)                         # quinto evento: niente carenza
    malattia(prendi(originali), 7, 20, 6, esente=True)             # prognosi di 14 giorni: carenza dovuta
    i = prendi(originali)
    d0, d1 = giorno(2), giorno(25)
    sbagliata = R.centesimi(base_agosto(i) / 26) * 0.5 * R.giorni_malattia(d0, d1, C.MESE)[1] \
        + R.centesimi(base_agosto(i) / 26) * 0.6666 * R.giorni_malattia(d0, d1, C.MESE)[2]
    malattia(i, 2, 25, 2, inps=R.centesimi(sbagliata))
    registra(i, "malattia", "indennità INPS calcolata su 1/26 della retribuzione invece che × 14/12 / 30")
    i = prendi(originali)
    malattia(i, 10, 16, 5, carenza=R.importo_carenza(base_agosto(i), 3, 0.5, C.MESE))
    registra(i, "carenza", "carenza pagata al quinto evento dell'anno, quando non è più dovuta")
    i = prendi(lambda r: originali(r) and S.loc[r.name, "codice_fiscale"][9] in "4567")      # una lavoratrice
    maternita(i, 1)
    i = prendi(lambda r: originali(r) and S.loc[r.name, "codice_fiscale"][9] in "4567")
    sbagliata = R.centesimi(base_agosto(i) / C.DIVISORE_RMGG) * C.MATERNITA_PERCENTUALE * 30
    maternita(i, 1, inps=R.centesimi(sbagliata))
    registra(i, "maternita", "indennità di maternità senza i ratei di tredicesima e quattordicesima nella base")

    # Permessi (C18): un neoassunto e un part-time che maturano come un tempo pieno con anzianità
    def permessi_pieni(i) -> None:
        r = S.loc[i]
        pieni = round((C.ROL_ORE["oltre_15"] + C.EX_FESTIVITA_ORE) / 12, 4)
        prima = r["permessi_residuo"] - r["permessi_maturati"] + r["permessi_goduti"]
        S.loc[i, "permessi_maturati"] = pieni
        S.loc[i, "permessi_residuo"] = round(prima + pieni - r["permessi_goduti"], 4)

    giovane = lambda r: date.fromisoformat(r["data_assunzione"]) > date(2024, 10, 1)
    i = prendi(lambda r: originali(r) and giovane(r))
    permessi_pieni(i)
    registra(i, "permessi", "assunto da meno di 2 anni: la riduzione d'orario non spetta ancora, maturata per intero")
    i = prendi(lambda r: originali(r) and r["part_time"] < 1 and not giovane(r))
    permessi_pieni(i)
    registra(i, "permessi", "part-time che matura i permessi di un tempo pieno")

    # Due quadri sopra la prima fascia pensionabile: l'1% aggiuntivo applicato a uno, dimenticato dall'altro (C03)
    sopra = []
    for k, (nascita, data) in enumerate(((date(1971, 4, 9), "2008-05-12"), (date(1969, 11, 2), "2004-02-23"))):
        cf = codice_fiscale.sintetico(rng2, nascita, False)
        d = pd.Series({"matricola": f"B19{k}", "cliente": "B", "codice_fiscale": cf,
                       "livello": "Quadri", "data_assunzione": data, "part_time": 1.0, "superminimo": 1900.0 + 300 * k,
                       "superminimo_assorbibile": False})
        g = cedolino(d, C.MESE_PRECEDENTE, rng2, 20.0, permessi_prec=30.0)
        ago.append(g)
        sopra.append(cedolino(d, C.MESE, rng2, g["ferie_residuo"], permessi_prec=g["permessi_residuo"]))
    r = sopra[1]
    r["contributi_inps"] = R.centesimi(R.euro(r["lordo"]) * R.aliquota_dipendente(C.CLIENTI["B"]["media_semestre"]))
    r["imponibile_irpef"] = R.centesimi(r["lordo"] - r["contributi_inps"])
    fisco(r)
    errori.append({"matricola": r["matricola"], "cliente": "B", "tipo": "inps",
                   "nota": "retribuzione oltre 4.685 €: contributo aggiuntivo dell'1% non trattenuto"})
    nuovi += sopra

    # IRPEF del mese (C20): tre ritenute sbagliate, ognuna con un netto coerente, così la quadratura torna
    annuo = lambda r: r["imponibile_irpef"] * C.MENSILITA       # noqa: E731
    # lo scaglione del 33% è ragguagliato al mese: serve un imponibile mensile oltre 28.000 / 12
    i = prendi(lambda r: libero(r) and r["imponibile_irpef"] > C.SCAGLIONI_IRPEF[0][0] / 12 + 50)
    S.loc[i] = pd.Series(fisco(S.loc[i].to_dict(), scaglioni=C.SCAGLIONI_IRPEF_2025))
    registra(i, "irpef", "ritenuta con lo scaglione del 35% del 2025 invece che del 33% del 2026")
    i = prendi(lambda r: libero(r) and C.CUNEO_DETRAZIONE["soglie"][0] < annuo(r) <= C.CUNEO_DETRAZIONE["soglie"][1])
    r = fisco(S.loc[i].to_dict())
    r["irpef"] = R.centesimi(r["irpef"] + C.CUNEO_DETRAZIONE["importo"] / 12)
    S.loc[i] = pd.Series(netto(r))
    registra(i, "irpef", "ulteriore detrazione del cuneo fiscale (1.000 € l'anno) non applicata")
    i = prendi(lambda r: libero(r) and annuo(r) <= C.CUNEO_SOMMA_SOGLIA)
    r = fisco(S.loc[i].to_dict())
    r["bonus_cuneo"] = 0.0
    S.loc[i] = pd.Series(netto(r))
    registra(i, "irpef", "somma del cuneo fiscale non erogata a un reddito sotto i 20.000 €")

    # Integrazione del datore di lavoro (C22): in fondo, per non cambiare i casi già presenti
    i = prendi(originali)
    malattia(i, 8, 19, 2, integrazione=0.0)
    registra(i, "integrazione", "integrazione del datore di lavoro non pagata: il netto resta sotto il 75% garantito")

    ago2, S2, a2 = clienti_v22(errori)
    S = pd.concat([S, pd.DataFrame(nuovi), S2], ignore_index=True)
    ago += ago2
    a = pd.concat([a, a2], ignore_index=True)
    ced = pd.concat([pd.DataFrame(ago), S], ignore_index=True)
    for col in ("scatti_n", "ratei_13", "ratei_14"):
        ced[col] = ced[col].astype(int)
    for col in ("tredicesima", "quattordicesima", "ferie_liquidate"):
        ced[col] = [f"{float(v):.2f}" if v not in ("", None) else "" for v in ced[col]]
    ced["preavviso_giorni"] = [str(int(v)) if v not in ("", None) else "" for v in ced["preavviso_giorni"]]
    ced.to_csv(C.CEDOLINI, index=False, float_format="%.4f")

    # F24 di settembre: ritenute (codice tributo 1001) e contributi a carico dei dipendenti per cliente.
    s = ced[ced["mese"] == C.MESE].groupby("cliente")[["irpef", "contributi_inps"]].sum().round(2)
    f24 = pd.DataFrame({"cliente": s.index, "mese": C.MESE, "ritenute_1001": s["irpef"].values,
                        "contributi_dipendente": s["contributi_inps"].values})
    f24.loc[f24["cliente"] == "C", "ritenute_1001"] -= 212.40   # una ritenuta rimasta fuori dalla delega
    f24["ritenute_1001"] = f24["ritenute_1001"].round(2)
    f24.to_csv(C.F24, index=False, float_format="%.2f")
    errori.append({"matricola": "", "cliente": "C", "tipo": "f24",
                   "nota": "F24 con 212,40 € di ritenute in meno dei cedolini"})

    a.to_csv(C.DIPENDENTI, index=False)
    pd.DataFrame(errori).to_csv(C.ERRORI, index=False)
    print(f"{len(a) + len(nuovi)} dipendenti, {len(ced)} cedolini, {len(errori)} errori inseriti")


if __name__ == "__main__":
    main()
