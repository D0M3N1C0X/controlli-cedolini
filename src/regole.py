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


T = "terziario"
_TABELLE: dict = {}


def regola(ccnl: str) -> dict:
    return C.CCNL[ccnl]


def ccnl_cliente(cliente) -> str:
    """Il CCNL del cliente; per un cliente che non è nei parametri, il Terziario."""
    return C.CLIENTI.get(cliente, {}).get("ccnl", T)


def tabella(ccnl: str = T) -> pd.DataFrame:
    if ccnl not in _TABELLE:
        _TABELLE[ccnl] = pd.read_csv(regola(ccnl)["tabella"], dtype={"livello": str}).set_index("livello")
    return _TABELLE[ccnl]


def primo_del_mese(mese: str) -> date:
    y, m = map(int, mese.split("-"))
    return date(y, m, 1)


def scatti_maturati(assunzione: date, mese: str, ccnl: str = T) -> int:
    """Scatti in pagamento nel mese: ogni periodo compiuto (triennio nel Terziario) conta dal mese successivo, fino al
    massimo del CCNL."""
    inizio = primo_del_mese(mese)
    g = regola(ccnl)
    n = 0
    for k in range(1, g["scatti_max"] + 1):
        y, m = assunzione.year + g["scatti_anni"] * k, assunzione.month
        # il triennio si compie nel mese (y, m): l'aumento parte dal mese dopo
        if (inizio.year, inizio.month) > (y, m):
            n = k
    return n


def dodicesimi(assunzione: date, mese: str, inizio: date, ccnl: str = T) -> int:
    """Mesi di servizio da `inizio` al mese del cedolino compreso. Il mese di assunzione conta se i giorni di
    servizio sono almeno quelli del CCNL (15 nel Terziario, più di 15 nel Metalmeccanico e nella Logistica); chi è
    assunto prima di `inizio` matura tutti i mesi del periodo."""
    fine = primo_del_mese(mese)
    if assunzione <= inizio:
        return (fine.year - inizio.year) * 12 + fine.month - inizio.month + 1
    giorni = calendar.monthrange(assunzione.year, assunzione.month)[1] - assunzione.day + 1
    return ((fine.year - assunzione.year) * 12 + fine.month - assunzione.month
            + (1 if giorni >= regola(ccnl)["giorni_mese_intero"] else 0))


def ha_quattordicesima(ccnl: str = T) -> bool:
    return regola(ccnl)["mensilita"] >= 14


def ratei_13(assunzione: date, mese: str, ccnl: str = T) -> int:
    """Dodicesimi di tredicesima maturati nell'anno solare, fino al mese del cedolino."""
    return dodicesimi(assunzione, mese, date(primo_del_mese(mese).year, 1, 1), ccnl)


def ratei_14(assunzione: date, mese: str, ccnl: str = T) -> int:
    """Dodicesimi di quattordicesima maturati da luglio (dell'anno, o di quello prima se il mese è prima di luglio).
    Zero se il CCNL non ha la quattordicesima (Metalmeccanico)."""
    if not ha_quattordicesima(ccnl):
        return 0
    m = primo_del_mese(mese)
    return dodicesimi(assunzione, mese, date(m.year if m.month >= 7 else m.year - 1, 7, 1), ccnl)


def dodicesimi_alla_cessazione(assunzione: date, cessazione: date, inizio: date, ccnl: str = T) -> int:
    """Mesi di servizio da `inizio` alla data di cessazione. Il primo e l'ultimo mese contano se i giorni di
    servizio in quel mese sono almeno quelli del CCNL (F11). Nel Turismo le due frazioni si sommano: un dodicesimo
    ogni 30 giorni, più uno per il resto di almeno 15 (F33)."""
    g = regola(ccnl)
    gm = g["giorni_mese_intero"]
    da = max(assunzione, inizio)
    if cessazione < da:
        return 0
    if (da.year, da.month) == (cessazione.year, cessazione.month):
        return 1 if (cessazione - da).days + 1 >= gm else 0
    f1 = calendar.monthrange(da.year, da.month)[1] - da.day + 1
    f2 = cessazione.day
    in_mezzo = (cessazione.year - da.year) * 12 + cessazione.month - da.month - 1
    if g["somma_frazioni"] and da.day > 1 and cessazione.day < calendar.monthrange(cessazione.year,
                                                                                    cessazione.month)[1]:
        return in_mezzo + (f1 + f2) // 30 + (1 if (f1 + f2) % 30 >= gm else 0)
    return in_mezzo + int(f1 >= gm) + int(f2 >= gm)


