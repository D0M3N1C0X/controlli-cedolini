"""
Regole contro un rilevatore statistico. La domanda è legittima: perché scrivere dieci regole invece di
lasciare che un modello trovi le anomalie da solo? Qui il modello è il più semplice che non sa nulla del
CCNL: per ogni cedolino calcola alcuni rapporti (contributi su lordo, TFR su retribuzione ordinaria,
netto su lordo, netto sul mese prima) e segnala chi si allontana dalla mediana di più di k deviazioni
assolute mediane (punteggio z robusto). Poi si contano errori trovati e falsi allarmi, come per le regole.

    python src/statistica.py
"""
import numpy as np
import pandas as pd

import config as C
import controlli

SOGLIE = [3.0, 3.5, 5.0]


def caratteristiche(m: pd.DataFrame, prec: pd.DataFrame) -> pd.DataFrame:
    ordinaria = m["tabellare"] + m["scatti"] + m["superminimo"]
    netto_prec = m["matricola"].map(prec.set_index("matricola")["netto"])
    return pd.DataFrame({
        "contributi_su_lordo": m["contributi_inps"] / m["lordo"],
        "tfr_su_ordinaria": m["quota_tfr"] / ordinaria,
        "netto_su_lordo": m["netto"] / m["lordo"],
        "netto_su_mese_prima": (m["netto"] / netto_prec).fillna(1.0),
    })


def punteggi(x: pd.DataFrame) -> pd.DataFrame:
    """z robusto: (valore - mediana) / (1,4826 x deviazione assoluta mediana). Se più di metà dei valori
    coincide con la mediana la deviazione mediana è zero: si usa allora 1,2533 x deviazione media assoluta
    (Iglewicz e Hoaglin), altrimenti la colonna non segnalerebbe mai nulla."""
    med = x.median()
    dev = (x - med).abs()
    scala = dev.median() * 1.4826
    scala = scala.where(scala > 1e-12, dev.mean() * 1.2533)
    return (x - med) / scala.replace(0, np.nan)


def valutazione(soglie=SOGLIE) -> pd.DataFrame:
    m, prec, _ = controlli.carica()
    z = punteggi(caratteristiche(m, prec)).abs()
    err = pd.read_csv(C.ERRORI, keep_default_na=False)
    sbagliati = set(err.loc[err["matricola"] != "", "matricola"])
    rows = []
    for k in soglie:
        segnalati = set(m.loc[(z > k).any(axis=1), "matricola"])
        rows.append({"metodo": f"Statistico, z oltre {k:g}".replace(".", ","), "errori": len(sbagliati),
                     "trovati": len(segnalati & sbagliati), "falsi_allarmi": len(segnalati - sbagliati)})
    an, _ = controlli.esegui(m, prec, controlli.carica()[2])
    regole = set(an.loc[an["matricola"] != "", "matricola"])
    rows.append({"metodo": "Regole (C01-C10)", "errori": len(sbagliati), "trovati": len(regole & sbagliati),
                 "falsi_allarmi": len(regole - sbagliati)})
    t = pd.DataFrame(rows)
    t[["errori", "trovati", "falsi_allarmi"]] = t[["errori", "trovati", "falsi_allarmi"]].astype(int)
    t["richiamo"] = t["trovati"] / t["errori"]
    t["precisione"] = t["trovati"] / (t["trovati"] + t["falsi_allarmi"]).replace(0, np.nan)
    return t


def per_tipo(k: float = 3.5) -> pd.DataFrame:
    """Quali tipi di errore vede il rilevatore statistico, e quali no."""
    m, prec, _ = controlli.carica()
    z = punteggi(caratteristiche(m, prec)).abs()
    segnalati = set(m.loc[(z > k).any(axis=1), "matricola"])
    err = pd.read_csv(C.ERRORI, keep_default_na=False)
    err = err[err["matricola"] != ""]
    trovati = err.assign(trovato=err["matricola"].isin(segnalati)).groupby("tipo", sort=False)["trovato"]
    g = trovati.agg(["count", "sum"])
    g = g.rename(columns={"count": "errori", "sum": "trovati_statistico"}).astype(int)
    return g.reset_index()


def main() -> None:
    pd.set_option("display.width", 160)
    print(valutazione().round(3).to_string(index=False))
    print(per_tipo().to_string(index=False))


if __name__ == "__main__":
    main()
