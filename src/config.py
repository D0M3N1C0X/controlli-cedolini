"""
Tutti i parametri dei controlli, in un solo posto e con la loro fonte. Il foglio Parametri del
file Excel è scritto da qui: Python e foglio partono dagli stessi numeri.
"""
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CCNL_TERZIARIO = DATA / "ccnl_terziario.csv"
DIPENDENTI = DATA / "dipendenti.csv"
CEDOLINI = DATA / "cedolini.csv"
F24 = DATA / "f24.csv"
ERRORI = DATA / "errori_inseriti.csv"
DELIVERABLES = ROOT / "deliverables"
REPORT = ROOT / "report"

SEED = 2026
MESE_PRECEDENTE = "2026-08"
MESE = "2026-09"                 # il mese elaborato e controllato
PROSSIMA_TRANCHE = date(2026, 11, 1)

# Clienti sintetici. A, B e C applicano il CCNL Terziario Distribuzione e Servizi (Confcommercio); D, E e F i tre CCNL
# della v2.2. "media_semestre" è la media dei dipendenti nel semestre di riferimento, che decide FIS e CIGS (F14): il
# cliente A è cresciuto da poco e nel semestre era sotto i 15, anche se oggi ne ha 18. "fis": il cliente versa al FIS;
# un'impresa industriale no, ha la CIGO, che è tutta a carico del datore di lavoro (F31).
CLIENTI = {
    "A": {"nome": "Cliente A · negozio al dettaglio", "dipendenti": 18, "media_semestre": 14.5, "ccnl": "terziario"},
    "B": {"nome": "Cliente B · commercio all'ingrosso", "dipendenti": 74, "media_semestre": 74.0, "ccnl": "terziario"},
    "C": {"nome": "Cliente C · servizi alle imprese", "dipendenti": 27, "media_semestre": 27.0, "ccnl": "terziario"},
    "D": {"nome": "Cliente D · progettazione meccanica", "dipendenti": 22, "media_semestre": 22.0,
          "ccnl": "metalmeccanico", "fis": False},
    "E": {"nome": "Cliente E · ristorante", "dipendenti": 16, "media_semestre": 16.0, "ccnl": "turismo"},
    "F": {"nome": "Cliente F · casa di spedizioni", "dipendenti": 20, "media_semestre": 19.0, "ccnl": "logistica"},
}
CLIENTI_V1 = ("A", "B", "C")     # i clienti dei dati d'esempio fino alla v2.1, generati per primi

