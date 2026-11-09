# Changelog

Cosa cambia a ogni versione, per chi usa i controlli. Formato [Keep a Changelog](https://keepachangelog.com/it-IT/1.1.0/).
Le cose che vengono dopo sono in [docs/roadmap.md](docs/roadmap.md).

## [Non rilasciato]

## [2.2.0] - 2026-11-09

### Aggiunto

- **Tre CCNL in più, uno per cliente:** Metalmeccanico industria (Federmeccanica-Assistal, cliente D), Turismo,
  pubblici esercizi (Fipe, cliente E), Logistica, trasporto merci e spedizione (Confetra, cliente F), con le tabelle
  dei minimi e le regole lette nei testi delle parti firmatarie e all'archivio CNEL (F30-F40). Per ciascuno: minimi,
  scatti (periodo e numero), mensilità, regola della frazione di mese per i ratei, quattordicesima senza scatti nel
  Turismo, ferie, permessi, preavviso, quota giornaliera, indennità INPS di malattia e carenza.
- **C22 Integrazione del datore di lavoro:** nel mese di malattia o maternità, sul netto nel Terziario (il netto non
  sta sotto la quota garantita del netto normale, con contributi e IRPEF di C03 e C20) e nella maternità del Turismo;
  sul lordo nel Metalmeccanico e nella Logistica (D33).
- Diciotto errori inseriti nei clienti nuovi, quasi tutti regole di un altro contratto applicate per sbaglio, e uno
  nel Terziario (integrazione non pagata). Trovati 67 su 67, senza falsi allarmi.
- Foglio: tabella unica dei quattro CCNL con chiave `ccnl|livello`, una riga di regole per CCNL, il CCNL di ogni
  cliente nei Parametri; colonne DS-EC; 1.682 valori riconciliati (erano 983). Strumento nel browser: la scelta del
  CCNL per i file dell'utente e le stesse regole, verificate su 3.909 valori (erano 2.898).

### Cambiato

- **Il mese di un'assenza è un cedolino vero:** la retribuzione dei giorni assenti si toglie in giorni di calendario;
  indennità INPS, carenza e integrazione entrano nel lordo; l'imponibile contributivo esclude le indennità INPS (F41,
  D31). Prima le indennità erano voci a parte sopra la retribuzione piena (D22, superata).
- La carenza si paga sulla stessa misura giornaliera della retribuzione tolta (mensile / giorni del mese).
- Un'impresa industriale non versa al FIS (F31): l'aliquota del cliente D è IVS più CIGS.
- La tranche di novembre 2026 riguarda solo i clienti del Terziario; gli altri CCNL hanno la prossima nel 2027.

### Corretto

- **Strumento nel browser:** la pagina non aveva i campi delle colonne IRPEF della v2.1 (somma del cuneo, trattamento
  integrativo, dati del conguaglio), e le scartava leggendo il file: C20 e C21 tacevano, e il netto atteso di C06 non
  sommava il cuneo. I campi ci sono, con quelli nuovi della v2.2, e un test verifica che ogni colonna di
  `cedolini.csv` abbia il suo campo. Il controllo del JavaScript non lo vedeva perché passa i dati senza la pagina.

## [2.1.0] - 2026-11-08

### Aggiunto

- **C20 IRPEF del mese:** le regole 2026 lette nei testi ufficiali su Normattiva. Scaglioni del 23%, 33% (L. 199/2025,
  prima 35%) e 43% ragguagliati al mese, detrazione per lavoro dipendente (art. 13 TUIR), ulteriore detrazione e somma
  del cuneo fiscale (L. 207/2024), trattamento integrativo (D.L. 3/2020) (F24-F28).
- **C21 Conguaglio IRPEF alla cessazione:** imposta dell'anno sull'imponibile da gennaio, detrazioni e trattamento
  integrativo rapportati ai giorni di lavoro, meno quanto trattenuto o erogato nei mesi prima (F29).
