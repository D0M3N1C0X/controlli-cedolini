"""
Le regole contrattuali che i controlli applicano, scritte una volta sola. Le stesse regole sono
riscritte come formule nel foglio di controllo (build_foglio.py), e il foglio Riconciliazione
verifica che diano lo stesso risultato.
"""
import calendar
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

import pandas as pd

import config as C


def tabella() -> pd.DataFrame:
    return pd.read_csv(C.CCNL, dtype={"livello": str}).set_index("livello")


def primo_del_mese(mese: str) -> date:
    y, m = map(int, mese.split("-"))
    return date(y, m, 1)


def scatti_maturati(assunzione: date, mese: str) -> int:
    """Scatti in pagamento nel mese: ogni triennio compiuto conta dal mese successivo, fino a 10."""
    inizio = primo_del_mese(mese)
    n = 0
    for k in range(1, C.SCATTI_MAX + 1):
        y, m = assunzione.year + C.SCATTI_ANNI * k, assunzione.month
        # il triennio si compie nel mese (y, m): l'aumento parte dal mese dopo
        if (inizio.year, inizio.month) > (y, m):
            n = k
    return n


def dodicesimi(assunzione: date, mese: str, inizio: date) -> int:
    """Mesi di servizio da `inizio` al mese del cedolino compreso. Il mese di assunzione conta se i giorni di
    servizio sono almeno GIORNI_MESE_INTERO; chi è assunto prima di `inizio` matura tutti i mesi del periodo."""
    fine = primo_del_mese(mese)
    if assunzione <= inizio:
        return (fine.year - inizio.year) * 12 + fine.month - inizio.month + 1
    giorni = calendar.monthrange(assunzione.year, assunzione.month)[1] - assunzione.day + 1
    return ((fine.year - assunzione.year) * 12 + fine.month - assunzione.month
            + (1 if giorni >= C.GIORNI_MESE_INTERO else 0))


def ratei_13(assunzione: date, mese: str) -> int:
    """Dodicesimi di tredicesima maturati nell'anno solare, fino al mese del cedolino."""
    return dodicesimi(assunzione, mese, date(primo_del_mese(mese).year, 1, 1))


def ratei_14(assunzione: date, mese: str) -> int:
    """Dodicesimi di quattordicesima maturati da luglio (dell'anno, o di quello prima se il mese è prima di luglio)."""
    m = primo_del_mese(mese)
    return dodicesimi(assunzione, mese, date(m.year if m.month >= 7 else m.year - 1, 7, 1))


def centesimi(x: float) -> float:
    """Arrotonda al centesimo come ROUND di Excel: 15 cifre significative, poi metà per eccesso."""
    v = Decimal(f"{float(x):.15g}").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return float(v)


def tabellare(livello: str, part_time: float, colonna: str = C.COLONNA_MINIMO) -> float:
    return centesimi(tabella().loc[livello, colonna] * part_time)


def scatti_importo(livello: str, n: int, part_time: float) -> float:
    return centesimi(tabella().loc[livello, "scatto"] * n * part_time)


def euro(x: float) -> float:
    """Arrotonda all'unità di euro, metà per eccesso: così si arrotonda l'imponibile contributivo (F10)."""
    return float(Decimal(f"{float(x):.15g}").quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def contributi(lordo: float) -> float:
    """Contributo a carico del dipendente: aliquota sull'imponibile arrotondato all'euro, poi al centesimo."""
    return centesimi(euro(lordo) * C.ALIQUOTA_DIPENDENTE)


def quota_tfr(retribuzione_ordinaria: float) -> float:
    return centesimi(retribuzione_ordinaria * C.MENSILITA / C.DIVISORE_TFR / 12)


def ferie_mese() -> float:
    return round(C.FERIE_ANNUE / 12, 4)
