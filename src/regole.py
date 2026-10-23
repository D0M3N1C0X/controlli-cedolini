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


def dodicesimi_alla_cessazione(assunzione: date, cessazione: date, inizio: date) -> int:
    """Mesi di servizio da `inizio` alla data di cessazione. Il primo e l'ultimo mese contano se i giorni di
    servizio in quel mese sono almeno GIORNI_MESE_INTERO (F11)."""
    da = max(assunzione, inizio)
    if cessazione < da:
        return 0
    if (da.year, da.month) == (cessazione.year, cessazione.month):
        return 1 if (cessazione - da).days + 1 >= C.GIORNI_MESE_INTERO else 0
    primo = calendar.monthrange(da.year, da.month)[1] - da.day + 1 >= C.GIORNI_MESE_INTERO
    ultimo = cessazione.day >= C.GIORNI_MESE_INTERO
    in_mezzo = (cessazione.year - da.year) * 12 + cessazione.month - da.month - 1
    return in_mezzo + int(primo) + int(ultimo)


def inizio_13(giorno: date) -> date:
    return date(giorno.year, 1, 1)


def inizio_14(giorno: date) -> date:
    return date(giorno.year if giorno.month >= 7 else giorno.year - 1, 7, 1)


def ratei_al(assunzione: date, mese: str, cessazione: date | None = None) -> tuple[int, int]:
    """Dodicesimi di tredicesima e quattordicesima maturati nel cedolino del mese: fino al mese compreso, o fino
    alla data di cessazione se il dipendente lascia (l'ultimo mese conta con almeno 15 giorni)."""
    if cessazione is None:
        return ratei_13(assunzione, mese), ratei_14(assunzione, mese)
    return (dodicesimi_alla_cessazione(assunzione, cessazione, inizio_13(cessazione)),
            dodicesimi_alla_cessazione(assunzione, cessazione, inizio_14(cessazione)))


def dodicesimi_14_pagata(assunzione: date, mese: str) -> int:
    """I dodicesimi di una quattordicesima pagata nel mese a chi resta. Si paga a giugno o a luglio per il periodo
    luglio-giugno: da luglio in poi il periodo è quello chiuso il 30 giugno, non quello appena cominciato."""
    m = primo_del_mese(mese)
    if m.month < 7:
        return ratei_14(assunzione, mese)
    fine = date(m.year, 6, 30)
    return dodicesimi_alla_cessazione(assunzione, fine, inizio_14(fine))


def anni_di_servizio(assunzione: date, al: date) -> int:
    """Anni interi di servizio compiuti alla data."""
    return al.year - assunzione.year - ((al.month, al.day) < (assunzione.month, assunzione.day))


def preavviso_minimo(tipo: str, livello: str, assunzione: date, cessazione: date) -> int:
    """Giorni di preavviso del CCNL (F13): fino a 5 anni di servizio, dal 6° al 10° anno, oltre il 10°."""
    anni = anni_di_servizio(assunzione, cessazione)
    fascia = 0 if anni < 5 else 1 if anni < 10 else 2
    return C.PREAVVISO[tipo][livello][fascia]


def mensilita_aggiuntiva(retribuzione_mensile: float, dodicesimi_maturati: int) -> float:
    """Tredicesima o quattordicesima per i dodicesimi maturati (F11)."""
    return centesimi(retribuzione_mensile * dodicesimi_maturati / 12)


def ferie_non_godute(retribuzione_mensile: float, giorni: float) -> float:
    """Indennità per le ferie non godute: 1/26 della retribuzione mensile per giorno (F12)."""
    return centesimi(retribuzione_mensile / C.DIVISORE_GIORNALIERO * giorni)


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
