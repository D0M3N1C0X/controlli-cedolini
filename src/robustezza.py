"""
Prova di robustezza: gli errori inseriti da genera.py sono pochi e scelti da chi ha scritto i
controlli, quindi trovarli tutti dimostra poco. Qui si altera a caso una voce di un cedolino
corretto, di un importo casuale, centinaia di volte, e si conta quante alterazioni almeno un
controllo segnala, per voce e per ampiezza.

    python src/robustezza.py
"""
import random

import pandas as pd

import config as C
import controlli

VOCI = ["tabellare", "scatti", "superminimo", "straordinari", "lordo", "contributi_inps", "irpef",
        "altre_trattenute", "netto", "quota_tfr", "ferie_residuo"]
AMPIEZZE = [0.005, 0.02, 1.0, 10.0, 100.0]   # euro, o giorni per le ferie
PROVE = 1100


def run(seed: int = 7, prove: int = PROVE) -> pd.DataFrame:
    m, prec, f24 = controlli.carica()
    err = pd.read_csv(C.ERRORI, keep_default_na=False)
    puliti = m[~m["matricola"].isin(err["matricola"]) & ~m["cliente"].eq("C")].index.tolist()
    base, _ = controlli.esegui(m, prec, f24)
    assert base[base["matricola"].isin(m.loc[puliti, "matricola"])].empty
    rng = random.Random(seed)
    rows = []
    for _ in range(prove):
        i, voce, amp = rng.choice(puliti), rng.choice(VOCI), rng.choice(AMPIEZZE)
        segno = rng.choice([-1, 1])
        x = m.copy()
        x.loc[i, voce] = round(x.loc[i, voce] + segno * amp, 4)
        # i controlli di riga girano sul solo cedolino alterato; l'F24 resta quello trasmesso
        riga, _ = controlli.esegui(x.loc[[i]].reset_index(drop=True), prec, f24.iloc[0:0])
        cliente = x.loc[i, "cliente"]
        somme = x[x["cliente"] == cliente][["irpef", "contributi_inps"]].sum().round(2)
        f = f24.set_index("cliente").loc[cliente]
        c08 = (abs(f["ritenute_1001"] - somme["irpef"]) > C.TOLLERANZA
               or abs(f["contributi_dipendente"] - somme["contributi_inps"]) > C.TOLLERANZA)
        codici = set(riga["controllo"]) | ({"C08"} if c08 else set())
        rows.append({"voce": voce, "ampiezza": amp, "trovato": bool(codici), "da": ",".join(sorted(codici))})
    return pd.DataFrame(rows)


def tabella(r: pd.DataFrame) -> pd.DataFrame:
    t = r.pivot_table(index="voce", columns="ampiezza", values="trovato", aggfunc="mean")
    return t.reindex(VOCI)


def main() -> None:
    r = run()
    C.REPORT.mkdir(exist_ok=True)
    r.to_csv(C.REPORT / "robustezza.csv", index=False)
    print(tabella(r).round(2).to_string())
    print("sopra la tolleranza:", r[r["ampiezza"] > C.TOLLERANZA]["trovato"].mean().round(3))


if __name__ == "__main__":
    main()


def errore_coerente() -> dict:
    """Il limite dichiarato: un livello sbagliato in anagrafica, con il cedolino ricalcolato in modo
    coerente, passa tutti i controlli aritmetici. Restituisce cosa vedono i controlli."""
    import genera
    m, prec, f24 = controlli.carica()
    err = pd.read_csv(C.ERRORI, keep_default_na=False)
    i = m[~m["matricola"].isin(err["matricola"]) & m["livello"].eq("4") & m["evento"].eq("")].index[0]
    d = m.loc[i].copy()
    d["livello"] = "5"                         # assunto come 4° livello, inserito come 5°
    giusto = m.loc[i, "ferie_residuo"] + m.loc[i, "ferie_godute"] - m.loc[i, "ferie_maturate"]
    r = genera.cedolino(d, C.MESE, random.Random(0), giusto, ferie_godute=m.loc[i, "ferie_godute"])
    r["evento"] = ""
    x = m.copy()
    for k, v in r.items():
        x.loc[i, k] = v
    riga, _ = controlli.esegui(x.loc[[i]].reset_index(drop=True), prec, f24.iloc[0:0])
    return {"matricola": m.loc[i, "matricola"], "netto_giusto": float(m.loc[i, "netto"]),
            "netto_pagato": float(x.loc[i, "netto"]), "segnalazioni": list(riga["controllo"])}