# ---- Regole usate dai controlli ---------------------------------------------------------------
# Minimi: CCNL Terziario, tranche dal 1° novembre 2025 (vedi docs/fonti.md, F01).
COLONNA_MINIMO = "minimo_2025_11"
COLONNA_MINIMO_PROSSIMO = "minimo_2026_11"
# Scatti: uno ogni triennio, fino a 10, dal primo giorno del mese successivo al triennio (F03).
SCATTI_MAX = 10
SCATTI_ANNI = 3
# Contributi a carico del dipendente (F05, F14, F15). IVS 9,19%; CIGS 0,30% se nel semestre la media supera 15
# dipendenti; un terzo del contributo FIS (0,50% fino a 5 dipendenti di media, 0,80% oltre); l'1% sulla parte di
# retribuzione mensile oltre la prima fascia pensionabile mensilizzata, 4.685 € nel 2026 (INPS, circ. 6/2026).
ALIQUOTA_DIPENDENTE = 0.0919
CIGS_DIPENDENTE = 0.003
CIGS_SOGLIA = 15
FIS_ALIQUOTA = {"fino_a_5": 0.005, "oltre_5": 0.008}
FIS_SOGLIA = 5
FIS_QUOTA_DIPENDENTE = 3          # il FIS si divide due terzi al datore di lavoro, un terzo al lavoratore
ALIQUOTA_AGGIUNTIVA = 0.01
PRIMA_FASCIA_MENSILE = 4685.00
# TFR: quota annua = retribuzione annua / 13,5 (art. 2120 c.c.). Rateo mensile sulla retribuzione
# ordinaria per 14 mensilità, diviso 12 (F06).
DIVISORE_TFR = 13.5
MENSILITA = 14
# TFR alla cessazione (F19-F22). Il fondo al 31 dicembre si rivaluta con 1,5% annuo fisso per mese più il 75%
# dell'aumento dell'indice FOI rispetto a dicembre; il mese conta se la cessazione cade dal 15 in poi. Dal 2026 il FOI
# ha base 2025=100: si confronta con dicembre 2025 in base 2015 moltiplicando per il coefficiente di raccordo.
# Sulla rivalutazione, imposta sostitutiva del 17%; dalle quote dell'anno si toglie lo 0,50% dell'imponibile.
TFR_TASSO_FISSO = 1.5
TFR_QUOTA_INFLAZIONE = 0.75
FOI_DICEMBRE = 121.5              # dicembre 2025, base 2015=100
FOI_RACCORDO = 1.214              # da base 2025 a base 2015
FOI_MESI = {"2026-08": 103.7, "2026-09": 104.3}     # base 2025=100, dati definitivi ISTAT
IMPOSTA_SOSTITUTIVA_TFR = 0.17
CONTRIBUTO_TFR = 0.005
# Assenze. Malattia (F16): indennità INPS anticipata dal datore di lavoro, 50% dal 4° al 20° giorno e 66,66% dal 21°
# al 180°, sulla retribuzione media globale giornaliera = retribuzione del mese prima × mensilità / 12 / 30 (F17).
# Maternità: 80% della stessa base (F18). Carenza (F16): l'integrazione dei primi 3 giorni si paga per intero ai
# primi 2 eventi dell'anno, al 66% al 3°, al 50% al 4°, e non più dal 5°, salvo i casi esenti.
MALATTIA_CARENZA = 3
MALATTIA_FASCE = ((20, 0.5), (180, 0.6666))
MATERNITA_PERCENTUALE = 0.8
DIVISORE_RMGG = 30
CARENZA_PERCENTUALI = (1.0, 1.0, 0.66, 0.5)
# Permessi (F23): riduzione d'orario 56 ore l'anno, 72 nelle aziende con più di 15 dipendenti, più 32 ore di ex
# festività, per dodicesimi. Per chi è entrato dopo il 1° marzo 2011 la riduzione d'orario spetta al 50% dopo 2 anni
# e al 100% dopo 4; prima dei 2 anni, solo le ex festività. Il part-time matura in proporzione.
ROL_ORE = {"fino_a_15": 56, "oltre_15": 72}
ROL_SOGLIA = 15
EX_FESTIVITA_ORE = 32
ROL_NUOVI_ASSUNTI = "2011-03-01"
TOLLERANZA_ORE = 0.01
# Ferie: 26 giorni lavorativi l'anno, maturati per dodicesimi (F04).
FERIE_ANNUE = 26
# Variazione del netto rispetto al mese prima oltre la quale serve una spiegazione.
SOGLIA_VARIAZIONE = 0.20
TOLLERANZA = 0.01                # euro: un centesimo di arrotondamento
TOLLERANZA_FERIE = 0.01          # giorni
# Ratei di tredicesima e quattordicesima: un dodicesimo per mese di servizio nel periodo (gennaio-dicembre per la
# tredicesima, luglio-giugno per la quattordicesima); la frazione di mese di almeno 15 giorni conta intera (F11).
GIORNI_MESE_INTERO = 15
# Cessazioni. Quota giornaliera della retribuzione = retribuzione mensile / 26; ogni giorno di ferie non goduto si
# paga 1/26 della retribuzione mensile di fatto (F12). Preavviso minimo in giorni, per dimissioni e licenziamento,
# per livello e anni di servizio: fino a 5, dal 6° al 10°, oltre il 10° (F13). Vale anche per il part-time.
DIVISORE_GIORNALIERO = 26
PREAVVISO = {
    "dimissioni": {"Quadri": (45, 60, 90), "1": (45, 60, 90), "2": (20, 30, 45), "3": (20, 30, 45),
                   "4": (15, 20, 30), "5": (15, 20, 30), "6": (10, 15, 15), "7": (10, 15, 15)},
    "licenziamento": {"Quadri": (60, 90, 120), "1": (60, 90, 120), "2": (30, 45, 60), "3": (30, 45, 60),
                      "4": (20, 30, 45), "5": (20, 30, 45), "6": (15, 20, 20), "7": (15, 20, 20)},
}

# ---- IRPEF 2026 (F24-F29) --------------------------------------------------------------------------------------
# Scaglioni dell'art. 11 TUIR come sostituito dalla L. 207/2024 (art. 1 c. 2), con il 33% della L. 199/2025
# (art. 1 c. 3) al posto del 35% dal 2026. Limite superiore e aliquota; l'ultimo non ha limite.
SCAGLIONI_IRPEF = ((28000.0, 0.23), (50000.0, 0.33), (None, 0.43))
SCAGLIONI_IRPEF_2025 = ((28000.0, 0.23), (50000.0, 0.35), (None, 0.43))   # solo per gli errori inseriti
# Detrazione per lavoro dipendente, art. 13 c. 1 e 1.1 TUIR (testo in vigore nel 2026).
DETRAZIONE_LAVORO = {"base": 1955.0, "minimo": 690.0, "fascia2": 1910.0, "fascia2_extra": 1190.0,
                     "soglie": (15000.0, 28000.0, 50000.0), "bonus_65": 65.0, "bonus_65_soglie": (25000.0, 35000.0)}