def inizio_13(giorno: date) -> date:
    return date(giorno.year, 1, 1)


def inizio_14(giorno: date) -> date:
    return date(giorno.year if giorno.month >= 7 else giorno.year - 1, 7, 1)


def ratei_al(assunzione: date, mese: str, cessazione: date | None = None, ccnl: str = T) -> tuple[int, int]:
    """Dodicesimi di tredicesima e quattordicesima maturati nel cedolino del mese: fino al mese compreso, o fino
    alla data di cessazione se il dipendente lascia (l'ultimo mese conta con i giorni del CCNL)."""
    if cessazione is None:
        return ratei_13(assunzione, mese, ccnl), ratei_14(assunzione, mese, ccnl)
    return (dodicesimi_alla_cessazione(assunzione, cessazione, inizio_13(cessazione), ccnl),
            dodicesimi_alla_cessazione(assunzione, cessazione, inizio_14(cessazione), ccnl)
            if ha_quattordicesima(ccnl) else 0)


def dodicesimi_14_pagata(assunzione: date, mese: str, ccnl: str = T) -> int:
    """I dodicesimi di una quattordicesima pagata nel mese a chi resta. Si paga a giugno o a luglio per il periodo
    luglio-giugno: da luglio in poi il periodo è quello chiuso il 30 giugno, non quello appena cominciato."""
    m = primo_del_mese(mese)
    if m.month < 7:
        return ratei_14(assunzione, mese, ccnl)
    fine = date(m.year, 6, 30)
    return dodicesimi_alla_cessazione(assunzione, fine, inizio_14(fine), ccnl)


def base_quattordicesima(mensile: float, scatti: float, ccnl: str = T) -> float:
    """La retribuzione su cui si calcola la quattordicesima: nel Turismo senza gli scatti (F33)."""
    return centesimi(mensile - scatti) if regola(ccnl)["quattordicesima_senza_scatti"] else mensile


def anni_di_servizio(assunzione: date, al: date) -> int:
    """Anni interi di servizio compiuti alla data."""
    return al.year - assunzione.year - ((al.month, al.day) < (assunzione.month, assunzione.day))


def preavviso_minimo(tipo: str, livello: str, assunzione: date, cessazione: date, ccnl: str = T) -> float:
    """Giorni di preavviso del CCNL (F13, F34, F36, F38): fino a 5 anni di servizio, dal 6° al 10° anno, oltre il
    10°. I mesi dei CCNL sono contati 30 giorni (D29)."""
    anni = anni_di_servizio(assunzione, cessazione)
    fascia = 0 if anni < 5 else 1 if anni < 10 else 2
    return regola(ccnl)["preavviso"][tipo][livello][fascia]


def mensilita_aggiuntiva(retribuzione_mensile: float, dodicesimi_maturati: int) -> float:
    """Tredicesima o quattordicesima per i dodicesimi maturati (F11)."""
    return centesimi(retribuzione_mensile * dodicesimi_maturati / 12)


def ferie_non_godute(retribuzione_mensile: float, giorni: float, ccnl: str = T) -> float:
    """Indennità per le ferie non godute: la quota giornaliera del CCNL per giorno, 1/26 della retribuzione mensile
    (F12), 1/22 nella Logistica con la settimana di 5 giorni (F38)."""
    return centesimi(retribuzione_mensile / regola(ccnl)["divisore_giornaliero"] * giorni)


def centesimi(x: float) -> float:
    """Arrotonda al centesimo come ROUND di Excel: 15 cifre significative, poi metà per eccesso."""
    v = Decimal(f"{float(x):.15g}").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return float(v)


def tabellare(livello: str, part_time: float, colonna: str | None = None, ccnl: str = T) -> float:
    return centesimi(tabella(ccnl).loc[livello, colonna or regola(ccnl)["minimo"]] * part_time)


def scatti_importo(livello: str, n: int, part_time: float, ccnl: str = T) -> float:
    return centesimi(tabella(ccnl).loc[livello, "scatto"] * n * part_time)


