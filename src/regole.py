"""
Le regole contrattuali che i controlli applicano, scritte una volta sola. Le stesse regole sono
riscritte come formule nel foglio di controllo (build_foglio.py), e il foglio Riconciliazione
verifica che diano lo stesso risultato.
"""
import calendar
from datetime import date, timedelta
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


def aliquota_dipendente(media_semestre: float) -> float:
    """Aliquota a carico del dipendente per la posizione INPS (F05, F14): IVS, più la CIGS se nel semestre la media
    supera 15 dipendenti, più un terzo del contributo FIS. Sommate in quest'ordine, come la formula del foglio."""
    cigs = C.CIGS_DIPENDENTE if media_semestre > C.CIGS_SOGLIA else 0.0
    fis = C.FIS_ALIQUOTA["fino_a_5" if media_semestre <= C.FIS_SOGLIA else "oltre_5"]
    return C.ALIQUOTA_DIPENDENTE + cigs + fis / C.FIS_QUOTA_DIPENDENTE


def media_cliente(cliente: str) -> float:
    return C.CLIENTI[cliente]["media_semestre"]


def contributi(lordo: float, media_semestre: float) -> float:
    """Contributo a carico del dipendente: aliquota della posizione sull'imponibile arrotondato all'euro, più l'1% sulla
    parte oltre la prima fascia pensionabile mensilizzata (F15), poi al centesimo."""
    imponibile = euro(lordo)
    return centesimi(imponibile * aliquota_dipendente(media_semestre)
                     + max(0.0, imponibile - C.PRIMA_FASCIA_MENSILE) * C.ALIQUOTA_AGGIUNTIVA)


def quota_tfr(retribuzione_ordinaria: float) -> float:
    return centesimi(retribuzione_ordinaria * C.MENSILITA / C.DIVISORE_TFR / 12)


def ferie_mese() -> float:
    return round(C.FERIE_ANNUE / 12, 4)


def arrotonda(x: float, cifre: int) -> float:
    """Come ROUND di Excel con `cifre` decimali: 15 cifre significative, poi metà per eccesso."""
    q = Decimal(1).scaleb(-cifre)
    return float(Decimal(f"{float(x):.15g}").quantize(q, rounding=ROUND_HALF_UP))


# ---- Assenze ------------------------------------------------------------------------------------
def ultimo_del_mese(mese: str) -> date:
    y, m = map(int, mese.split("-"))
    return date(y, m, calendar.monthrange(y, m)[1])


def _sovrapposti(da: date, a: date, inizio: date, fine: date) -> int:
    """Giorni di calendario comuni a [da, a] e [inizio, fine]."""
    return max(0, (min(a, fine) - max(da, inizio)).days + 1)


def rmgg(retribuzione_mese_prima: float) -> float:
    """Retribuzione media globale giornaliera di un impiegato: retribuzione teorica del mese prima × mensilità / 12,
    diviso 30 (INPS, circ. 94/2009; F17)."""
    return centesimi(retribuzione_mese_prima * C.MENSILITA / 12 / C.DIVISORE_RMGG)


def giorni_malattia(dal: date, al: date, mese: str) -> tuple[int, int, int]:
    """Giorni dell'evento nel mese, per fascia: carenza (1°-3° giorno), al 50% (4°-20°), al 66,66% (21°-180°).
    Contano i giorni di calendario dall'inizio dell'evento, domeniche comprese (F16)."""
    inizio, fine = max(dal, primo_del_mese(mese)), min(al, ultimo_del_mese(mese))
    (f1, _), (f2, _) = C.MALATTIA_FASCE
    giorno = lambda k: dal + timedelta(days=k - 1)      # il k-esimo giorno dell'evento
    carenza = _sovrapposti(dal, giorno(C.MALATTIA_CARENZA), inizio, fine)
    al_50 = _sovrapposti(giorno(C.MALATTIA_CARENZA + 1), giorno(f1), inizio, fine)
    al_66 = _sovrapposti(giorno(f1 + 1), giorno(f2), inizio, fine)
    return carenza, al_50, al_66