DECIMALI_RAPPORTO = 4            # art. 13 c. 6: i rapporti si assumono nelle prime quattro cifre decimali
# Cuneo fiscale, L. 207/2024 art. 1: somma non imponibile fino a 20.000 € di reddito (c. 4-5) e ulteriore
# detrazione tra 20.000 e 40.000 € (c. 6), nel testo in vigore nel 2026.
CUNEO_SOMMA_SOGLIA = 20000.0
CUNEO_SOMMA_FASCE = ((8500.0, 0.071), (15000.0, 0.053), (None, 0.048))
CUNEO_DETRAZIONE = {"importo": 1000.0, "soglie": (20000.0, 32000.0, 40000.0)}
# Trattamento integrativo, D.L. 3/2020 art. 1: 1.200 € l'anno, rapportato al periodo di lavoro; la capienza si
# misura con la detrazione dell'art. 13 diminuita di 75 € rapportati al periodo (L. 207/2024 art. 1 c. 3).
TRATTAMENTO_INTEGRATIVO = {"importo": 1200.0, "soglia": 15000.0, "soglia_alta": 28000.0, "riduzione_capienza": 75.0}
# Ritenuta del mese (art. 23 c. 2 DPR 600/1973): scaglioni ragguagliati al mese, detrazioni rapportate al mese
# (un dodicesimo, S08); il reddito dell'anno che decide detrazioni e cuneo è presunto: imponibile del mese per le
# mensilità dell'anno (S09). Conguaglio alla cessazione (art. 23 c. 3): detrazioni rapportate ai giorni.
GIORNI_ANNO = 365


# ---- I quattro CCNL (v2.2, F30-F40) -----------------------------------------------------------------------------
# Le regole che cambiano da un CCNL all'altro; tutto il resto (INPS, TFR, IRPEF) vale per tutti. Il preavviso è in
# giorni di calendario: un mese conta 30 giorni (D29). "minimo" è la colonna della tabella in vigore a settembre 2026,
# "minimo_prec" quella della tranche prima (per gli errori inseriti), "minimo_prossimo" la prossima tranche.
# Integrazione della malattia: "netto" = il netto del mese non sta sotto la quota garantita del netto normale;
# "lordo" = indennità INPS più integrazione arrivano alla retribuzione dei giorni di malattia; None = nessuna.
# "quote" = quota garantita dal 4° al 20° giorno e dal 21° al 180°. "maternita_netto": il CCNL integra il congedo di
# maternità fino al 100% del netto (Terziario F18, Turismo F37); negli altri due non è stato verificato (D32).
_PREAVVISO_TERZIARIO = PREAVVISO
_metal = {**{lv: (60, 90, 120) for lv in ("B2", "B3", "A1")}, **{lv: (45, 60, 75) for lv in ("C2", "C3", "B1")},
          **{lv: (10, 20, 30) for lv in ("D1", "D2", "C1")}}
_turismo = {**{lv: (120, 150, 180) for lv in ("Qa", "Qb")}, "1": (60, 90, 120), **{lv: (30, 45, 60) for lv in ("2", "3")},
            **{lv: (20, 30, 45) for lv in ("4", "5")}, **{lv: (15, 20, 20) for lv in ("6s", "6", "7")}}
_log_lic = {**{lv: (75, 105, 135) for lv in ("Quadri", "1")}, "2": (45, 60, 75),
            **{lv: (30, 45, 60) for lv in ("3S", "3", "4", "4J", "5", "6")}}
