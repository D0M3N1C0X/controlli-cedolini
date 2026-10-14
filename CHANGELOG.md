# Changelog

Cosa cambia a ogni versione, per chi usa i controlli. Formato [Keep a Changelog](https://keepachangelog.com/it-IT/1.1.0/).
Le cose che vengono dopo sono in [docs/roadmap.md](docs/roadmap.md).

## [Non rilasciato]

### Aggiunto

- [Catalogo dei controlli](docs/catalogo-controlli.md): una scheda per controllo, generata da codice, foglio e
  segnalazioni, con un test che lo tiene aggiornato.
- [Guida operativa](docs/guida-operativa.md): la procedura mensile del team paghe, con ruoli e criteri di rilascio.
- [Architettura](docs/architettura.md): come restano uguali le tre versioni, come si aggiunge un controllo.
- Il rapporto online conta le visite con GoatCounter, senza cookie; lo strumento nel browser no.

### Cambiato

- La descrizione di C01 nomina anche gli altri elementi del minimo.

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

[Non rilasciato]: https://github.com/D0M3N1C0X/controlli-cedolini/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/D0M3N1C0X/controlli-cedolini/releases/tag/v1.2.0
[1.1.0]: https://github.com/D0M3N1C0X/controlli-cedolini/releases/tag/v1.1.0
[1.0.0]: https://github.com/D0M3N1C0X/controlli-cedolini/releases/tag/v1.0.0