- Colonne `bonus_cuneo` e `trattamento_integrativo` in ogni cedolino; per chi esce, imponibile fiscale dell'anno,
  giorni di lavoro e somme dei mesi prima. Il netto somma le due voci del cuneo.
- Cinque errori inseriti: tabella del 2025, ulteriore detrazione non applicata, somma del cuneo non erogata, due
  conguagli sbagliati. Trovati 49 su 49, senza falsi allarmi.
- Foglio: parametri IRPEF con la fonte, colonne CY-DR, 983 valori riconciliati (erano 737). Strumento nel browser: le
  stesse regole in JavaScript, verificate su 2.898 valori (erano 2.593).

### Cambiato

- L'IRPEF dei dati di esempio è calcolata con le regole, non più sintetica (D26). Le scelte S08-S11 dicono come il mese
  stima il reddito dell'anno e ripartisce le detrazioni.
- L'integrazione aziendale di malattia e maternità sul netto resta fuori (D21, aggiornata): servono cedolini che
  riducano la retribuzione dei giorni di assenza, previsti con i prossimi CCNL.

## [2.0.0] - 2026-11-06

### Aggiunto

- **C15 Indennità di malattia INPS:** 50% dal 4° al 20° giorno e 66,66% dal 21° al 180°, sulla retribuzione del mese
  prima × 14/12 / 30 (INPS, circ. 94/2009). **C16 Carenza:** integrazione dei primi 3 giorni per numero dell'evento
  nell'anno, con le esenzioni del CCNL. **C17 Indennità di maternità INPS:** 80% della stessa base.
- **C18 Permessi:** riduzione d'orario (72 o 56 ore) ed ex festività (32 ore) per dodicesimi, in proporzione al
  part-time, con la regola dei 2 e 4 anni per chi è entrato dopo il 1° marzo 2011.
- **C19 TFR liquidato:** fondo al 31 dicembre rivalutato con l'indice ISTAT FOI (coefficiente ricostruito al sesto
  decimale, il mese conta dal 15), imposta sostitutiva del 17%, quote dell'anno meno lo 0,50%.
- Nel foglio: la tabella **Clienti** con la posizione INPS di ciascuno, gli indici FOI, le colonne BQ-CX; nel
  browser: i dipendenti medi del semestre e quelli in forza al posto dell'aliquota.
- 44 errori inseriti (erano 35), tutti trovati, nessun falso allarme; 737 valori riconciliati nel foglio, 2.593 nel
  browser.

### Cambiato

- **C03 Contributi INPS** usa l'aliquota della posizione: IVS 9,19%, CIGS 0,30% oltre 15 dipendenti di media nel
  semestre, un terzo del FIS, più l'1% oltre la prima fascia pensionabile (4.685 € al mese nel 2026). L'aliquota
  unica del 9,19% sottostimava i contributi di quasi tutti i dipendenti di esempio, e l'errore inserito prima
  (9,49%) era più vicino al vero del valore corretto.
- Il rilevatore statistico confronta ogni cedolino con quelli dello stesso cliente (D23).

### Corretto

- Le fonti del CCNL: la sintesi Filcams usata finora è del rinnovo 2011-2013. Ora è dichiarato in `docs/fonti.md`,
  con gli articoli cambiati dal rinnovo 2024 secondo la circolare Confcommercio n. 16/2024.

## [1.3.1] - 2026-10-23

### Corretto

- **Foglio:** il livello si cerca come testo, così un livello incollato come numero non spegne più C01, C02 e C14;
  un livello che non è nel CCNL è un ERRORE di C01, come in Python.
- **C11 e C12** contano allo stesso modo i dodicesimi di chi lascia prima del 15 (D20); **C12** non segnala più la
  quattordicesima pagata a luglio (D19). Le indicazioni su cosa fare dicono se pagare o recuperare, e per il
  preavviso distinguono dimissioni e licenziamento.
- **Strumento nel browser:** i decimali si riconoscono dai numeri, non dal separatore del CSV; matricole lette
  come numero e come testo coincidono; part-time in percentuale ("100", "50%"); mesi scritti come 01/09/2026,
  202609 o «settembre 2026»; date impossibili rifiutate; un avviso per le righe con il mese illeggibile.
