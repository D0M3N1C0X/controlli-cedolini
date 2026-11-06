"""
Genera i dati sintetici: tre clienti, 119 dipendenti, i cedolini di agosto e settembre 2026 e gli
F24 di settembre. Agosto è corretto; a settembre vengono inseriti errori di tipo noto, registrati
in data/errori_inseriti.csv, così si può misurare quanti ne trovano i controlli e quanti falsi
allarmi danno. Ci sono anche casi legittimi che non devono essere segnalati: assunzioni del mese,
straordinari dichiarati, un passaggio a part-time.

    python src/genera.py
"""
import calendar
import random
from datetime import date, timedelta

import pandas as pd

import codice_fiscale
import config as C
import regole as R
from controlli import ASSENZE, TFR_USCITA

LIVELLI = ["Quadri", "1", "2", "3", "4", "5", "6", "7"]
PESI_LIVELLO = [1, 3, 8, 18, 34, 20, 10, 6]


def irpef_sintetica(imponibile: float) -> float:
    """Ritenuta verosimile ma NON calcolata con le regole fiscali: serve solo a riconciliare l'F24."""
    annuo = imponibile * 12
    imposta = 0.23 * min(annuo, 28000) + 0.33 * max(0, min(annuo, 50000) - 28000) + 0.43 * max(0, annuo - 50000)
    detrazione = max(0.0, 1955 - 0.04 * max(0, annuo - 15000))
    return R.centesimi(max(0.0, imposta - detrazione) / 12)


def anagrafica(rng: random.Random) -> pd.DataFrame:
    rows = []
    n = 0
    for cliente, info in C.CLIENTI.items():
        for _ in range(info["dipendenti"]):
            n += 1
            donna = rng.random() < 0.52
            nascita = date(rng.randint(1962, 2003), rng.randint(1, 12), rng.randint(1, 28))
            assunzione = date(rng.randint(max(nascita.year + 19, 1995), 2026), rng.randint(1, 12), rng.randint(1, 28))
            if assunzione > date(2026, 7, 31):
                assunzione = date(rng.randint(2012, 2025), rng.randint(1, 12), rng.randint(1, 28))
            livello = rng.choices(LIVELLI, PESI_LIVELLO)[0]
            pt = rng.choices([1.0, 0.75, 0.5], [70, 20, 10])[0] if livello not in ("Quadri", "1") else 1.0
            superminimo = R.centesimi(rng.choice([0, 0, 0, 50, 80, 120, 150, 200, 300]) * pt)
            rows.append({"matricola": f"{cliente}{n:03d}", "cliente": cliente,
                         "codice_fiscale": codice_fiscale.sintetico(rng, nascita, donna),
                         "sesso": "F" if donna else "M", "livello": livello,
                         "data_assunzione": assunzione.isoformat(), "part_time": pt, "superminimo": superminimo,
                         "superminimo_assorbibile": rng.random() < 0.7})
    a = pd.DataFrame(rows)
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
    n = R.scatti_maturati(assunzione, mese)
    tab = R.tabellare(d["livello"], pt)
    sc = R.scatti_importo(d["livello"], n, pt)
    ordinaria = R.centesimi(tab + sc + d["superminimo"])
    lordo = R.centesimi(ordinaria + straordinari)
    inps = R.contributi(lordo, R.media_cliente(d["cliente"]))
    permessi = R.permessi_mese(assunzione, mese, C.CLIENTI[d["cliente"]]["dipendenti"], pt)
    imponibile = R.centesimi(lordo - inps)
    irpef = irpef_sintetica(imponibile)
    altre = R.centesimi(imponibile * 0.015)
    maturate = R.ferie_mese()
    return {"mese": mese, "matricola": d["matricola"], "cliente": d["cliente"], "codice_fiscale": d["codice_fiscale"],
            "livello": d["livello"], "data_assunzione": d["data_assunzione"], "part_time": pt,
            "superminimo_assorbibile": d["superminimo_assorbibile"], "evento": "",
            "tabellare": tab, "scatti_n": n, "scatti": sc, "superminimo": d["superminimo"],
            "straordinari": straordinari, "lordo": lordo, "contributi_inps": inps, "imponibile_irpef": imponibile,
            "irpef": irpef, "altre_trattenute": altre, "netto": R.centesimi(imponibile - irpef - altre),
            "quota_tfr": R.quota_tfr(ordinaria), "ferie_maturate": maturate, "ferie_godute": ferie_godute,
            "ferie_residuo": round(residuo_prec + maturate - ferie_godute, 4),
            "ratei_13": R.ratei_13(assunzione, mese), "ratei_14": R.ratei_14(assunzione, mese),
            # voci della cessazione: vuote finché il dipendente resta
            "data_cessazione": "", "tipo_cessazione": "", "preavviso_giorni": "", "tredicesima": "",
            "quattordicesima": "", "ferie_liquidate": "",
            # assenze del mese e TFR alla cessazione: vuoti se non ci sono
            **{c: "" for c in ASSENZE + TFR_USCITA},
            "permessi_maturati": permessi, "permessi_goduti": permessi_goduti,
            "permessi_residuo": round(permessi_prec + permessi - permessi_goduti, 4)}


