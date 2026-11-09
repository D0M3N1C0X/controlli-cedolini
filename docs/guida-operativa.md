# Guida operativa: il controllo dei cedolini, ogni mese

La procedura per un team paghe che elabora cedolini per più clienti, ognuno con il suo CCNL (Terziario,
Metalmeccanico industria, Turismo pubblici esercizi, Logistica), e vuole fermare gli
errori **prima** che arrivino al cliente. Funziona con lo [strumento nel browser](https://d0m3n1c0x.github.io/controlli-cedolini/strumento/)
o con il [foglio di controllo](../deliverables/foglio_controllo_cedolini.xlsx): la logica è la stessa, i risultati
anche. Cosa controlla ogni controllo è nel [catalogo](catalogo-controlli.md).

## Chi fa cosa

| Ruolo | Chi è | Responsabilità |
|---|---|---|
| **Operatore paghe** | Chi elabora i cedolini del cliente | Raccoglie gli eventi, lancia i controlli, corregge, annota |
| **Revisore** | Il responsabile del team o un collega senior | Approva il rilascio, decide sulle segnalazioni lasciate aperte |
| **Referente del cliente** | Chi gestisce il personale dal lato del cliente | Conferma eventi, anagrafica e lettere di assunzione |

| Passo | Operatore | Revisore | Cliente |
|---|---|---|---|
| 0. Parametri del cliente | esegue | approva | fornisce i dati |
| 1. Eventi del mese | raccoglie | | conferma |
| 2-3. Export e controlli | esegue | | |
| 4. Smistamento delle segnalazioni | esegue | consultato sulle medie | consultato |
| 5. Correzione e nuovo controllo | esegue | | |
| 6. Rilascio | prepara | **decide** | |
| 7. Invio e F24 | esegue | | riceve |
| 8. Registro del mese | compila | legge | |

## Prima del primo mese, e a ogni rinnovo del contratto

**0. I parametri del cliente.** Nel foglio Parametri, o nella pagina dello strumento:

- l'**aliquota INPS** a carico del dipendente, dalla posizione del cliente (9,19% è solo il valore generale);
- il **CCNL** del cliente: decide minimi, scatti, mensilità, ferie, permessi, preavviso, malattia e integrazione
  (tabelle in `data/ccnl_*.csv`, fonti in [fonti.md](fonti.md));
- se il cliente **versa al FIS**: un'impresa industriale no, ha la CIGO;
- per la tranche di novembre, quali **superminimi sono assorbibili**: lo dice la lettera di assunzione, non il
  software.

## Ogni mese

**1. Gli eventi.** Prima di controllare, chiedere al cliente cosa è cambiato: assunzioni, straordinari, passaggi
di livello o di part-time. Ogni cambio vero va scritto nella colonna `evento` del cedolino. Senza, C07 e C10 lo
segnalano: è il loro mestiere.

**2. L'export.** Dal software paghe: i cedolini del mese e quelli del mese prima, con le colonne del
[modello](https://d0m3n1c0x.github.io/controlli-cedolini/strumento/modello_cedolini.csv); l'F24 del mese, con
ritenute 1001 e contributi per cliente. I ratei di tredicesima e quattordicesima sono facoltativi: senza, C11 non
si applica. Per chi lascia, l'evento `cessazione` con data, tipo (dimissioni o licenziamento), giorni di preavviso,
mensilità aggiuntive e ferie non godute pagate: senza queste colonne, C12-C14 non si applicano e il cedolino di
uscita non quadra in C06, perché il lordo comprende importi che il file non riporta. Assenze, permessi e TFR
liquidato sono colonne facoltative anche loro: malattia (date, numero dell'evento nell'anno, esenzione, indennità
INPS, carenza pagata), maternità (date e indennità INPS), ore di permesso maturate, godute e residue, e per chi lascia
fondo TFR al 31 dicembre, quote e imponibile dell'anno, TFR liquidato; per l'IRPEF somma del cuneo e trattamento integrativo, e all'uscita i dati del conguaglio. Senza, C15-C21 non si applicano.

**Prima del primo mese, per ogni cliente:** la media dei dipendenti nel semestre di riferimento, dalla posizione
INPS, e i dipendenti in forza. La prima decide CIGS e FIS (C03), i secondi le ore di riduzione d'orario (C18).

**3. I controlli.** Nello strumento: caricare i due file e premere "Esegui i controlli". Nel foglio: incollare i
cedolini nel foglio Mese (colonne A-W, ratei in AU-AV, voci di chi lascia in AZ-BE, assenze, permessi e TFR in BQ-CF),
quelli del mese prima nel foglio Mese precedente, l'F24 nel foglio F24; la posizione di ogni cliente nella tabella
Clienti del foglio Parametri, e l'indice FOI del mese di ogni cessazione.

**4. Lo smistamento.** Ogni segnalazione ha valore atteso, valore trovato e cosa fare.

- **Priorità alta** (C01, C02, C03, C06, C08, C09, C10, C12-C15, C17, C19): si risolvono tutte prima dell'invio.
- **Priorità media** (C04, C05, C07, C11, C16, C18): si risolvono, oppure si scrive perché restano aperte e il revisore
  decide.
- **Un falso allarme si annota**, con il motivo: è il dato che serve per tarare soglie e regole.

**5. Correzione e nuovo controllo.** Correggere nel software paghe, rifare l'export, rilanciare i controlli.
Si ripete finché le segnalazioni ad alta priorità sono zero.

**6. Il rilascio.** Il revisore guarda il riepilogo per cliente e le note sulle segnalazioni medie rimaste. Criteri:

- [ ] zero segnalazioni ad alta priorità;
- [ ] ogni segnalazione media risolta o motivata per iscritto;
- [ ] C08 a zero per ogni cliente: l'F24 corrisponde ai cedolini;
- [ ] eventi del mese confermati dal cliente.

**7. Invio e F24.** Cedolini al cliente; la delega F24 solo dopo che C08 è a zero, entro la scadenza del
versamento.

**8. Il registro del mese.** Una riga per cliente, ogni mese:

| Mese | Cliente | Cedolini | Segnalazioni per controllo | Errori veri | Falsi allarmi | Minuti | Note |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

Dopo due o tre mesi il registro dice quanti errori i controlli fermano, quanto tempo costano e quali soglie
correggere: è la base per decidere se estenderli ad altri clienti.

## Quando è il controllo a sbagliare

Succede: una regola può non coprire un caso, o la fonte può essere cambiata. In quel caso non si forza il
cedolino per far tornare il controllo. Si annota il caso nel registro, si verifica la regola in [fonti.md](fonti.md)
e, se serve, si corregge la regola: come si fa è in [architettura.md](architettura.md).