def indennita_malattia(retribuzione_mese_prima: float, dal: date, al: date, mese: str) -> float:
    """Indennità di malattia INPS anticipata nel mese (F16, F17)."""
    _, n50, n66 = giorni_malattia(dal, al, mese)
    (_, p50), (_, p66) = C.MALATTIA_FASCE
    g = rmgg(retribuzione_mese_prima)
    return centesimi(g * p50 * n50 + g * p66 * n66)


def carenza_percentuale(evento_n: int, esente: bool) -> float:
    """Quota dell'integrazione dei primi 3 giorni che il datore di lavoro deve pagare (F16)."""
    if esente:
        return 1.0
    return C.CARENZA_PERCENTUALI[evento_n - 1] if 1 <= evento_n <= len(C.CARENZA_PERCENTUALI) else 0.0


def indennita_maternita(retribuzione_mese_prima: float, dal: date, al: date, mese: str) -> float:
    """Indennità di maternità INPS anticipata nel mese: 80% della stessa base, per ogni giorno (F18)."""
    giorni = _sovrapposti(dal, al, primo_del_mese(mese), ultimo_del_mese(mese))
    return centesimi(rmgg(retribuzione_mese_prima) * C.MATERNITA_PERCENTUALE * giorni)


def permessi_mese(assunzione: date, mese: str, dipendenti: float, part_time: float) -> float:
    """Ore di permesso maturate nel mese: riduzione d'orario ed ex festività per dodicesimi, in proporzione al
    part-time; la riduzione d'orario al 50% dopo 2 anni e al 100% dopo 4 per chi è entrato dopo il 1° marzo 2011 (F23).
    Gli anni si contano all'ultimo giorno del mese."""
    rol = C.ROL_ORE["oltre_15" if dipendenti > C.ROL_SOGLIA else "fino_a_15"]
    quota = 1.0
    if assunzione > date.fromisoformat(C.ROL_NUOVI_ASSUNTI):
        anni = anni_di_servizio(assunzione, ultimo_del_mese(mese))
        quota = 0.0 if anni < 2 else 0.5 if anni < 4 else 1.0
    return round((rol * quota + C.EX_FESTIVITA_ORE) / 12 * part_time, 4)


# ---- TFR alla cessazione --------------------------------------------------------------------------
def coefficiente_tfr(cessazione: date) -> float | None:
    """Coefficiente di rivalutazione del fondo al 31 dicembre, in percentuale con 6 decimali come lo pubblica l'ISTAT:
    1,5% annuo fisso per i mesi interi (il mese conta se la cessazione cade dal 15 in poi) più il 75% dell'aumento del
    FOI rispetto a dicembre (F19, F20). None se l'indice del mese non è nei parametri."""
    m = cessazione.month if cessazione.day >= 15 else cessazione.month - 1
    if m == 0:
        return 0.0
    foi = C.FOI_MESI.get(f"{cessazione.year}-{m:02d}")
    if foi is None:
        return None
    variazione = (foi * C.FOI_RACCORDO / C.FOI_DICEMBRE - 1) * 100
    return arrotonda(C.TFR_TASSO_FISSO * m / 12 + C.TFR_QUOTA_INFLAZIONE * variazione, 6)


def tfr_liquidato(fondo: float, quote_anno: float, imponibile_anno: float, cessazione: date) -> float | None:
    """TFR lordo alla cessazione: fondo al 31 dicembre, più la rivalutazione al netto dell'imposta sostitutiva del 17%,
    più le quote dell'anno meno lo 0,50% dell'imponibile previdenziale dell'anno (F19-F22)."""
    c = coefficiente_tfr(cessazione)
    if c is None:
        return None
    rivalutazione = centesimi(fondo * c / 100)
    imposta = centesimi(rivalutazione * C.IMPOSTA_SOSTITUTIVA_TFR)
    contributo = centesimi(imponibile_anno * C.CONTRIBUTO_TFR)
    return centesimi(fondo + rivalutazione - imposta + quote_anno - contributo)
