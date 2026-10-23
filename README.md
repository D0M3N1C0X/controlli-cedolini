# Controlli cedolini

Quattordici controlli da passare sui cedolini del mese **prima di mandarli al cliente**: minimi e scatti del
CCNL Terziario, contributi, TFR, ferie, quadratura, variazioni anomale, F24, codice fiscale, anagrafica,
ratei di tredicesima e quattordicesima e, per chi lascia, mensilità aggiuntive, ferie non godute e preavviso. In più,
quanto costa a ogni cliente la **tranche CCNL del 1° novembre 2026** e quanto ne assorbono i
superminimi. Gli stessi controlli esistono in Python e in un **foglio di calcolo con formule vive**,
che si apre anche in Google Sheets, per chi elabora le paghe senza scrivere codice.

[![CI](https://github.com/D0M3N1C0X/controlli-cedolini/actions/workflows/ci.yml/badge.svg)](https://github.com/D0M3N1C0X/controlli-cedolini/actions/workflows/ci.yml)
![python](https://img.shields.io/badge/python-3.12%2B-blue)
![ccnl](https://img.shields.io/badge/CCNL-Terziario%20Confcommercio-f2a900)
![license](https://img.shields.io/badge/license-MIT-lightgrey)

> **Dati sintetici, regole reali.** Tre clienti e 122 dipendenti inventati, con errori inseriti apposta;
> minimi (ricostruiti dalla circolare Confcommercio), scatti, ferie e preavviso del CCNL Terziario con le fonti in
> [docs/fonti.md](docs/fonti.md).
> Non è consulenza del lavoro.

> **In English.** Fourteen pre-release checks on Italian payslips under the retail and services collective
> agreement (CCNL Terziario): contractual minimums, seniority steps, social security, severance accrual,
> holiday balances, payslip arithmetic, unexplained swings, tax-payment reconciliation, tax-code validity,
> undeclared master-data changes, 13th/14th-month accruals and, for leavers, 13th/14th-month pay, untaken
> holiday and notice period, plus the cost of the November 2026 pay increase per client. Built three times,
> all giving the same results: in Python, as a live-formula spreadsheet (reconciled on 580 values) and
> as a browser tool where payslip files never leave the computer (checked on 2,219 values). On synthetic data
> it finds all 35 planted errors with no false alarms. Pay tables are rebuilt to the cent from the employers'
> association's official note; every rule has its source in [docs/fonti.md](docs/fonti.md). The rest of the
> repository is in Italian, the language of Italian payroll.

### ▶ [Prova lo strumento nel browser](https://d0m3n1c0x.github.io/controlli-cedolini/strumento/) · [Leggi il rapporto di settembre](https://d0m3n1c0x.github.io/controlli-cedolini/) · [Scarica il foglio di controllo](https://github.com/D0M3N1C0X/controlli-cedolini/raw/main/deliverables/foglio_controllo_cedolini.xlsx)

---

## Cosa trova, sul mese di settembre 2026

| | |
|---|---|
| **35 segnalazioni su 122 cedolini e 3 F24**, 24 ad alta priorità. Ognuna con valore atteso, valore trovato e cosa fare. | **6 dipendenti sotto il minimo:** il tabellare è fermo alla tranche di marzo 2025. Sono 175,44 € al mese, più gli arretrati da novembre 2025. |
| **Un F24 con 212,40 € di ritenute in meno** della somma dei cedolini del cliente. | **Novembre 2026:** 3.765,80 € al mese di aumenti dei minimi per chi resta; i superminimi assorbibili ne coprono 1.385,82 €, restano **2.379,98 € al mese**. |
| **Sei cessazioni a settembre**, tre con un errore: quattordicesima contata da gennaio, ferie non godute a 1/30, licenziamento con metà del preavviso. | |

## I controlli

| Codice | Controllo | Come |
|---|---|---|
| C01 | Minimo tabellare | Paga base, altri elementi e contingenza = minimo del livello × part-time |
| C02 | Scatti di anzianità | Scatti maturati dalla data di assunzione (10 trienni, dal mese successivo) × importo del livello |
| C03 | Contributi INPS | Contributo a carico del dipendente = imponibile arrotondato all'euro × aliquota |
| C04 | Quota TFR | Rateo = retribuzione ordinaria × 14 / 13,5 / 12 |
| C05 | Residuo ferie | Residuo = residuo del mese prima + 26/12 − godute |
| C06 | Quadratura | Lordo = somma delle voci; netto = lordo − trattenute |
| C07 | Variazione del netto | Oltre il 20% sul mese prima senza un evento registrato (assunzione, straordinari, part-time, cessazione) |
| C08 | Riconciliazione F24 | Ritenute (1001) e contributi in delega = somma dei cedolini del cliente |
| C09 | Codice fiscale | Carattere di controllo |
| C10 | Anagrafica | Livello, part-time, superminimo o data di assunzione diversi dal mese prima senza un evento: l'errore coerente che nasce da un cambio |
| C11 | Ratei 13ª e 14ª | Dodicesimi di tredicesima (da gennaio) e quattordicesima (da luglio) diversi dai mesi di servizio: il mese di assunzione conta se ha almeno 15 giorni |
| C12 | Tredicesima e quattordicesima pagate | Retribuzione mensile × dodicesimi maturati / 12: a dicembre i ratei, alla cessazione i mesi fino all'uscita (l'ultimo conta con almeno 15 giorni) |
| C13 | Ferie non godute | Alla cessazione, retribuzione mensile / 26 × giorni di residuo |
| C14 | Preavviso | Giorni di calendario almeno pari al minimo del CCNL per livello, anni di servizio e dimissioni o licenziamento |

Le colonne di C11-C14 sono facoltative: se l'export non le ha, quei controlli non si applicano e gli altri
funzionano lo stesso. Un cedolino di uscita senza le sue voci, però, non quadra in C06: il lordo comprende
importi che il file non riporta.

I controlli **ricalcolano ogni voce dalle regole del contratto**, o la confrontano con il mese prima e con
l'F24: non serve sapere come l'ha calcolata il software paghe.

## Quanto ci si può fidare

- **Sugli errori inseriti:** 35 trovati su 35, nessun falso allarme, e nessuna segnalazione sui casi
  legittimi (assunzioni del mese, straordinari dichiarati, passaggio a part-time, cessazioni corrette). Dimostra che i
  controlli fanno quello che dicono, non che troverebbero errori reali: gli errori li ho scelti io.
- **Su 1.100 alterazioni casuali:** una voce qualsiasi di un cedolino corretto, cambiata di un importo
  a caso. Sopra il centesimo di tolleranza le trovano tutte.
- **Regole contro statistica:** un rilevatore di anomalie che non conosce il contratto trova 11 cedolini sbagliati
  su 34, con 7 falsi allarmi; le regole 34 su 34, con nessuno. Vede solo gli errori che spostano un rapporto
  (contributi, TFR, variazione del netto), non minimi, scatti, anagrafica o ratei. I cedolini di uscita li
  segnala tutti, giusti o sbagliati, perché il netto salta.
- **Il limite, ristretto da C10:** un errore *coerente* passa i controlli aritmetici. Un dipendente di
  4° livello inserito al 5°, con il cedolino ricalcolato da capo, torna in ogni voce e prende 61,29 €
  netti in meno al mese. Se l'errore nasce da un cambio rispetto al mese prima lo trova C10; resta
  invisibile solo se è sbagliato fin dall'assunzione, e lì serve il confronto con i documenti del
  cliente. Il test `test_limite_dichiarato_errore_coerente` tiene vero il limite.
- **Tre motori, una risposta:** il foglio di calcolo è confrontato con Python su 580 valori e ricalcolato
  con LibreOffice nella CI; lo strumento nel browser è confrontato con Python su 2.219 valori. La verifica del
  foglio usa [excel-twin](https://github.com/D0M3N1C0X/excel-twin), una piccola libreria condivisa dal portfolio.

## Cosa c'è

| File | Per chi | Cosa contiene |
|---|---|---|
| [`foglio_controllo_cedolini.xlsx`](deliverables/foglio_controllo_cedolini.xlsx) | chi elabora le paghe | Si incollano i cedolini del mese e del mese prima (fino a 250 righe, formule già pronte) e gli F24: esiti OK/ERRORE riga per riga, riepilogo per cliente, tranche di novembre, parametri modificabili, riconciliazione con Python. |
| [Rapporto](report/rapporto.md) | il responsabile del team | Le segnalazioni con cosa fare, l'F24, la tranche di novembre, quanto ci si può fidare dei controlli. |
| [`anomalie.csv`](report/anomalie.csv) | un altro strumento | Le segnalazioni in formato tabellare, da caricare in un ticket o in un CRM. |
| [`docs/fonti.md`](docs/fonti.md) | chi verifica | Fonte e stato di ogni regola, le correzioni fatte e cosa ricontrollare prima di usarlo su dati veri. |
| [`docs/catalogo-controlli.md`](docs/catalogo-controlli.md) | chi usa i controlli | Una scheda per controllo: regola, fonte, formula del foglio, esempio vero, cause tipiche, cosa fare, limiti. |
| [`docs/guida-operativa.md`](docs/guida-operativa.md) | il team paghe | La procedura del mese: chi fa cosa, smistamento delle segnalazioni, criteri di rilascio, registro. |
| [`docs/architettura.md`](docs/architettura.md) | chi mantiene il codice | Come restano uguali Python, foglio e browser; come si aggiunge un controllo o si aggiorna il contratto. |
| [`docs/roadmap.md`](docs/roadmap.md) · [`CHANGELOG.md`](CHANGELOG.md) | chi decide | Cosa viene dopo e perché; cosa è cambiato a ogni versione. |
| [`docs/decisioni.md`](docs/decisioni.md) | chi verifica il metodo | Ogni scelta di metodo, con l'alternativa che ha sostituito e il perché. |
| [`docs/dizionario-dati.md`](docs/dizionario-dati.md) | chi usa i dati | Ogni colonna, livello, evento e tipo di errore; un test lo tiene completo. |

## Usare lo strumento nel browser

[Apri lo strumento](https://d0m3n1c0x.github.io/controlli-cedolini/strumento/) e trascina i file così come escono dal
software paghe: i cedolini del mese, se vuoi quelli del mese prima e le deleghe F24, in **Excel (.xlsx) o CSV**.

- **Le colonne si abbinano da sole** quando hanno nomi comuni ("Codice dipendente", "Totale competenze", "Residuo
  ferie"...); se manca qualcosa, lo strumento chiede quale colonna usare e ricorda la scelta su quel computer.
- **L'esito si scarica in Excel**, con le colonne per chi corregge e quando, e si stampa per il cliente.
- **In italiano e in inglese**, con un interruttore in alto.
- **I file non lasciano il computer**: i controlli girano nella pagina, che non carica script esterni. I file Excel
  si aprono senza librerie, con la decompressione che il browser ha già. Il rapporto online conta le visite con
  GoatCounter, senza cookie; lo strumento no.

Con "Prova con i dati di esempio" si vede subito il risultato.

Il JavaScript dello strumento è verificato contro Python a ogni modifica: 2.219 confronti su nove casi e sui casi limite di ratei e cessazioni, comprese le
alterazioni di mezzo centesimo e il formato italiano.

## Usare il foglio, senza Python

1. Apri [`foglio_controllo_cedolini.xlsx`](deliverables/foglio_controllo_cedolini.xlsx) in Excel o LibreOffice, oppure importalo in Google Sheets.
2. Nel foglio **Parametri** imposta il mese e l'aliquota INPS del cliente.
3. Incolla i cedolini del mese nel foglio **Mese** (colonne A-W; i ratei in AU-AV e le voci di chi lascia in AZ-BE, se ci sono; fino a 250 righe) e quelli del mese prima in **Mese precedente**; gli importi delle deleghe vanno nel foglio **F24**.
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
ruff check .                 # lo stesso controllo dello stile della CI; regole in pyproject.toml
```

Ogni funzione in `src/` dichiara cosa restituisce; la CI controlla lo stile e misura la copertura dei test.

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
│   ├── controlli.py         i quattordici controlli, la tranche di novembre, la valutazione
│   ├── robustezza.py        alterazioni casuali e l'errore coerente
│   ├── statistica.py        regole contro un rilevatore statistico
│   ├── build_foglio.py      il foglio di calcolo con le formule
│   ├── build_rapporto.py    il rapporto
│   ├── build_catalogo.py    il catalogo dei controlli, dalle regole e dal foglio
│   ├── genera.py            i dati sintetici
│   └── run_all.py           tutto in un comando
├── deliverables/            il foglio di calcolo
├── report/                  rapporto, pagina HTML, segnalazioni
├── docs/
│   ├── catalogo-controlli.md una scheda per controllo, generata dal codice
│   ├── guida-operativa.md   la procedura del mese per il team paghe
│   ├── architettura.md      come restano uguali le tre versioni
│   ├── roadmap.md           cosa viene dopo
│   ├── fonti.md             fonte e stato di ogni regola, correzioni
│   ├── decisioni.md         le scelte di metodo e le alternative scartate
│   └── dizionario-dati.md   ogni colonna dei dati
└── tests/
```

## Limiti

- **Contributi semplificati:** un'aliquota del 9,19% per tutti; FIS, CIGS e contributo aggiuntivo
  dell'1% non sono modellati. In uso reale l'aliquota viene dalla posizione INPS del cliente.
- **Un CCNL, un mese senza assenze:** malattia, aspettativa, conguagli e l'indennità sostitutiva del
  preavviso non sono controllati; delle cessazioni si controllano mensilità aggiuntive, ferie non godute e
  giorni di preavviso, non il TFR liquidato. L'IRPEF dei dati sintetici non è calcolata con le regole fiscali: serve solo all'F24.
- **Fonti:** i minimi sono ricostruiti dalla circolare Confcommercio del 29 marzo 2024; gli importi degli scatti
  vengono da due fonti secondarie concordi e vanno ricontrollati sul testo del CCNL prima dell'uso.

## Autore

**Domenico Perroni** — HR advisory, people analytics e media education, a Cracovia.
[Profilo GitHub](https://github.com/D0M3N1C0X) · [LinkedIn](https://www.linkedin.com/in/domenico-perroni)

**Altri progetti collegati**

- [workforce-cost-model](https://github.com/D0M3N1C0X/workforce-cost-model) — il costo del personale in Italia e Polonia, con INPS, TFR e ZUS: budget, scostamenti e scenari in Excel riconciliato con pandas
- [pay-transparency-readiness-kit](https://github.com/D0M3N1C0X/pay-transparency-readiness-kit) — la direttiva UE sulla trasparenza retributiva applicata a un datore di lavoro in quattro paesi
- [equal-value-pay-ranges](https://github.com/D0M3N1C0X/equal-value-pay-ranges) — fasce retributive di pari valore per grado e paese, su dati Eurostat
- [job-search-agent](https://github.com/D0M3N1C0X/job-search-agent) — la mia ricerca di lavoro automatizzata: annunci dalle API dei sistemi di selezione, punteggio deterministico, zero dipendenze

Licenza MIT.