def euro(x: float) -> float:
    """Arrotonda all'unità di euro, metà per eccesso: così si arrotonda l'imponibile contributivo (F10)."""
    return float(Decimal(f"{float(x):.15g}").quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def aliquota_dipendente(media_semestre: float, fis: bool = True) -> float:
    """Aliquota a carico del dipendente per la posizione INPS (F05, F14): IVS, più la CIGS se nel semestre la media
    supera 15 dipendenti, più un terzo del contributo FIS se il cliente lo versa (un'impresa industriale no, F31).
    Sommate in quest'ordine, come la formula del foglio."""
    cigs = C.CIGS_DIPENDENTE if media_semestre > C.CIGS_SOGLIA else 0.0
    quota = C.FIS_ALIQUOTA["fino_a_5" if media_semestre <= C.FIS_SOGLIA else "oltre_5"] if fis else 0.0
    return C.ALIQUOTA_DIPENDENTE + cigs + quota / C.FIS_QUOTA_DIPENDENTE


def media_cliente(cliente: str) -> float:
    return C.CLIENTI[cliente]["media_semestre"]


def fis_cliente(cliente: str) -> bool:
    return C.CLIENTI[cliente].get("fis", True)


def aliquota_cliente(cliente: str) -> float:
    return aliquota_dipendente(media_cliente(cliente), fis_cliente(cliente))


def contributi(lordo: float, media_semestre: float, fis: bool = True) -> float:
    """Contributo a carico del dipendente: aliquota della posizione sull'imponibile arrotondato all'euro, più l'1% sulla
    parte oltre la prima fascia pensionabile mensilizzata (F15), poi al centesimo. `lordo` è l'imponibile
    previdenziale: le indennità INPS di malattia e maternità non ne fanno parte (F41)."""
    imponibile = euro(lordo)
    return centesimi(imponibile * aliquota_dipendente(media_semestre, fis)
                     + max(0.0, imponibile - C.PRIMA_FASCIA_MENSILE) * C.ALIQUOTA_AGGIUNTIVA)


def contributi_cliente(imponibile: float, cliente: str) -> float:
    return contributi(imponibile, media_cliente(cliente), fis_cliente(cliente))


def retribuzione_annua(mensile: float, scatti: float = 0.0, ccnl: str = T) -> float:
    """La retribuzione di un anno: la mensile per le mensilità del CCNL, meno gli scatti della quattordicesima nel
    Turismo. Non arrotondata: è la base di TFR e retribuzione media giornaliera."""
    g = regola(ccnl)
    return mensile * g["mensilita"] - (scatti if g["quattordicesima_senza_scatti"] else 0.0)


def quota_tfr(retribuzione_ordinaria: float, scatti: float = 0.0, ccnl: str = T) -> float:
    return centesimi(retribuzione_annua(retribuzione_ordinaria, scatti, ccnl) / C.DIVISORE_TFR / 12)


def ferie_annue(ccnl: str = T, anni: int = 0) -> int:
    """Giorni di ferie dell'anno: 26 nel Terziario e nel Turismo, 22 nella Logistica (settimana di 5 giorni), 4
    settimane di 6 giorni nel Metalmeccanico, con un giorno in più oltre 10 anni e una settimana oltre 18 (F32)."""
    giorni = 0
    for da, g in regola(ccnl)["ferie"]:
        if anni >= da:
            giorni = g
    return giorni


def ferie_mese(ccnl: str = T, anni: int = 0) -> float:
    return round(ferie_annue(ccnl, anni) / 12, 4)


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


def rmgg(retribuzione_mese_prima: float, scatti: float = 0.0, ccnl: str = T) -> float:
    """Retribuzione media globale giornaliera di un impiegato: retribuzione teorica del mese prima × mensilità / 12,
    diviso 30 (INPS, circ. 94/2009; F17); nel Turismo la quattordicesima senza gli scatti."""
    return centesimi(retribuzione_annua(retribuzione_mese_prima, scatti, ccnl) / 12 / C.DIVISORE_RMGG)


def giorni_malattia(dal: date, al: date, mese: str, ccnl: str = T) -> tuple[int, int, int]:
    """Giorni dell'evento nel mese, per fascia: carenza (1°-3° giorno), prima fascia (4°-20°), seconda (21°-180°).
    Contano i giorni di calendario dall'inizio dell'evento, domeniche comprese (F16)."""
    inizio, fine = max(dal, primo_del_mese(mese)), min(al, ultimo_del_mese(mese))
    (f1, _), (f2, _) = regola(ccnl)["malattia_fasce"]
    giorno = lambda k: dal + timedelta(days=k - 1)      # il k-esimo giorno dell'evento
    carenza = _sovrapposti(dal, giorno(C.MALATTIA_CARENZA), inizio, fine)
    al_50 = _sovrapposti(giorno(C.MALATTIA_CARENZA + 1), giorno(f1), inizio, fine)
    al_66 = _sovrapposti(giorno(f1 + 1), giorno(f2), inizio, fine)
    return carenza, al_50, al_66


def indennita_malattia(retribuzione_mese_prima: float, dal: date, al: date, mese: str, scatti: float = 0.0,
                       ccnl: str = T) -> float:
    """Indennità di malattia INPS anticipata nel mese (F16, F17): 50% e 66,66%, 80% nei pubblici esercizi (F37).
    Zero per gli impiegati dell'industria, che l'INPS non indennizza (F35)."""
    g = regola(ccnl)
    if not g["malattia_inps"]:
        return 0.0
    _, n50, n66 = giorni_malattia(dal, al, mese, ccnl)
    (_, p50), (_, p66) = g["malattia_fasce"]
    base = rmgg(retribuzione_mese_prima, scatti, ccnl)
    return centesimi(base * p50 * n50 + base * p66 * n66)


def carenza_percentuale(evento_n: int, esente: bool, ccnl: str = T, durata: int = 0) -> float:
    """Quota dei primi 3 giorni di malattia che il datore di lavoro deve pagare (F16, F35, F37, F39). `durata` sono
    i giorni di calendario dell'evento."""
    regola_ = regola(ccnl)["carenza"]
    if regola_ == "turismo":
        return 1.0 if durata > C.CARENZA_TURISMO_DURATA else 0.0
    if esente or regola_ == "logistica":
        return 1.0
    if regola_ == "metalmeccanico":
        m = C.CARENZA_METALMECCANICO
        if durata > m["durata_max"] or evento_n < m["dal_evento"]:
            return 1.0
        return m["quote"][min(evento_n - m["dal_evento"], len(m["quote"]) - 1)]
    return C.CARENZA_PERCENTUALI[evento_n - 1] if 1 <= evento_n <= len(C.CARENZA_PERCENTUALI) else 0.0


def indennita_maternita(retribuzione_mese_prima: float, dal: date, al: date, mese: str, scatti: float = 0.0,
                        ccnl: str = T) -> float:
    """Indennità di maternità INPS anticipata nel mese: 80% della stessa base, per ogni giorno (F18)."""
    giorni = _sovrapposti(dal, al, primo_del_mese(mese), ultimo_del_mese(mese))
    return centesimi(rmgg(retribuzione_mese_prima, scatti, ccnl) * C.MATERNITA_PERCENTUALE * giorni)


def permessi_mese(assunzione: date, mese: str, dipendenti: float, part_time: float, ccnl: str = T) -> float:
    """Ore di permesso maturate nel mese: riduzione d'orario ed ex festività per dodicesimi, in proporzione al
    part-time; la riduzione d'orario al 50% dopo 2 anni e al 100% dopo 4 per chi è entrato dopo la data del CCNL
    (Terziario: 1° marzo 2011, F23; Turismo: dal 2018, F37). Gli anni si contano all'ultimo giorno del mese."""
    g = regola(ccnl)
    rol = g["rol"]["oltre_15" if dipendenti > C.ROL_SOGLIA else "fino_a_15"]
    quota = 1.0
    if g["rol_nuovi_assunti"] and assunzione > date.fromisoformat(g["rol_nuovi_assunti"]):
        anni = anni_di_servizio(assunzione, ultimo_del_mese(mese))
        quota = 0.0 if anni < 2 else 0.5 if anni < 4 else 1.0
    return round((rol * quota + g["ex_festivita"]) / 12 * part_time, 4)


# ---- Retribuzione del mese con un'assenza e integrazione del datore di lavoro (v2.2, C22) ------------------------
def giorni_assenza(dal: date, al: date, mese: str) -> int:
    """Giorni di calendario dell'assenza dentro il mese."""
    return _sovrapposti(dal, al, primo_del_mese(mese), ultimo_del_mese(mese))


def giorni_del_mese(mese: str) -> int:
    return ultimo_del_mese(mese).day


def trattenuta_assenza(mensile: float, giorni: int, mese: str) -> float:
    """La retribuzione dei giorni di assenza, tolta dal mese: in proporzione ai giorni di calendario (D31)."""
    return centesimi(mensile * giorni / giorni_del_mese(mese))


def importo_carenza(mensile: float, giorni: int, quota: float, mese: str) -> float:
    """I primi giorni di malattia pagati dal datore di lavoro, alla quota del CCNL, con la stessa misura giornaliera."""
    return centesimi(mensile * giorni / giorni_del_mese(mese) * quota)


def integrazione_lorda(mensile: float, inps: float, dal: date, al: date, mese: str, ccnl: str = T) -> float | None:
    """Integrazione del datore sul lordo (Metalmeccanico, Logistica; F35, F39): indennità INPS più integrazione
    arrivano alla quota garantita della retribuzione dei giorni dopo la carenza. None se il CCNL non la regola così."""
    g = regola(ccnl)["integrazione"]
    if g is None or g["base"] != "lordo":
        return None
    _, n1, n2 = giorni_malattia(dal, al, mese, ccnl)
    q1, q2 = g["quote"]
    dovuta = mensile * (n1 * q1 + n2 * q2) / giorni_del_mese(mese)
    return centesimi(max(0.0, dovuta - inps))


def netto_normale(mensile: float, cliente: str) -> float:
    """Il netto di un mese senza assenze, prima delle altre trattenute: retribuzione meno contributi e IRPEF del mese,
    più cuneo e trattamento integrativo (C20)."""
    imponibile = centesimi(mensile - contributi_cliente(mensile, cliente))
    f = irpef_mese(imponibile, regola(ccnl_cliente(cliente))["mensilita"])
    return centesimi(imponibile - f["irpef"] + f["bonus_cuneo"] + f["trattamento_integrativo"])


def quota_netto_garantita(mese: str, ccnl: str = T, malattia: tuple | None = None,
                          quota_carenza: float = 0.0) -> float | None:
    """La parte del netto normale che il mese con l'assenza deve almeno dare, se il CCNL integra sul netto
    (Terziario, F16, F18): i giorni lavorati per intero, i giorni di carenza alla quota dovuta, quelli dal 4° al 20°
    al 75%, dal 21° al 100%; i giorni di maternità al 100%, come quelli lavorati. `malattia` è (dal, al). None se il
    CCNL non integra sul netto."""
    g = regola(ccnl)["integrazione"]
    if g is None or g["base"] != "netto":
        return None
    G = giorni_del_mese(mese)
    if not malattia:
        return G / G
    n0, n1, n2 = giorni_malattia(*malattia, mese, ccnl)
    q1, q2 = g["quote"]
    # nello stesso ordine della formula del foglio
    return (G - giorni_assenza(*malattia, mese) + n0 * quota_carenza + n1 * q1 + n2 * q2) / G


def netto_garantito(mensile: float, cliente: str, quota: float) -> float:
    return centesimi(netto_normale(mensile, cliente) * quota)


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


# ---- IRPEF 2026 ------------------------------------------------------------------------------------------------
def imposta_lorda(reddito: float, periodi: int = 1, scaglioni=None) -> float:
    """Imposta lorda per scaglioni (F24). Con `periodi` = 12 gli scaglioni annui sono ragguagliati al mese, come vuole
    l'art. 23 c. 2 DPR 600/1973 per la ritenuta del periodo di paga. Non arrotondata."""
    imposta, sotto = 0.0, 0.0
    for limite, aliquota in scaglioni or C.SCAGLIONI_IRPEF:
        tetto = reddito if limite is None else min(reddito, limite / periodi)
        if tetto > sotto:
            imposta += (tetto - sotto) * aliquota
        if limite is None or reddito <= limite / periodi:
            break
        sotto = limite / periodi
    return imposta


def detrazione_lavoro(reddito: float) -> float:
    """Detrazione annua per lavoro dipendente, art. 13 c. 1 e 1.1 TUIR (F25), prima del rapporto al periodo.
    I rapporti hanno quattro decimali (c. 6)."""
    d = C.DETRAZIONE_LAVORO
    s1, s2, s3 = d["soglie"]
    if reddito <= s1:
        base = d["base"]
    elif reddito <= s2:
        base = d["fascia2"] + d["fascia2_extra"] * arrotonda((s2 - reddito) / (s2 - s1), C.DECIMALI_RAPPORTO)
    elif reddito <= s3:
        base = d["fascia2"] * arrotonda((s3 - reddito) / (s3 - s2), C.DECIMALI_RAPPORTO)
    else:
        base = 0.0
    lo, hi = d["bonus_65_soglie"]
    return base + (d["bonus_65"] if lo < reddito <= hi else 0.0)


def detrazione_cuneo(reddito: float) -> float:
    """Ulteriore detrazione annua, L. 207/2024 art. 1 c. 6 (F26): 1.000 € tra 20.000 e 32.000 €, poi a scalare fino
    a 40.000 €; il rapporto con quattro decimali come nell'art. 13 (S10)."""
    d = C.CUNEO_DETRAZIONE
    s1, s2, s3 = d["soglie"]
    if s1 < reddito <= s2:
        return d["importo"]
    if s2 < reddito <= s3:
        return d["importo"] * arrotonda((s3 - reddito) / (s3 - s2), C.DECIMALI_RAPPORTO)
    return 0.0


def percentuale_cuneo(reddito_annuo: float) -> float:
    """Percentuale della somma non imponibile, L. 207/2024 art. 1 c. 4 (F26), sul reddito di lavoro rapportato
    all'anno (c. 5)."""
    for limite, p in C.CUNEO_SOMMA_FASCE:
        if limite is None or reddito_annuo <= limite:
            return p
    return 0.0


def trattamento_integrativo(reddito: float, lorda: float, detrazione: float, frazione: float) -> float:
    """Trattamento integrativo dell'anno, D.L. 3/2020 art. 1 (F27), rapportato al periodo (`frazione`). Fino a
    15.000 € se l'imposta lorda supera la detrazione dell'art. 13 meno 75 € rapportati; tra 15.000 e 28.000 € la
    differenza tra detrazioni e imposta lorda, se positiva (nessun'altra detrazione nel modello, S11)."""
    t = C.TRATTAMENTO_INTEGRATIVO
    tetto = t["importo"] * frazione
    if reddito <= t["soglia"]:
        return tetto if lorda > detrazione - t["riduzione_capienza"] * frazione else 0.0
    if reddito <= t["soglia_alta"] and detrazione > lorda:
        return min(tetto, detrazione - lorda)
    return 0.0


def irpef_mese(imponibile: float, mensilita: int = C.MENSILITA, scaglioni=None) -> dict:
    """La ritenuta del mese e le somme del cuneo e del trattamento integrativo (C20). Reddito dell'anno presunto =
    imponibile × mensilità (S09); detrazioni e trattamento integrativo per un dodicesimo (S08)."""
    annuo = imponibile * mensilita
    lorda = imposta_lorda(imponibile, 12, scaglioni)
    det = detrazione_lavoro(annuo)
    ritenuta = centesimi(max(0.0, lorda - det / 12 - detrazione_cuneo(annuo) / 12))
    somma = centesimi(imponibile * percentuale_cuneo(annuo)) if annuo <= C.CUNEO_SOMMA_SOGLIA else 0.0
    ti = centesimi(trattamento_integrativo(annuo, imposta_lorda(annuo, 1, scaglioni), det, 1.0) / 12)
    return {"irpef": ritenuta, "bonus_cuneo": somma, "trattamento_integrativo": ti}


def conguaglio_cessazione(imponibile_anno: float, giorni: int, ritenute_prec: float, cuneo_prec: float,
                          ti_prec: float, scaglioni=None, rapporta: bool = True) -> dict:
    """Conguaglio IRPEF alla cessazione (art. 23 c. 3 DPR 600/1973, C21): imposta dell'anno sull'imponibile da
    gennaio, detrazioni e trattamento integrativo rapportati ai giorni di lavoro, meno quanto già trattenuto o
    erogato nei mesi prima. Ritorna le voci del cedolino di uscita: positive = da trattenere o da erogare."""
    frazione = giorni / C.GIORNI_ANNO if rapporta else 1.0
    lorda = imposta_lorda(imponibile_anno, 1, scaglioni)
    det = detrazione_lavoro(imponibile_anno) * frazione
    if imponibile_anno <= C.DETRAZIONE_LAVORO["soglie"][0]:
        det = max(det, C.DETRAZIONE_LAVORO["minimo"])
    netta = centesimi(max(0.0, lorda - det - detrazione_cuneo(imponibile_anno) * frazione))
    annuo = imponibile_anno * C.GIORNI_ANNO / giorni
    somma = centesimi(imponibile_anno * percentuale_cuneo(annuo)) if imponibile_anno <= C.CUNEO_SOMMA_SOGLIA else 0.0
    ti = centesimi(trattamento_integrativo(imponibile_anno, lorda, det, frazione))
    return {"irpef": centesimi(netta - ritenute_prec), "bonus_cuneo": centesimi(somma - cuneo_prec),
            "trattamento_integrativo": centesimi(ti - ti_prec), "imposta_netta": netta}
