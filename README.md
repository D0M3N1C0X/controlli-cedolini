# Controlli cedolini

Dieci controlli da passare sui cedolini del mese **prima di mandarli al cliente**: minimi e scatti del
CCNL Terziario, contributi, TFR, ferie, quadratura, variazioni anomale, F24 e codice fiscale. In più,
quanto costa a ogni cliente la **tranche CCNL del 1° novembre 2026** e quanto ne assorbono i
superminimi. Gli stessi controlli esistono in Python e in un **foglio di calcolo con formule vive**,
che si apre anche in Google Sheets, per chi elabora le paghe senza scrivere codice.

[![CI](https://github.com/D0M3N1C0X/controlli-cedolini/actions/workflows/ci.yml/badge.svg)](https://github.com/D0M3N1C0X/controlli-cedolini/actions/workflows/ci.yml)
![python](https://img.shields.io/badge/python-3.12%2B-blue)
![ccnl](https://img.shields.io/badge/CCNL-Terziario%20Confcommercio-f2a900)
![license](https://img.shields.io/badge/license-MIT-lightgrey)

> **Dati sintetici, regole reali.** Tre clienti e 122 dipendenti inventati, con errori inseriti apposta;
> minimi, scatti e ferie del CCNL Terziario Confcommercio con le fonti in [docs/fonti.md](docs/fonti.md).
> Non è consulenza del lavoro.

### ▶ [Prova lo strumento nel browser](https://d0m3n1c0x.github.io/controlli-cedolini/strumento/) · [Leggi il rapporto di settembre](https://d0m3n1c0x.github.io/controlli-cedolini/) · [Scarica il foglio di controllo](https://github.com/D0M3N1C0X/controlli-cedolini/raw/main/deliverables/foglio_controllo_cedolini.xlsx)

---

## Cosa trova, sul mese di settembre 2026

| | |
|---|---|
| **29 segnalazioni su 122 cedolini e 3 F24**, 21 ad alta priorità. Ognuna con valore atteso, valore trovato e cosa fare. | **6 dipendenti sotto il minimo:** il tabellare è fermo alla tranche di marzo 2025. Sono 175,44 € al mese, più gli arretrati da novembre 2025. |
| **Un F24 con 212,40 € di ritenute in meno** della somma dei cedolini del cliente. | **Novembre 2026:** 3.927,52 € al mese di aumenti dei minimi; i superminimi assorbibili ne coprono 1.478,70 €, restano **2.448,82 € al mese**. |

## I controlli

| Codice | Controllo | Come |
|---|---|---|
| C01 | Minimo tabellare | Paga base + contingenza = minimo del livello × part-time |
| C02 | Scatti di anzianità | Scatti maturati dalla data di assunzione (10 trienni, dal mese successivo) × importo del livello |
| C03 | Contributi INPS | Contributo a carico del dipendente = imponibile × aliquota |
| C04 | Quota TFR | Rateo = retribuzione ordinaria × 14 / 13,5 / 12 |
| C05 | Residuo ferie | Residuo = residuo del mese prima + 26/12 − godute |
| C06 | Quadratura | Lordo = somma delle voci; netto = lordo − trattenute |
| C07 | Variazione del netto | Oltre il 20% sul mese prima senza un evento registrato (assunzione, straordinari, part-time) |
| C08 | Riconciliazione F24 | Ritenute (1001) e contributi in delega = somma dei cedolini del cliente |
| C09 | Codice fiscale | Carattere di controllo |
| C10 | Anagrafica | Livello, part-time, superminimo o data di assunzione diversi dal mese prima senza un evento: l'errore coerente che nasce da un cambio |

I controlli **ricalcolano ogni voce dalle regole del contratto**, o la confrontano con il mese prima e con
l'F24: non serve sapere come l'ha calcolata il software paghe.

## Quanto ci si può fidare

- **Sugli errori inseriti:** 29 trovati su 29, nessun falso allarme, e nessuna segnalazione sui casi
  legittimi (assunzioni del mese, straordinari dichiarati, passaggio a part-time). Dimostra che i
  controlli fanno quello che dicono, non che troverebbero errori reali: gli errori li ho scelti io.
- **Su 1.100 alterazioni casuali:** una voce qualsiasi di un cedolino corretto, cambiata di un importo
  a caso. Sopra il centesimo di tolleranza le trovano tutte.
- **Regole contro statistica:** un rilevatore di anomalie che non conosce il contratto trova 9 cedolini sbagliati
  su 28, con 8 falsi allarmi; le regole 28 su 28, con nessuno. Vede solo gli errori che spostano un rapporto
  (contributi, TFR, variazione del netto), non minimi, scatti o anagrafica.
- **Il limite, ristretto da C10:** un errore *coerente* passa i controlli aritmetici. Un dipendente di
  4° livello inserito al 5°, con il cedolino ricalcolato da capo, torna in ogni voce e prende 61,27 €
  netti in meno al mese. Se l'errore nasce da un cambio rispetto al mese prima lo trova C10; resta
  invisibile solo se è sbagliato fin dall'assunzione, e lì serve il confronto con i documenti del
  cliente. Il test `test_limite_dichiarato_errore_coerente` tiene vero il limite.
- **Tre motori, una risposta:** il foglio di calcolo è confrontato con Python su 435 valori e ricalcolato
  con LibreOffice nella CI; lo strumento nel browser è confrontato con Python su 1.807 valori.

## Cosa c'è

| File | Per chi | Cosa contiene |
|---|---|---|
| [`foglio_controllo_cedolini.xlsx`](deliverables/foglio_controllo_cedolini.xlsx) | chi elabora le paghe | Si incollano i cedolini del mese e del mese prima (fino a 250 righe, formule già pronte) e gli F24: esiti OK/ERRORE riga per riga, riepilogo per cliente, tranche di novembre, parametri modificabili, riconciliazione con Python. |
| [Rapporto](report/rapporto.md) | il responsabile del team | Le segnalazioni con cosa fare, l'F24, la tranche di novembre, quanto ci si può fidare dei controlli. |
| [`anomalie.csv`](report/anomalie.csv) | un altro strumento | Le segnalazioni in formato tabellare, da caricare in un ticket o in un CRM. |
| [`docs/fonti.md`](docs/fonti.md) | chi verifica | Fonte e stato di ogni regola, e cosa ricontrollare prima di usarlo su dati veri. |

## Usare lo strumento nel browser

[Apri lo strumento](https://d0m3n1c0x.github.io/controlli-cedolini/strumento/), carica il CSV dei cedolini (mese da
controllare e mese prima) e, se vuoi, quello degli F24. I controlli girano nella pagina: **i file non lasciano il
computer**. Accetta l'esportazione di Excel in italiano (punto e virgola, virgola decimale, date gg/mm/aaaa); i
modelli delle colonne sono nella pagina. Con "Usa i dati di esempio" si vede subito il risultato.

Il JavaScript dello strumento è verificato contro Python a ogni modifica: 1.807 confronti su nove casi, comprese le
alterazioni di mezzo centesimo e il formato italiano.

## Usare il foglio, senza Python

1. Apri [`foglio_controllo_cedolini.xlsx`](deliverables/foglio_controllo_cedolini.xlsx) in Excel o LibreOffice, oppure importalo in Google Sheets.
2. Nel foglio **Parametri** imposta il mese e l'aliquota INPS del cliente.
3. Incolla i cedolini del mese nel foglio **Mese** (colonne A-W, fino a 250 righe) e quelli del mese prima in **Mese precedente**; gli importi delle deleghe vanno nel foglio **F24**.
4. Leggi il **Riepilogo**, poi filtra il foglio Mese sulla colonna *Errori*. Il foglio **Novembre 2026** si aggiorna da solo.

I dati di esempio già presenti si possono cancellare: le formule restano.

## Usare lo script

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python src/run_all.py        # circa 25 secondi
```

Test, compreso il foglio calcolato in Python e confrontato con pandas:

```bash
pip install -r requirements-dev.txt
pytest
```

## Struttura

```
├── data/
│   ├── ccnl_terziario.csv   minimi per tranche e scatti, con fonte
│   ├── cedolini.csv         agosto e settembre 2026, sintetici
│   ├── f24.csv              deleghe di settembre per cliente
│   └── errori_inseriti.csv  cosa è stato sbagliato apposta, per misurare i controlli
├── src/
│   ├── config.py            parametri e soglie
│   ├── regole.py            le regole del contratto, scritte una volta
│   ├── controlli.py         i dieci controlli, la tranche di novembre, la valutazione
│   ├── robustezza.py        alterazioni casuali e l'errore coerente
│   ├── statistica.py        regole contro un rilevatore statistico
│   ├── build_foglio.py      il foglio di calcolo con le formule
│   ├── build_rapporto.py    il rapporto
│   ├── genera.py            i dati sintetici
│   └── run_all.py           tutto in un comando
├── deliverables/            il foglio di calcolo
├── report/                  rapporto, pagina HTML, segnalazioni
├── docs/fonti.md
└── tests/
```

## Limiti

- **Contributi semplificati:** un'aliquota del 9,19% per tutti; FIS, CIGS e contributo aggiuntivo
  dell'1% non sono modellati. In uso reale l'aliquota viene dalla posizione INPS del cliente.
- **Un CCNL, un mese ordinario:** tredicesima, quattordicesima, malattia, cessazioni e conguagli non sono
  controllati. L'IRPEF dei dati sintetici non è calcolata con le regole fiscali: serve solo all'F24.
- **Fonti secondarie concordi** per minimi e scatti: prima dell'uso vanno ricontrollati sul testo firmato.

## In English

Ten pre-release checks on Italian payslips under the retail and services collective agreement
(CCNL Terziario): contractual minimums, seniority steps, social security, severance accrual, holiday
balances, payslip arithmetic, unexplained swings, tax-payment reconciliation, tax-code validity and
undeclared master-data changes, plus the cost of the November 2026 pay increase per client. Built three
times, all giving the same results: in Python, as a live-formula spreadsheet (reconciled on 435 values)
and as a browser tool where payslip files never leave the computer (checked on 1,807 values).

## Autore

**Domenico Perroni** — HR advisory, people analytics e media education, a Cracovia.
[Profilo GitHub](https://github.com/D0M3N1C0X) · [LinkedIn](https://www.linkedin.com/in/domenico-perroni)

**Altri progetti collegati**

- [workforce-cost-model](https://github.com/D0M3N1C0X/workforce-cost-model) — il costo del personale in Italia e Polonia, con INPS, TFR e ZUS: budget, scostamenti e scenari in Excel riconciliato con pandas
- [pay-transparency-readiness-kit](https://github.com/D0M3N1C0X/pay-transparency-readiness-kit) — la direttiva UE sulla trasparenza retributiva applicata a un datore di lavoro in quattro paesi
- [equal-value-pay-ranges](https://github.com/D0M3N1C0X/equal-value-pay-ranges) — fasce retributive di pari valore per grado e paese, su dati Eurostat
- [job-search-agent](https://github.com/D0M3N1C0X/job-search-agent) — la mia ricerca di lavoro automatizzata: annunci dalle API dei sistemi di selezione, punteggio deterministico, zero dipendenze

Licenza MIT.