def _importo(v) -> float:
    return 0.0 if v in ("", None) or (isinstance(v, float) and v != v) else float(v)


def ricalcola(r: dict) -> dict:
    """Dopo una modifica a monte, rifà a cascata le voci che il software paghe deriverebbe."""
    ordinaria = R.centesimi(r["tabellare"] + r["scatti"] + r["superminimo"])
    r["lordo"] = R.centesimi(ordinaria + r["straordinari"] + sum(_importo(r.get(k)) for k in
                                                                 ("tredicesima", "quattordicesima", "ferie_liquidate")))
    r["contributi_inps"] = R.contributi(r["lordo"], R.media_cliente(r["cliente"]))
    r["imponibile_irpef"] = R.centesimi(r["lordo"] - r["contributi_inps"])
    r["irpef"] = irpef_sintetica(r["imponibile_irpef"])
    r["altre_trattenute"] = R.centesimi(r["imponibile_irpef"] * 0.015)
    r["netto"] = R.centesimi(r["imponibile_irpef"] - r["irpef"] - r["altre_trattenute"])
    r["quota_tfr"] = R.quota_tfr(ordinaria)
    return r


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
        S.loc[i, "contributi_inps"] = importo
        S.loc[i, "imponibile_irpef"] = R.centesimi(S.loc[i, "lordo"] - S.loc[i, "contributi_inps"])
        S.loc[i, "irpef"] = irpef_sintetica(S.loc[i, "imponibile_irpef"])
        S.loc[i, "altre_trattenute"] = R.centesimi(S.loc[i, "imponibile_irpef"] * 0.015)
        S.loc[i, "netto"] = R.centesimi(S.loc[i, "imponibile_irpef"] - S.loc[i, "irpef"] - S.loc[i, "altre_trattenute"])

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
              "altre_trattenute", "netto", "quota_tfr"):
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
        r = S.loc[i].to_dict()
        assunzione = date.fromisoformat(r["data_assunzione"])
        mensile = R.centesimi(r["tabellare"] + r["scatti"] + r["superminimo"])
        uscita = giorno or fine_mese
        n13, n14 = R.ratei_al(assunzione, C.MESE, uscita)
        minimo = R.preavviso_minimo(tipo, r["livello"], assunzione, uscita)
        r.update({"evento": "cessazione", "data_cessazione": uscita.isoformat(), "tipo_cessazione": tipo,
                  "ratei_13": n13, "ratei_14": n14,
                  "preavviso_giorni": minimo, "tredicesima": R.mensilita_aggiuntiva(mensile, n13),
                  "quattordicesima": R.mensilita_aggiuntiva(mensile, n14),
                  "ferie_liquidate": R.ferie_non_godute(mensile, r["ferie_residuo"])})
        if errore == "ferie":
            r["ferie_liquidate"] = R.centesimi(mensile / 30 * r["ferie_residuo"])
        elif errore == "quattordicesima":
            r["quattordicesima"] = R.mensilita_aggiuntiva(mensile, n13)
        elif errore == "preavviso":
            r["preavviso_giorni"] = minimo // 2
        S.loc[i] = pd.Series(ricalcola(r))

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

    for col in ASSENZE + TFR_USCITA:
        S[col] = S[col].astype(object)

    # TFR alla cessazione (C19): fondo al 31 dicembre 2025, quote del 2026 fino all'uscita e imponibile dello stesso
    # periodo; poi il TFR liquidato con la rivalutazione ISTAT. Tre uscite con un errore ciascuna.
    altri_errori = iter(["imposta", "contributo"])
    for i in S.index[S["evento"] == "cessazione"]:
        r = S.loc[i]
        assunto, uscita = date.fromisoformat(r["data_assunzione"]), date.fromisoformat(r["data_cessazione"])
        mensile = R.centesimi(r["tabellare"] + r["scatti"] + r["superminimo"])
        anni = R.anni_di_servizio(assunto, date(2025, 12, 31))
        mesi = R.dodicesimi_alla_cessazione(assunto, uscita, date(2026, 1, 1))
        fondo = R.centesimi(mensile * C.MENSILITA / C.DIVISORE_TFR * anni * rng2.uniform(0.96, 1.08))
        quote, imponibile = R.centesimi(r["quota_tfr"] * mesi), R.centesimi(r["lordo"] * mesi)
        liquidato = R.tfr_liquidato(fondo, quote, imponibile, uscita)
        errore = "coefficiente" if uscita.day < 15 else next(altri_errori, "")
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
        S.loc[i, TFR_USCITA] = [f"{fondo:.2f}", f"{quote:.2f}", f"{imponibile:.2f}", f"{liquidato:.2f}"]
        if errore:
            registra(i, "tfr_liquidato", nota)

    # Assenze di settembre (C15-C17). La base è la retribuzione di agosto; le indennità sono voci a parte.
    inizio = R.primo_del_mese(C.MESE)

    def base_agosto(i) -> float:
        g = ago[i]
        return R.centesimi(g["tabellare"] + g["scatti"] + g["superminimo"])

    def malattia(i, dal: int, al: int, evento_n: int, esente: bool = False, inps: float | None = None,
                 carenza: float | None = None) -> None:
        d0, d1 = date(inizio.year, inizio.month, dal), date(inizio.year, inizio.month, al)
        n_car, _, _ = R.giorni_malattia(d0, d1, C.MESE)
        quota = R.carenza_percentuale(evento_n, esente)
        giornaliera = R.centesimi(base_agosto(i) / C.DIVISORE_GIORNALIERO)
        dovuta = R.centesimi(giornaliera * n_car * quota)
        dovuta_inps = R.indennita_malattia(base_agosto(i), d0, d1, C.MESE) if inps is None else inps
        S.loc[i, ASSENZE[:6]] = [d0.isoformat(), d1.isoformat(), str(evento_n), "true" if esente else "false",
                                 f"{dovuta_inps:.2f}",
                                 f"{dovuta if carenza is None else carenza:.2f}"]
        S.loc[i, "evento"] = "malattia"

    def maternita(i, dal: int, inps: float | None = None) -> None:
        d0 = date(inizio.year, inizio.month, dal)
        d1 = d0 + timedelta(days=149)                       # cinque mesi di congedo obbligatorio
        importo = R.indennita_maternita(base_agosto(i), d0, d1, C.MESE) if inps is None else inps
        S.loc[i, ASSENZE[6:]] = [d0.isoformat(), d1.isoformat(), f"{importo:.2f}"]
        S.loc[i, "evento"] = "maternità"

    n_originali = len(ago)             # i dipendenti con il cedolino di agosto, che dà la base
    originali = lambda r: libero(r) and r.name < n_originali
    malattia(prendi(originali), 3, 30, 1)                          # 28 giorni: carenza, 50% e 66,66%
    malattia(prendi(originali), 14, 18, 5)                         # quinto evento: niente carenza
    malattia(prendi(originali), 7, 20, 6, esente=True)             # prognosi di 14 giorni: carenza dovuta
    i = prendi(originali)
    d0, d1 = date(inizio.year, inizio.month, 2), date(inizio.year, inizio.month, 25)
    sbagliata = R.centesimi(base_agosto(i) / 26) * 0.5 * R.giorni_malattia(d0, d1, C.MESE)[1] \
        + R.centesimi(base_agosto(i) / 26) * 0.6666 * R.giorni_malattia(d0, d1, C.MESE)[2]
    malattia(i, 2, 25, 2, inps=R.centesimi(sbagliata))
    registra(i, "malattia", "indennità INPS calcolata su 1/26 della retribuzione invece che × 14/12 / 30")
    i = prendi(originali)
    malattia(i, 10, 16, 5, carenza=R.centesimi(base_agosto(i) / C.DIVISORE_GIORNALIERO * 3 * 0.5))
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
    r["irpef"] = irpef_sintetica(r["imponibile_irpef"])
    r["altre_trattenute"] = R.centesimi(r["imponibile_irpef"] * 0.015)
    r["netto"] = R.centesimi(r["imponibile_irpef"] - r["irpef"] - r["altre_trattenute"])
    errori.append({"matricola": r["matricola"], "cliente": "B", "tipo": "inps",
                   "nota": "retribuzione oltre 4.685 €: contributo aggiuntivo dell'1% non trattenuto"})
    nuovi += sopra

    S = pd.concat([S, pd.DataFrame(nuovi)], ignore_index=True)
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
