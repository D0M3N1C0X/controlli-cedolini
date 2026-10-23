# Changelog

Cosa cambia a ogni versione, per chi usa i controlli. Formato [Keep a Changelog](https://keepachangelog.com/it-IT/1.1.0/).
Le cose che vengono dopo sono in [docs/roadmap.md](docs/roadmap.md).

## [Non rilasciato]

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
