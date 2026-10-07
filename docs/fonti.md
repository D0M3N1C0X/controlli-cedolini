# Fonti e verifiche

Ogni regola che i controlli applicano, da dove viene e quanto è stata verificata. Controllato il
**6 ottobre 2026**. Non è consulenza del lavoro.

**Stato**

- **Primaria**: letta nel testo ufficiale.
- **Fonti concordi**: due o più fonti secondarie indipendenti dicono la stessa cosa.
- **Conoscenza generale**: regola nota del sistema paghe, non ricontrollata in questa sessione.
- **Scelta**: una decisione del modello, con il suo motivo.

| # | Regola | Fonte | Stato |
|---|---|---|---|
| F01 | Minimi mensili del CCNL Terziario Confcommercio (paga base + contingenza) per livello, tranche di marzo 2025, novembre 2025, novembre 2026 e febbraio 2027 | Accordo di rinnovo del 22 marzo 2024. Tabelle in [Lexplain](https://www.lexplain.it/tabelle-retributive-ccnl-commercio-2024-2027/) (totali per tranche) e [Leggeinchiaro](https://leggeinchiaro.it/ccnl-commercio-confcommercio-tabelle-retributive/) (paga base e aumenti): gli aumenti di novembre 2026 coincidono livello per livello | Fonti concordi |
| F02 | Al 7° livello il minimo comprende un elemento di 5,16 €: 873,22 + 517,51 + 5,16 = 1.395,89 € | Tabelle di novembre 2025 trovate in ricerca, coerenti con il totale di F01 | Fonti concordi |
| F03 | Scatti: 10 trienni, dal primo giorno del mese successivo al triennio; importi mensili Quadri 25,46 €, 1° 24,84, 2° 22,83, 3° 21,95, 4° 20,66, 5° 20,30, 6° 19,73, 7° 19,47 | [Sintesi Filcams CGIL del CCNL Terziario](https://cgil-agb.it/images/Filcams/pdf/commercio/TERZIARIO_confcommercio.pdf) e [Lexplain](https://www.lexplain.it/scatti-di-anzianita-nel-contratto-commercio-come-cambia-lo-stipendio/): stessi importi | Fonti concordi |
| F04 | Ferie: 26 giorni lavorativi l'anno, per dodicesimi nell'anno di assunzione | Sintesi Filcams CGIL | Fonti concordi |
| F05 | Contributo IVS a carico del dipendente: 9,19% | Aliquota generale del Fondo pensioni lavoratori dipendenti | Conoscenza generale |
| F06 | TFR: quota annua pari alla retribuzione annua divisa per 13,5 | Art. 2120 del Codice civile | Conoscenza generale |
| F07 | Tredicesima e quattordicesima | Sintesi Filcams CGIL | Fonti concordi |
| F08 | Carattere di controllo del codice fiscale | DM 23 dicembre 1976; algoritmo verificato sull'esempio `RSSMRA85T10A562S` | Conoscenza generale |
| F09 | Ritenute su redditi di lavoro dipendente versate in F24 con codice tributo 1001 | Prassi Agenzia delle Entrate | Conoscenza generale |

## Prima di usarlo su dati veri

- **Ricontrollare F01 e F03 sul testo ufficiale dell'accordo** firmato da Confcommercio e dai sindacati:
  qui sono confrontate due fonti secondarie, non il testo firmato.
- **L'aliquota a carico del dipendente va presa dalla posizione INPS del cliente**: il modello non
  considera FIS, CIGS e il contributo aggiuntivo dell'1% sopra la prima fascia pensionabile.
- **L'assorbibilità del superminimo** dipende dalla lettera di assunzione e dagli accordi aziendali.

## Scelte del modello

| # | Scelta | Motivo |
|---|---|---|
| S01 | Tolleranza di un centesimo su ogni importo | Gli arrotondamenti dei software paghe differiscono al centesimo |
| S02 | Soglia del 20% sulla variazione del netto | Da tarare sui primi mesi di uso reale |
| S03 | Rateo TFR mensile = retribuzione ordinaria × 14 / 13,5 / 12 | Accantonamento mensile che include tredicesima e quattordicesima |
| S04 | Scatti valorizzati al livello attuale | Il CCNL non rivaluta gli scatti già maturati con il passaggio di livello: chi ha cambiato livello va controllato a mano |
| S05 | Arrotondamento al centesimo come ROUND di Excel, metà per eccesso | Python e foglio di calcolo devono dare lo stesso risultato |
| S06 | C10 confronta livello, part-time, superminimo e data di assunzione con il mese prima; un cambio senza evento è una segnalazione | Un errore coerente spesso nasce da un cambio di anagrafica: il cedolino torna, ma il dato è cambiato senza motivo |
