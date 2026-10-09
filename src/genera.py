"""
Genera i dati sintetici: tre clienti, 119 dipendenti, i cedolini di agosto e settembre 2026 e gli
F24 di settembre. Agosto è corretto; a settembre vengono inseriti errori di tipo noto, registrati
in data/errori_inseriti.csv, così si può misurare quanti ne trovano i controlli e quanti falsi
allarmi danno. Ci sono anche casi legittimi che non devono essere segnalati: assunzioni del mese,
straordinari dichiarati, un passaggio a part-time.

    python src/genera.py
"""
import random
from datetime import date

import pandas as pd

import codice_fiscale
import config as C
import regole as R

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
             ferie_godute: float = 0.0, part_time: float | None = None) -> dict:
    pt = d["part_time"] if part_time is None else part_time
    assunzione = date.fromisoformat(d["data_assunzione"])
    n = R.scatti_maturati(assunzione, mese)
    tab = R.tabellare(d["livello"], pt)
    sc = R.scatti_importo(d["livello"], n, pt)
    ordinaria = R.centesimi(tab + sc + d["superminimo"])
    lordo = R.centesimi(ordinaria + straordinari)
    inps = R.contributi(lordo)
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
            "ferie_residuo": round(residuo_prec + maturate - ferie_godute, 4)}


def ricalcola(r: dict) -> dict:
    """Dopo una modifica a monte, rifà a cascata le voci che il software paghe deriverebbe."""
    ordinaria = R.centesimi(r["tabellare"] + r["scatti"] + r["superminimo"])
    r["lordo"] = R.centesimi(ordinaria + r["straordinari"])
    r["contributi_inps"] = R.contributi(r["lordo"])
    r["imponibile_irpef"] = R.centesimi(r["lordo"] - r["contributi_inps"])
    r["irpef"] = irpef_sintetica(r["imponibile_irpef"])
    r["altre_trattenute"] = R.centesimi(r["imponibile_irpef"] * 0.015)
    r["netto"] = R.centesimi(r["imponibile_irpef"] - r["irpef"] - r["altre_trattenute"])
    r["quota_tfr"] = R.quota_tfr(ordinaria)
    return r


def main() -> None:
    rng = random.Random(C.SEED)
    a = anagrafica(rng)
    ago, set_ = [], []
    for _, d in a.iterrows():
        residuo = round(rng.uniform(12, 30), 4)
        g_ago = min(rng.choice([0, 5, 10, 10, 15]), int(residuo))
        ago.append(cedolino(d, C.MESE_PRECEDENTE, rng, residuo, ferie_godute=g_ago))
        set_.append(cedolino(d, C.MESE, rng, ago[-1]["ferie_residuo"], ferie_godute=rng.choice([0, 0, 0, 1, 2])))
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
    for _ in range(4):        # aliquota sbagliata
        i = prendi(libero)
        S.loc[i, "contributi_inps"] = R.centesimi(R.euro(S.loc[i, "lordo"]) * 0.0949)
        S.loc[i, "imponibile_irpef"] = R.centesimi(S.loc[i, "lordo"] - S.loc[i, "contributi_inps"])
        S.loc[i, "irpef"] = irpef_sintetica(S.loc[i, "imponibile_irpef"])
        S.loc[i, "altre_trattenute"] = R.centesimi(S.loc[i, "imponibile_irpef"] * 0.015)
        S.loc[i, "netto"] = R.centesimi(S.loc[i, "imponibile_irpef"] - S.loc[i, "irpef"] - S.loc[i, "altre_trattenute"])
        registra(i, "inps", "aliquota 9,49% invece di 9,19%")
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

    S = pd.concat([S, pd.DataFrame(nuovi)], ignore_index=True)
    ced = pd.concat([pd.DataFrame(ago), S], ignore_index=True)
    for col in ("scatti_n",):
        ced[col] = ced[col].astype(int)
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
