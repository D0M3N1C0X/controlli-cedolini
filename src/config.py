"""
Tutti i parametri dei controlli, in un solo posto e con la loro fonte. Il foglio Parametri del
file Excel è scritto da qui: Python e foglio partono dagli stessi numeri.
"""
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CCNL = DATA / "ccnl_terziario.csv"
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

# Clienti sintetici, tutti con il CCNL Terziario Distribuzione e Servizi (Confcommercio).
CLIENTI = {
    "A": {"nome": "Cliente A · negozio al dettaglio", "dipendenti": 18},
    "B": {"nome": "Cliente B · commercio all'ingrosso", "dipendenti": 74},
    "C": {"nome": "Cliente C · servizi alle imprese", "dipendenti": 27},
}

# ---- Regole usate dai controlli ---------------------------------------------------------------
# Minimi: CCNL Terziario, tranche dal 1° novembre 2025 (vedi docs/fonti.md, F01).
COLONNA_MINIMO = "minimo_2025_11"
COLONNA_MINIMO_PROSSIMO = "minimo_2026_11"
# Scatti: uno ogni triennio, fino a 10, dal primo giorno del mese successivo al triennio (F03).
SCATTI_MAX = 10
SCATTI_ANNI = 3
# Contributo IVS a carico del dipendente. Semplificato: lo stesso per tutti i clienti, senza FIS,
# CIGS né il contributo aggiuntivo dell'1% sopra la prima fascia pensionabile (F05).
ALIQUOTA_DIPENDENTE = 0.0919
# TFR: quota annua = retribuzione annua / 13,5 (art. 2120 c.c.). Rateo mensile sulla retribuzione
# ordinaria per 14 mensilità, diviso 12 (F06).
DIVISORE_TFR = 13.5
MENSILITA = 14
# Ferie: 26 giorni lavorativi l'anno, maturati per dodicesimi (F04).
FERIE_ANNUE = 26
# Variazione del netto rispetto al mese prima oltre la quale serve una spiegazione.
SOGLIA_VARIAZIONE = 0.20
TOLLERANZA = 0.01                # euro: un centesimo di arrotondamento
TOLLERANZA_FERIE = 0.01          # giorni
