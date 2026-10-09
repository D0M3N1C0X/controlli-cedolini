# Fonti e verifiche

Ogni regola che i controlli applicano, da dove viene e quanto è stata verificata. Controllato il
**6 ottobre 2026**, minimi e contributi ricontrollati sulle fonti primarie il **9 ottobre 2026**. Non è consulenza del lavoro.

**Stato**

- **Primaria**: letta nel testo ufficiale, o nel documento di una parte firmataria o dell'ente che fissa la regola.
- **Fonti concordi**: due o più fonti secondarie indipendenti dicono la stessa cosa.
- **Conoscenza generale**: regola nota del sistema paghe, non ricontrollata in questa sessione.
- **Scelta**: una decisione del modello, con il suo motivo.

| # | Regola | Fonte | Stato |
|---|---|---|---|
| F01 | Minimi mensili del CCNL Terziario Confcommercio per livello (paga base + altri elementi + contingenza ed EDR), tranche di marzo 2025, novembre 2025, novembre 2026 e febbraio 2027 | [Confcommercio, circolare n. 16 del 29 marzo 2024](https://www.dottrinalavoro.it/wp-content/uploads/2024/04/Confcommercio-chiarimenti-operativi-Rinnovo-del-CCNL-e-Accordo-Integrativo-del-28-marzo-2024.pdf), chiarimenti operativi sul rinnovo del 22 marzo 2024 e sull'accordo integrativo del 28 marzo 2024: tabella "Paga base dal 1/3/2025" (p. 8) più gli aumenti per tranche dell'art. 213 (p. 7). I valori di `data/ccnl_terziario.csv` sono ricostruiti così, al centesimo | Primaria (parte firmataria) |
| F02 | "Altri elementi" compresi nel minimo: 260,76 € per i Quadri, 5,16 € al 7° livello; nessuno negli altri livelli | Stessa circolare, colonna "Altri el." delle tabelle di p. 8 | Primaria (parte firmataria) |
| F03 | Scatti: 10 trienni, dal primo giorno del mese successivo al triennio; importi mensili Quadri 25,46 €, 1° 24,84, 2° 22,83, 3° 21,95, 4° 20,66, 5° 20,30, 6° 19,73, 7° 19,47 | [Sintesi Filcams CGIL del CCNL Terziario](https://cgil-agb.it/images/Filcams/pdf/commercio/TERZIARIO_confcommercio.pdf) e [Lexplain](https://www.lexplain.it/scatti-di-anzianita-nel-contratto-commercio-come-cambia-lo-stipendio/): stessi importi | Fonti concordi |
| F04 | Ferie: 26 giorni lavorativi l'anno, per dodicesimi nell'anno di assunzione | Sintesi Filcams CGIL | Fonti concordi |
| F05 | Contributo IVS a carico del dipendente: 9,19% | Aliquota generale del Fondo pensioni lavoratori dipendenti | Conoscenza generale |
| F06 | TFR: quota annua pari alla retribuzione annua divisa per 13,5 | Art. 2120 del Codice civile | Conoscenza generale |
| F07 | Tredicesima e quattordicesima | Sintesi Filcams CGIL | Fonti concordi |
| F08 | Carattere di controllo del codice fiscale | DM 23 dicembre 1976; algoritmo verificato sull'esempio `RSSMRA85T10A562S` | Conoscenza generale |
| F09 | Ritenute su redditi di lavoro dipendente versate in F24 con codice tributo 1001 | Prassi Agenzia delle Entrate | Conoscenza generale |
| F10 | L'imponibile contributivo si espone in unità di euro e il contributo si arrotonda al centesimo (millesimi da 5 a 9 per eccesso): l'aliquota si applica all'imponibile arrotondato all'euro, 1.779,00 × 9,19% = 163,49 € | [INPS, Documento tecnico UniEmens individuale, versione 4.33 del 29/09/2026](https://www.inps.it/content/dam/inps-site/pdf/prestazioni-e-servizi/uniemens-aziende-private/UniEMENSind.pdf): importi interi e contributivi (p. 31), elemento `<Imponibile>` di `<DatiRetributivi>` (p. 52). Esempio di calcolo: [ODCEC Torino, "Conosci la tua busta paga?"](https://odcec.torino.it/public/pagine/slides.pdf), p. 24 | Primaria per il formato; il calcolo sull'imponibile arrotondato è prassi, confermata dall'esempio |

## Prima di usarlo su dati veri

- **Ricontrollare F03 (scatti) sul testo del CCNL**: gli importi vengono da due fonti secondarie concordi.
  I minimi (F01, F02) sono invece ricostruiti al centesimo dalla circolare Confcommercio del 29 marzo 2024.
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

## Correzioni

- **9 ottobre 2026, minimi.** Il confronto con la circolare Confcommercio n. 16/2024 ha trovato tre differenze
  rispetto alle fonti secondarie usate prima: ai Quadri mancavano gli "altri elementi" di 260,76 € al mese;
  contingenza ed EDR di Quadri, 1° e 2° livello erano sbagliate di 1-2 centesimi; il 6° livello di febbraio 2027
  di un centesimo. Tabella ricostruita dalla fonte primaria, dati e risultati rigenerati.
- **9 ottobre 2026, contributi.** C03 applicava l'aliquota al lordo al centesimo; ora all'imponibile arrotondato
  all'euro (F10). Su cedolini veri la versione precedente avrebbe dato falsi allarmi di pochi centesimi.