CCNL = {
    "terziario": {
        "nome": "Terziario Distribuzione e Servizi (Confcommercio)", "tabella": DATA / "ccnl_terziario.csv",
        "minimo": "minimo_2025_11", "minimo_prec": "minimo_2025_03", "minimo_prossimo": "minimo_2026_11",
        "prossima_tranche": date(2026, 11, 1),
        "livelli": ["Quadri", "1", "2", "3", "4", "5", "6", "7"], "pesi": [1, 3, 8, 18, 34, 20, 10, 6],
        "scatti_max": 10, "scatti_anni": 3, "mensilita": 14, "quattordicesima_senza_scatti": False,
        "giorni_mese_intero": 15, "somma_frazioni": False, "ferie": ((0, 26),), "divisore_giornaliero": 26,
        "rol": {"fino_a_15": 56, "oltre_15": 72}, "ex_festivita": 32, "rol_nuovi_assunti": "2011-03-01",
        "preavviso": _PREAVVISO_TERZIARIO,
        "malattia_inps": True, "malattia_fasce": ((20, 0.5), (180, 0.6666)), "carenza": "terziario",
        "integrazione": {"base": "netto", "quote": (0.75, 1.0)}, "maternita_netto": True,
    },
    "metalmeccanico": {
        "nome": "Metalmeccanico industria (Federmeccanica-Assistal)", "tabella": DATA / "ccnl_metalmeccanico.csv",
        "minimo": "minimo_2026_06", "minimo_prec": "minimo_2025_06", "minimo_prossimo": "minimo_2027_06",
        "prossima_tranche": date(2027, 6, 1),
        # nei dati d'esempio solo impiegati (D30): niente D1 e D2, i livelli degli operai
        "livelli": ["C1", "C2", "C3", "B1", "B2", "B3", "A1"], "pesi": [2, 4, 6, 5, 3, 1, 1],
        "scatti_max": 5, "scatti_anni": 2, "mensilita": 13, "quattordicesima_senza_scatti": False,
        "giorni_mese_intero": 16, "somma_frazioni": False, "ferie": ((0, 24), (10, 25), (18, 30)),
        "divisore_giornaliero": 26,
        "rol": {"fino_a_15": 72, "oltre_15": 72}, "ex_festivita": 32, "rol_nuovi_assunti": None,
        "preavviso": {"dimissioni": _metal, "licenziamento": _metal},
        # gli impiegati dell'industria non hanno l'indennità INPS: la malattia è tutta a carico del datore (F35)
        "malattia_inps": False, "malattia_fasce": ((20, 0.5), (180, 0.6666)), "carenza": "metalmeccanico",
        "integrazione": {"base": "lordo", "quote": (1.0, 1.0)}, "maternita_netto": False,
    },
    "turismo": {
        "nome": "Turismo, pubblici esercizi (Fipe)", "tabella": DATA / "ccnl_turismo.csv",
        "minimo": "totale_2026_06", "minimo_prec": "totale_2025_06", "minimo_prossimo": "totale_2027_06",
        "prossima_tranche": date(2027, 6, 1),
        "livelli": ["Qb", "1", "2", "3", "4", "5", "6s", "6", "7"], "pesi": [1, 1, 2, 3, 4, 4, 2, 1, 1],
        "scatti_max": 6, "scatti_anni": 4, "mensilita": 14, "quattordicesima_senza_scatti": True,
        "giorni_mese_intero": 15, "somma_frazioni": True, "ferie": ((0, 26),), "divisore_giornaliero": 26,
        "rol": {"fino_a_15": 72, "oltre_15": 72}, "ex_festivita": 32, "rol_nuovi_assunti": "2017-12-31",
        "preavviso": {"dimissioni": _turismo, "licenziamento": _turismo},
        "malattia_inps": True, "malattia_fasce": ((20, 0.8), (180, 0.8)), "carenza": "turismo",
        "integrazione": None, "maternita_netto": True,
    },
    "logistica": {
        "nome": "Logistica, trasporto merci e spedizione (Confetra)", "tabella": DATA / "ccnl_logistica.csv",
        "minimo": "totale_2026_01", "minimo_prec": "minimo_2026_01", "minimo_prossimo": "totale_2027_01",
        "prossima_tranche": date(2027, 1, 1),
        "livelli": ["Quadri", "1", "2", "3S", "3", "4", "4J", "5", "6"], "pesi": [1, 1, 2, 3, 4, 4, 2, 2, 1],
        "scatti_max": 5, "scatti_anni": 2, "mensilita": 14, "quattordicesima_senza_scatti": False,
        "giorni_mese_intero": 16, "somma_frazioni": False, "ferie": ((0, 22),), "divisore_giornaliero": 22,
        "rol": {"fino_a_15": 40, "oltre_15": 40}, "ex_festivita": 32, "rol_nuovi_assunti": None,
        # impiegati (D30): per le dimissioni i termini del licenziamento ridotti della metà
        "preavviso": {"dimissioni": {lv: tuple(g / 2 for g in t) for lv, t in _log_lic.items()},
                      "licenziamento": _log_lic},
        "malattia_inps": True, "malattia_fasce": ((20, 0.5), (180, 0.6666)), "carenza": "logistica",
        "integrazione": {"base": "lordo", "quote": (1.0, 1.0)}, "maternita_netto": False,
    },
}
# Carenza (F16, F35, F37, F39): la quota dei primi 3 giorni che il datore di lavoro paga. Terziario: per numero
# dell'evento nell'anno (CARENZA_PERCENTUALI). Metalmeccanico: intera, ma dal 4° evento di non più di 5 giorni il 66%
# (4°) e il 50% (5° e successivi). Turismo: intera solo se la malattia supera i 5 giorni. Logistica: intera.
CARENZA_METALMECCANICO = {"durata_max": 5, "dal_evento": 4, "quote": (0.66, 0.5)}
CARENZA_TURISMO_DURATA = 5
