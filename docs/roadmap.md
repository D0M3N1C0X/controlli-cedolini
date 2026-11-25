# Roadmap

Cosa viene dopo, in ordine di valore per un team paghe. Ogni voce dice perché conta e cosa serve per farla. Le
date sono un'intenzione, non una promessa.

| # | Cosa | Perché conta | Cosa serve | Quando |
|---|---|---|---|---|
| 1 | **Misure da un uso reale**: errori veri, falsi allarmi e tempo su un mese di cedolini veri | Oggi la precisione è misurata solo su errori inseriti da me | Un cliente disposto a provare lo strumento nel browser: i file restano suoi | Appena possibile |
| 2 | **Operai e personale viaggiante** nei CCNL della v2.2 | C22 e le regole di malattia valgono per gli impiegati (D30); gli operai hanno un'altra base INPS e altri preavvisi | Le regole INPS per gli operai (giornate retribuite) e le parti del Metalmeccanico e della Logistica che li riguardano | 2027 |
| 3 | **Mappature degli export** dei software paghe più usati verso le colonne del modello | Oggi l'export va adattato a mano: è il primo ostacolo per chi prova | Un export vero (solo i nomi delle colonne) per ogni software | Con il punto 1 |
| 4 | **Altri contratti**, dopo i quattro della v2.2 (Terziario, Metalmeccanico, Turismo, Logistica): una riga di `config.CCNL` e una tabella per contratto | Il motore per contratto c'è (D28): ogni CCNL in più è lavoro di fonti, non di codice | La fonte primaria di ciascun contratto, e il testo vigente del Terziario dall'archivio CNEL | 2027 |
| 5 | **F24 completo**: quota INPS a carico dell'azienda e addizionali IRPEF | C08 oggi riconcilia solo ritenute 1001 e contributi dei dipendenti | Aliquote azienda per posizione; codici tributo 3802 e 3848 | 2027 |

Un anno intero di cedolini e nove errori di configurazione (sezione 5 del rapporto) dicono che l'anagrafica è
il punto cieco dei controlli aritmetici: un confronto con i documenti del cliente, all'assunzione e a ogni
segnalazione C10, resta un passo manuale.

L'indennità sostitutiva del preavviso (ex punto 2) è C23 da novembre 2026.

Le scelte che hanno portato fin qui sono in [decisioni.md](decisioni.md); cosa è già stato fatto, nel
[CHANGELOG](../CHANGELOG.md).
