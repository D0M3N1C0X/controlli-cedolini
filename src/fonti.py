"""
Le fonti al mese chiuso: fino a quando vale ogni parametro che cambia nel tempo, e se copre i mesi controllati.

Un controllo è giusto solo quanto la regola che applica. Le aliquote e le soglie di un anno, gli indici ISTAT di un
mese, le tranche di un contratto hanno una data: SCADENZE la scrive una volta, con la fonte (docs/fonti.md) e il
giorno in cui è stata letta. `copertura` dice, per un mese, quali parametri non lo coprono; i test la chiamano sul
mese controllato e su tutti i mesi dell'anno, così che spostare C.MESE oltre una scadenza fermi la pipeline invece di
dare risultati con le regole vecchie.
"""
import csv
from dataclasses import dataclass

import config as C
import regole as R

ULTIMO_MESE_CHIUSO = "2026-10"          # il mese chiuso più recente al giorno della lettura
LETTURA = "2026-11-25"
FOI_ISTAT = C.DATA / "source" / "istat_foi.csv"
RINNOVO = "9999-12"                     # i minimi valgono fino al prossimo rinnovo, che non ha una data


@dataclass(frozen=True)
class Scadenza:
    parametro: str
    fonte: str                # codice in docs/fonti.md
    dal: str                  # primo mese coperto
    al: str                   # ultimo mese coperto
    letto: str                # giorno della lettura alla fonte
    prossima: str             # quando e dove arriva il valore successivo


MESI_NOMI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre",
             "novembre", "dicembre"]


def nome_mese(m: str) -> str:
    """'2027-02' -> 'febbraio 2027'; il mese del rinnovo senza data -> 'fino al rinnovo'."""
    if m == RINNOVO:
        return "fino al rinnovo"
    a, n = m.split("-")
    return f"{MESI_NOMI[int(n) - 1]} {a}"


def _foi_ultimo() -> str:
    return max(C.FOI_MESI)


def _tranche_ultima(ccnl: str) -> str:
    prefisso = R.regola(ccnl)["minimo"].rsplit("_", 2)[0]
    cols = [c for c in R.tabella(ccnl).columns if c.startswith(prefisso + "_")]
    return max(c[-7:].replace("_", "-") for c in cols)


def scadenze() -> list[Scadenza]:
    s = [
        Scadenza("Scaglioni IRPEF 2026 (23%, 33%, 43%)", "F24", "2026-01", "2026-12", "2026-11-08",
                 "legge di bilancio 2027, da rileggere a gennaio 2027"),
        Scadenza("Detrazioni per lavoro dipendente (art. 13 TUIR)", "F25", "2025-01", "2026-12", "2026-11-08",
                 "il testo in vigore scade il 31 dicembre 2026"),
        Scadenza("Cuneo fiscale: somma e ulteriore detrazione", "F26", "2026-01", "2026-12", "2026-11-08",
                 "dal 2027 cambia (D.lgs. 117/2026)"),
        Scadenza("Prima fascia pensionabile 56.224 €, 4.685 € al mese", "F15", "2026-01", "2026-12", LETTURA,
                 "circolare INPS sui minimali e massimali 2027, di solito a fine gennaio"),
        Scadenza("Indice FOI per la rivalutazione del TFR", "F20", "2026-01", _foi_ultimo(), LETTURA,
                 "il FOI di un mese esce verso la metà del mese dopo"),
    ]
    for k in C.CCNL:
        s.append(Scadenza(f"Minimi del CCNL {k}, ultima tranche in tabella", "F01" if k == "terziario" else "F30-F40",
                          "2025-01", RINNOVO, "2026-10-09" if k == "terziario" else "2026-11-09",
                          f"dopo la tranche di {nome_mese(_tranche_ultima(k))} in tabella, il prossimo rinnovo"))
    return s


def copertura(mese: str) -> list[Scadenza]:
    """I parametri che non coprono il mese."""
    return [x for x in scadenze() if not (x.dal <= mese <= x.al)]


def foi_istat() -> dict[str, float]:
    """La serie 2026 della tavola ISTAT copiata in data/source, base 2025."""
    with open(FOI_ISTAT, encoding="utf-8") as f:
        return {r["mese"]: float(r["indice"]) for r in csv.DictReader(f) if r["base"] == "2025"}


def prima_scadenza(dopo: str = ULTIMO_MESE_CHIUSO) -> Scadenza:
    """Il primo parametro annuale a scadere dopo il mese chiuso (il FOI è mensile per natura)."""
    return min((x for x in scadenze() if x.al >= dopo and x.fonte != "F20"), key=lambda x: x.al)


if __name__ == "__main__":
    for x in scadenze():
        print(f"{x.parametro:55} {x.dal} - {x.al}  letto {x.letto}")
    print("prima a scadere:", prima_scadenza())