- Un'uscita corretta a metà mese nei dati di esempio: 580 valori riconciliati nel foglio, 2.219 nel browser.

## [1.3.0] - 2026-10-23

### Aggiunto

- **C12, tredicesima e quattordicesima pagate**: retribuzione mensile per i dodicesimi maturati, a dicembre dai ratei
  e alla cessazione fino alla data di uscita (fonte F11).
- **C13, ferie non godute**: alla cessazione, 1/26 della retribuzione mensile per giorno di residuo (fonte F12).
- **C14, preavviso**: giorni di calendario almeno pari al minimo del CCNL per livello, anni di servizio e tipo di
  recesso (fonte F13).
- Sei colonne facoltative per chi lascia, nello script, nel foglio (AZ-BE) e nello strumento nel browser, che le
  abbina da sole quando hanno nomi comuni. Cinque cessazioni nei dati di esempio, tre con un errore inserito.
- Strumento nel browser: file Excel (.xlsx) oltre ai CSV, abbinamento guidato delle colonne, esito scaricabile in
  Excel e stampabile, italiano e inglese.
- [Catalogo dei controlli](docs/catalogo-controlli.md): una scheda per controllo, generata da codice, foglio e
  segnalazioni, con un test che lo tiene aggiornato.
- [Guida operativa](docs/guida-operativa.md): la procedura mensile del team paghe, con ruoli e criteri di rilascio.
- [Architettura](docs/architettura.md): come restano uguali le tre versioni, come si aggiunge un controllo.
- Il rapporto online conta le visite con GoatCounter, senza cookie; lo strumento nel browser no.

### Cambiato

- La descrizione di C01 nomina anche gli altri elementi del minimo.
- La tranche di novembre esclude chi lascia prima del 1° novembre: nello script, nel foglio e nel browser.
- Il confronto con il rilevatore statistico dice che segnala tutti i cedolini di uscita, giusti o sbagliati.

## [1.2.0] - 2026-10-12

### Aggiunto

- **C11, ratei di tredicesima e quattordicesima**: dodicesimi da gennaio e da luglio, il mese di assunzione intero
  se ha almeno 15 giorni (fonte F11). Colonne facoltative.

### Corretto

- I file modello dello strumento nel browser riportavano i contributi di prima della correzione INPS: ora sono
  generati dai dati.

## [1.1.0] - 2026-10-09

### Corretto

- **Minimi ricostruiti dalla circolare Confcommercio** del 29 marzo 2024: ai Quadri mancavano 260,76 € di altri
  elementi; contingenza di Quadri, 1° e 2° livello sbagliata di 1-2 centesimi.
- **Contributi INPS sull'imponibile arrotondato all'euro** (fonte F10, documento tecnico UniEmens).
- Totali e differenze arrotondati come ROUND di Excel in tutte e tre le versioni.

### Aggiunto

- Registro delle decisioni e dizionario dei dati; stile, tipi e copertura dei test nella CI.

## [1.0.0] - 2026-10-09

Prima versione completa: dieci controlli (C01-C10), la tranche di novembre 2026, il foglio con formule vive e lo
strumento nel browser.

[Non rilasciato]: https://github.com/D0M3N1C0X/controlli-cedolini/compare/v1.3.1...HEAD
[1.3.1]: https://github.com/D0M3N1C0X/controlli-cedolini/releases/tag/v1.3.1
[1.3.0]: https://github.com/D0M3N1C0X/controlli-cedolini/releases/tag/v1.3.0
[1.2.0]: https://github.com/D0M3N1C0X/controlli-cedolini/releases/tag/v1.2.0
[1.1.0]: https://github.com/D0M3N1C0X/controlli-cedolini/releases/tag/v1.1.0
[1.0.0]: https://github.com/D0M3N1C0X/controlli-cedolini/releases/tag/v1.0.0
