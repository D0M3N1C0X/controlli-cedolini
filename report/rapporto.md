# Controlli sui cedolini di settembre 2026

**Perimetro:** 6 clienti con quattro CCNL (Terziario, Metalmeccanico industria, Turismo e Logistica), 182 cedolini di settembre confrontati con quelli di agosto e con gli F24
**Dati:** Clienti e dipendenti inventati, con errori inseriti apposta; minimi, scatti e regole dei CCNL reali, con le fonti in [docs/fonti.md](../docs/fonti.md)
**Strumenti:** Uno script Python, lo stesso controllo in un [foglio di calcolo](../deliverables/foglio_controllo_cedolini.xlsx) e uno [strumento nel browser](https://d0m3n1c0x.github.io/controlli-cedolini/strumento/) dove i file restano sul computer

> Ventidue controlli da passare prima di mandare i cedolini al cliente. I controlli ricalcolano ogni voce dalle regole del contratto e dell'INPS, o la confrontano con il mese prima e con l'F24: non serve sapere come l'ha calcolata il software paghe. Non è consulenza del lavoro.

## In sintesi

- **67 segnalazioni: 63 cedolini e 1 F24**, 49 ad alta priorità; cliente A 9, cliente B 32, cliente C 9, cliente D 7, cliente E 5, cliente F 5.
- **10 dipendenti sono pagati sotto il minimo:** il tabellare è fermo alla tranche precedente del loro CCNL, o senza l'elemento perequativo nella Logistica. Mancano 305,24 € al mese in tutto, più gli arretrati dalla tranche mancata.
- **L'F24 del cliente C ha 212,40 € di ritenute in meno** della somma dei cedolini: va integrato prima della scadenza del versamento.
- **Dal 1° novembre 2026 i minimi del Terziario salgono:** 3.892,67 € al mese per 118 dipendenti. Il superminimo assorbibile ne copre 1.443,69 € in 44 casi; restano 2.448,98 € al mese, 34.286 € l'anno su 14 mensilità.
- **I controlli trovano ogni alterazione sopra il centesimo:** tutte le 855 delle 1.100 prove casuali che superano il centesimo (sezione 4). Un errore coerente lo vedono solo se nasce da un cambio rispetto al mese prima (C10).
- **Su un anno intero, nove errori di configurazione del software paghe** (sezione 5): i 6 errori di regola sono segnalati dal primo mese e in ogni mese dopo; dei 3 di anagrafica, uno sbagliato dall'assunzione non lo vede nessun controllo, gli altri due li vede C10 una volta sola. L'anno pulito non dà falsi allarmi.
- **Gli stessi cedolini alimentano gli altri strumenti** (sezione 6): l'estratto per il kit della trasparenza retributiva dà gli stessi divari al codice del kit e a questo, e INPS e TFR tornano con il modello del costo del lavoro.

## 1. Le segnalazioni, cedolino per cedolino

| Matricola | Cliente | Controllo | Priorità | Atteso | Trovato | Differenza |
|---|---|---|---:|---:|---:|---:|
| B031 | B | C01 | alta | 890,84 € | 873,34 € | −17,50 € |
| B036 | B | C01 | alta | 1.486,38 € | 1.456,03 € | −30,35 € |
| B044 | B | C01 | alta | 2.233,58 € | 2.186,23 € | −47,35 € |
| B052 | B | C01 | alta | 1.658,01 € | 1.626,39 € | −31,62 € |
| B064 | B | C01 | alta | 1.395,89 € | 1.371,58 € | −24,31 € |
| B082 | B | C01 | alta | 1.395,89 € | 1.371,58 € | −24,31 € |
| D308 | D | C01 | alta | 1.658,57 € | 1.618,70 € | −39,87 € |
| E337 | E | C01 | alta | 1.916,35 € | 1.868,92 € | −47,43 € |
| F341 | F | C01 | alta | 1.460,13 € | 1.437,63 € | −22,50 € |
| F351 | F | C01 | alta | 1.387,67 € | 1.367,67 € | −20,00 € |
| A007 | A | C02 | alta | 49,68 € | 24,84 € | −24,84 € |
| A016 | A | C02 | alta | 61,98 € | 41,32 € | −20,66 € |
| B025 | B | C02 | alta | 38,94 € | 19,47 € | −19,47 € |
| B047 | B | C02 | alta | 24,84 € | 0,00 € | −24,84 € |
| D302 | D | C02 | alta | 59,28 € | 29,64 € | −29,64 € |
| A009 | A | C03 | alta | 159,63 € | 164,69 € | 5,06 € |
| B053 | B | C03 | alta | 86,93 € | 81,88 € | −5,05 € |
| B087 | B | C03 | alta | 133,37 € | 125,63 € | −7,74 € |
| B191 | B | C03 | alta | 529,92 € | 523,15 € | −6,77 € |
| C098 | C | C03 | alta | 211,13 € | 198,87 € | −12,26 € |
| A001 | A | C04 | media | 146,02 € | 133,06 € | −12,96 € |
| B090 | B | C04 | media | 206,84 € | 193,03 € | −13,81 € |
| C093 | C | C04 | media | 175,06 € | 171,27 € | −3,79 € |
| A015 | A | C05 | media | 29,61 gg | 27,44 gg | −2,17 gg |
| B058 | B | C05 | media | 20,48 gg | 18,31 gg | −2,17 gg |
| C099 | C | C05 | media | 12,58 gg | 10,42 gg | −2,17 gg |
| D303 | D | C05 | media | 14,69 gg | 14,60 gg | −0,08 gg |
| A005 | A | C06 | alta | 1.336,88 € | 1.374,38 € | 37,50 € |
| C107 | C | C06 | alta | 1.224,71 € | 1.324,71 € | 100,00 € |
| A008 | A | C07 | media | 1.637,54 € | 2.095,61 € | 458,07 € |
| B020 | B | C07 | media | 2.021,13 € | 2.487,65 € | 466,52 € |
| F24 | C | C08 | alta | 3.510,18 € | 3.297,78 € | −212,40 € |
| B040 | B | C09 | alta | valido | `CPTFPV79H01Z105A` | - |
| B070 | B | C09 | alta | valido | `FZTSLD68R18Z151A` | - |
| B061 | B | C10 | alta | livello 4 | livello 5 | - |
| C108 | C | C10 | alta | superminimo 50 | superminimo 0 | - |
| A011 | A | C11 | media | 13ª 9; 14ª 3 | 13ª 9; 14ª 9 | - |
| B034 | B | C11 | media | 13ª 7; 14ª 3 | 13ª 8; 14ª 3 | - |
| B092 | B | C11 | media | 13ª 9; 14ª 3 | 13ª 8; 14ª 3 | - |
| D301 | D | C11 | media | 13ª 5; 14ª 0 | 13ª 6; 14ª 0 | - |
| B062 | B | C12 | alta | 470,59 € | 1.411,76 € | 941,17 € |
| E335 | E | C12 | alta | 317,38 € | 335,97 € | 18,59 € |
| B027 | B | C13 | alta | 1.980,46 € | 1.716,40 € | −264,06 € |
| F356 | F | C13 | alta | 1.406,78 € | 1.190,35 € | −216,43 € |
| B076 | B | C14 | alta | 20 gg | 10 gg | −10 gg |
| D305 | D | C14 | alta | 60 gg | 45 gg | −15 gg |
| F358 | F | C14 | alta | 38 gg | 15 gg | −22 gg |
| B080 | B | C15 | alta | 682,94 € | 675,46 € | −7,48 € |
| D315 | D | C15 | alta | 0,00 € | 473,00 € | 473,00 € |
| E330 | E | C15 | alta | 815,94 € | 509,96 € | −305,98 € |
| B026 | B | C16 | media | carenza non dovuta | 131,43 € | - |
| E336 | E | C16 | media | carenza 100% | 0,00 € | - |
| C095 | C | C17 | alta | 1.005,12 € | 861,60 € | −143,52 € |
| A017 | A | C18 | media | 33,16 ore | 39,82 ore | 6,67 ore |
| C103 | C | C18 | media | 51,75 ore | 53,92 ore | 2,17 ore |
| E323 | E | C18 | media | 58,31 ore | 61,31 ore | 3,00 ore |
| B027 | B | C19 | alta | 23.446,76 € | 23.604,31 € | 157,55 € |
| B038 | B | C19 | alta | 6.314,85 € | 6.465,86 € | 151,01 € |
| B051 | B | C19 | alta | 11.694,38 € | 11.743,95 € | 49,57 € |
| B030 | B | C20 | alta | 60,47 € | 0,00 € | −60,47 € |
| B041 | B | C20 | alta | 373,68 € | 375,21 € | 1,53 € |
| C097 | C | C20 | alta | 71,85 € | 155,18 € | 83,33 € |
| B027 | B | C21 | alta | 1.194,70 € | 444,85 € | −749,85 € |
| B038 | B | C21 | alta | 1.000,65 € | 710,99 € | −289,66 € |
| B081 | B | C22 | alta | 1.452,51 € | 1.452,13 € | −0,38 € |
| D318 | D | C22 | alta | 978,05 € | 782,44 € | −195,61 € |
| F357 | F | C22 | alta | 585,84 € | 273,57 € | −312,27 € |

**Cosa fare, per controllo**

| Controllo | Cosa fare |
|---|---|
| C01 Minimo tabellare | Aggiornare il tabellare al minimo in vigore e pagare la differenza dei mesi arretrati |
| C02 Scatti di anzianità | Inserire lo scatto maturato e verificare la data di decorrenza |
| C03 Contributi INPS | Correggere l'aliquota nella posizione INPS del cliente: CIGS e FIS dipendono dalla media dei dipendenti nel semestre; sopra 4.685 € al mese si aggiunge l'1% |
| C04 Quota TFR | Ricalcolare il rateo includendo scatti e superminimo |
| C05 Residuo ferie | Riallineare il residuo: maturazione del mese non registrata |
| C06 Quadratura | Ricontrollare le voci: il cedolino non quadra |
| C07 Variazione del netto | Chiedere al cliente l'evento che giustifica la variazione |
| C08 Riconciliazione F24 | Integrare la delega prima della scadenza del versamento |
| C09 Codice fiscale | Correggere il codice fiscale in anagrafica |
| C10 Anagrafica | Verificare il cambio con il cliente e con i documenti: se non c'è stato, correggere l'anagrafica |
| C11 Ratei 13ª e 14ª | Ricontare i dodicesimi dalla data di assunzione e correggere i ratei prima della tredicesima di dicembre |
| C12 Tredicesima e quattordicesima pagate | Ricalcolare la mensilità con i dodicesimi giusti, da gennaio per la tredicesima e da luglio per la quattordicesima, e regolare la differenza: pagarla se manca, recuperarla se è stata pagata in più |
| C13 Ferie non godute | Ricalcolare le ferie non godute con la quota giornaliera del CCNL (1/26 della retribuzione mensile, 1/22 nella Logistica) e regolare la differenza: pagarla se manca, recuperarla se è in più |
| C14 Preavviso | Verificare la data della lettera. Licenziamento: i giorni di preavviso non lavorati si pagano come indennità sostitutiva. Dimissioni: il preavviso non dato si può trattenere come indennità a carico del dipendente |
| C15 Indennità di malattia INPS | Ricalcolare l'indennità sulla retribuzione del mese prima × mensilità / 12 / 30, al 50% dal 4° al 20° giorno e al 66,66% dopo (80% nei pubblici esercizi; niente per gli impiegati dell'industria), e correggere il conguaglio con l'INPS nel flusso UniEmens |
| C16 Carenza di malattia | Applicare la regola del CCNL. Terziario: dal quinto evento dell'anno la carenza non si paga, salvo ricovero, prognosi di almeno 12 giorni, terapie salvavita o gravidanza. Metalmeccanico: dal quarto evento breve il 66%, poi il 50%. Turismo: si paga se la malattia supera i 5 giorni. Se è dovuta e manca, pagarla |
| C17 Indennità di maternità INPS | Ricalcolare l'indennità all'80% della retribuzione media giornaliera, ratei compresi, e correggere il conguaglio con l'INPS; l'integrazione al 100% resta a carico dell'azienda |
| C18 Permessi ROL ed ex festività | Rifare la maturazione dei permessi con le ore del CCNL (Terziario 72 o 56 di riduzione d'orario più 32 di ex festività; Metalmeccanico e Turismo 104; Logistica 72), in proporzione al part-time e con la regola dei nuovi assunti dove c'è |
| C19 TFR liquidato | Rifare il conteggio: coefficiente ISTAT del mese giusto (dal 15 in poi conta il mese), imposta sostitutiva del 17% sulla rivalutazione, 0,50% tolto dalle quote dell'anno; regolare la differenza |
| C20 IRPEF del mese | Controllare la tabella IRPEF del software (33% sul secondo scaglione dal 2026), l'ulteriore detrazione e la somma del cuneo fiscale, il trattamento integrativo; rifare la ritenuta e correggere nel mese dopo |
| C21 Conguaglio IRPEF alla cessazione | Rifare il conguaglio: imposta dell'anno sull'imponibile da gennaio, detrazioni e trattamento integrativo rapportati ai giorni di lavoro, meno quanto trattenuto o erogato; consegnare il conteggio con la CU |
| C22 Integrazione del datore di lavoro | Ricalcolare l'integrazione con la regola del CCNL (Terziario: il netto non sotto il 75% dal 4° al 20° giorno e il 100% dopo; Metalmeccanico e Logistica: la retribuzione intera meno l'indennità INPS) e pagare la differenza nel mese dopo |

*C07 non dice che il cedolino è sbagliato: dice che il netto è cambiato di oltre il 20% senza un evento registrato. Le assunzioni del mese, gli straordinari dichiarati e il passaggio a part-time non sono segnalati.*

## 2. F24 contro cedolini

| Cliente | Ritenute in F24 (1001) | Ritenute nei cedolini | Differenza | Contributi in F24 | Contributi nei cedolini | Differenza |
|---|---:|---:|---:|---:|---:|---:|
| A | 2.813,86 € | 2.813,86 € | 0,00 € | 3.151,67 € | 3.151,67 € | 0,00 € |
| B | 17.903,16 € | 17.903,16 € | 0,00 € | 15.821,13 € | 15.821,13 € | 0,00 € |
| C | 3.297,78 € | 3.510,18 € | −212,40 € | 4.184,84 € | 4.184,84 € | 0,00 € |
| D | 7.144,46 € | 7.144,46 € | 0,00 € | 5.820,99 € | 5.820,99 € | 0,00 € |
| E | 3.409,88 € | 3.409,88 € | 0,00 € | 2.923,00 € | 2.923,00 € | 0,00 € |
| F | 4.763,04 € | 4.763,04 € | 0,00 € | 4.504,93 € | 4.504,93 € | 0,00 € |

*Le ritenute dei cedolini seguono le regole IRPEF 2026, che C20 ricalcola: qui conta che la delega porti la loro somma.*

## 3. La tranche del 1° novembre 2026

Il rinnovo del CCNL Terziario del 22 marzo 2024 alza i minimi a novembre 2026 e di nuovo a febbraio 2027; gli altri tre CCNL hanno la prossima tranche nel 2027 (Logistica a gennaio, Metalmeccanico e Turismo a giugno), e i loro clienti non sono in questa tabella. Per ogni dipendente: l'aumento del livello, riproporzionato al part-time; quanto ne assorbe il superminimo, se la lettera di assunzione lo dice assorbibile; quanto resta da pagare.

| Cliente | Dipendenti | Aumento al mese | Assorbito | Da pagare al mese | Costo annuo (14 mensilità) |
|---|---:|---:|---:|---:|---:|
| Cliente A | 18 | 565,41 € | 277,65 € | 287,76 € | 4.029 € |
| Cliente B | 73 | 2.454,80 € | 859,90 € | 1.594,90 € | 22.329 € |
| Cliente C | 27 | 872,46 € | 306,14 € | 566,32 € | 7.928 € |

*Lordo dipendente, senza i contributi a carico dell'azienda. L'assorbibilità del superminimo dipende dalla lettera di assunzione e dagli accordi aziendali: va verificata dipendente per dipendente prima di comunicarla.*

## 4. Quanto ci si può fidare dei controlli

**Sugli errori inseriti.** 67 su 67, nessun falso allarme. Dimostra che i controlli fanno quello che dicono, non che troverebbero errori reali: gli errori li ho scelti io.

| Controllo | Errori inseriti | Trovati | Mancati | Falsi allarmi |
|---|---:|---:|---:|---:|
| C01 Minimo tabellare | 10 | 10 | 0 | 0 |
| C02 Scatti di anzianità | 5 | 5 | 0 | 0 |
| C03 Contributi INPS | 5 | 5 | 0 | 0 |
| C04 Quota TFR | 3 | 3 | 0 | 0 |
| C05 Residuo ferie | 4 | 4 | 0 | 0 |
| C06 Quadratura | 2 | 2 | 0 | 0 |
| C07 Variazione del netto | 2 | 2 | 0 | 0 |
| C08 Riconciliazione F24 | 1 | 1 | 0 | 0 |
| C09 Codice fiscale | 2 | 2 | 0 | 0 |
| C10 Anagrafica | 2 | 2 | 0 | 0 |
| C11 Ratei 13ª e 14ª | 4 | 4 | 0 | 0 |
| C12 Tredicesima e quattordicesima pagate | 2 | 2 | 0 | 0 |
| C13 Ferie non godute | 2 | 2 | 0 | 0 |
| C14 Preavviso | 3 | 3 | 0 | 0 |
| C15 Indennità di malattia INPS | 3 | 3 | 0 | 0 |
| C16 Carenza di malattia | 2 | 2 | 0 | 0 |
| C17 Indennità di maternità INPS | 1 | 1 | 0 | 0 |
| C18 Permessi ROL ed ex festività | 3 | 3 | 0 | 0 |
| C19 TFR liquidato | 3 | 3 | 0 | 0 |
| C20 IRPEF del mese | 3 | 3 | 0 | 0 |
| C21 Conguaglio IRPEF alla cessazione | 2 | 2 | 0 | 0 |
| C22 Integrazione del datore di lavoro | 3 | 3 | 0 | 0 |

**Su alterazioni casuali.** 1.100 prove: una voce a caso di un cedolino corretto, cambiata di un importo a caso. La tabella dice quante volte almeno un controllo se ne accorge.

| Voce alterata | ± 0,005 € | ± 0,02 € | ± 1,00 € | ± 10,00 € | ± 100,00 € |
|---|---:|---:|---:|---:|---:|
| tabellare | 15% | 100% | 100% | 100% | 100% |
| scatti | 13% | 100% | 100% | 100% | 100% |
| superminimo | 0% | 100% | 100% | 100% | 100% |
| straordinari | 4% | 100% | 100% | 100% | 100% |
| lordo | 0% | 100% | 100% | 100% | 100% |
| contributi inps | 49% | 100% | 100% | 100% | 100% |
| irpef | 16% | 100% | 100% | 100% | 100% |
| altre trattenute | 0% | 100% | 100% | 100% | 100% |
| netto | 0% | 100% | 100% | 100% | 100% |
| quota tfr | 0% | 100% | 100% | 100% | 100% |
| ferie residuo | 0% | 100% | 100% | 100% | 100% |

*Sotto la tolleranza di un centesimo l'alterazione si confonde con un arrotondamento, ed è giusto che passi. Sopra, la trovano tutte: 100%. Per le ferie l'importo è in giorni.*

**Perché regole e non un modello statistico.** Un rilevatore che non sa nulla del contratto confronta ogni cedolino con gli altri dello stesso cliente su quattro rapporti (contributi su lordo, TFR su retribuzione ordinaria, netto su lordo, netto sul mese prima) e segnala chi si allontana dalla mediana. Sugli stessi errori:

| Metodo | Cedolini sbagliati | Trovati | Falsi allarmi | Precisione |
|---|---:|---:|---:|---:|
| Statistico, z oltre 3 | 63 | 29 | 18 | 62% |
| Statistico, z oltre 3,5 | 63 | 27 | 14 | 66% |
| Statistico, z oltre 5 | 63 | 24 | 10 | 71% |
| Regole (C01-C22) | 63 | 63 | 0 | 100% |

*Il rilevatore confronta ogni cedolino con quelli dello stesso cliente, perché posizioni INPS diverse non sono anomalie. Vede solo gli errori che spostano un rapporto (contributi, TFR, variazioni del netto, malattia, carenza, maternità, integrazione del datore); minimi, scatti, ferie, codice fiscale, anagrafica, IRPEF, assenze e permessi richiedono di conoscere il contratto e le regole INPS, e lì non trova nulla. I cedolini di uscita li segnala tutti, giusti o sbagliati, perché il netto salta rispetto al mese prima: così prende anche gli errori di cessazione, ma i cedolini di uscita corretti diventano falsi allarmi. Su un dominio scritto in regole, le regole vincono; la statistica serve dove una regola non c'è.*

**Il limite, e come C10 lo restringe.** Un errore coerente passa i controlli aritmetici: il dipendente A003 è assunto al 4° livello; inserito al 5° e ricalcolato da capo, il cedolino torna in ogni voce e prende 77,98 € netti in meno al mese. Se l'errore nasce da un cambio rispetto al mese prima, senza un evento che lo spieghi, lo trova C10: i due errori di anagrafica inseriti (un livello, un superminimo azzerato) sono segnalati. Resta invisibile solo se è sbagliato fin dall'assunzione: lì serve il confronto con i documenti del cliente, lettera di assunzione e mansioni.

## 5. Un anno intero e gli errori di configurazione

**Perché.** Gli errori inseriti e le prove casuali toccano una voce di un cedolino. Un software paghe configurato male sbaglia la regola, per tutti i dipendenti del cliente e per tutti i mesi, e ricalcola a valle: lordo, contributi, imponibile, IRPEF e netto tornano fra loro. Per vedere cosa succede, i dipendenti dell'anagrafica passano un anno intero, gennaio-dicembre 2026: 2.102 cedolini mensili e 332 cedolini a parte di quattordicesima (luglio) e tredicesima (dicembre), con le tranche dei minimi nel mese in cui entrano in vigore (Metalmeccanico e Turismo a giugno, Terziario a novembre), gli scatti che maturano, ferie, permessi, straordinari, tre passaggi di livello e una trasformazione in part-time.

**L'anno pulito: 0 segnalazioni su 2.434 cedolini.** Nessun falso allarme in nessun mese, compresi giugno e novembre, quando cambiano i minimi. Ma i cedolini li genera lo stesso codice che scrive le regole: dice che i controlli non inventano errori dove le regole sono rispettate, non quanti falsi allarmi darebbe un export reale. Gli eventi contano: se i quattro eventi legittimi non fossero registrati sul cedolino, le segnalazioni sarebbero 5 (C07 1, C10 4), ed è giusto: un cambio di livello o di orario senza un documento è una domanda da fare al cliente.

**Nove errori di configurazione.** Ognuno su un cliente o su un dipendente, da un mese a dicembre. *Esposti*: i cedolini che l'errore cambia (mensili e mensilità aggiuntive); *segnalati*: quelli su cui almeno un controllo scatta. L'effetto è la differenza nell'anno rispetto all'anno pulito, dal lato del dipendente.

| Errore | Tipo | Cliente | Dal | Esposti | Segnalati | Prima segnalazione | Controlli | Netto nell'anno | Contributi |
|---|---|---|---:|---:|---:|---|---|---:|---:|
| K1 Tranche di giugno non caricata | regola | E | 2026-06 | 142 | 111 | 2026-06 | C01 | −3.841,47 € | −431,53 € |
| K2 CIGS non applicata | regola | F | 2026-01 | 240 | 240 | 2026-01 | C03 | 911,98 € | −1.453,97 € |
| K3 CCNL a 13 mensilità invece di 14 | regola | A | 2026-01 | 233 | 215 | 2026-01 | C04, C11, C20 | −29.227,51 € | 0,00 € |
| K4 Scaglioni IRPEF del 2025 | regola | B | 2026-01 | 79 | 79 | 2026-01 | C20 | −228,33 € | 0,00 € |
| K5 Scatto pagato un mese prima | regola | C | 2026-01 | 13 | 11 | 2026-02 | C02 | 170,32 € | 21,85 € |
| K6 Ferie a 22 giorni invece di 26 | regola | B | 2026-01 | 881 | 881 | 2026-01 | C05 | 0,00 € | 0,00 € |
| K7 Livello sbagliato dall'assunzione | anagrafica | B | 2025-12 | 14 | 0 | mai | nessuno | 1.877,98 € | 237,50 € |
| K8 Part-time inserito a giugno senza lettera | anagrafica | C | 2026-06 | 9 | 1 | 2026-06 | C10 | −3.234,18 € | −348,23 € |
| K9 Superminimo assorbito ma non assorbibile | anagrafica | A | 2026-11 | 3 | 1 | 2026-11 | C10 | −68,82 € | −5,86 € |

**Un errore nella regola si vede subito, e ogni mese.** 6 dei 6 errori di regola sono segnalati nel primo mese in cui cambiano un cedolino, e poi in ogni mese dopo, perché i controlli ricalcolano la regola da capo e non si fidano del software. Quanti cedolini espongono dipende dall'errore, non dai controlli: gli scaglioni IRPEF del 2025 toccano solo chi supera i 28.000 € l'anno (79 cedolini su 888), lo scatto anticipato solo il mese prima della maturazione (13 cedolini). Le ferie a 22 giorni non cambiano il netto, ma a dicembre il cliente B ha 286 giorni di ferie in meno nei residui dei suoi 74 dipendenti: quattro a testa, meno per chi è entrato nell'anno. Quello che sfugge sono le mensilità aggiuntive costruite su una base sbagliata: C12 rifà il conto sul tabellare del cedolino, e quel tabellare l'ha già segnalato C01. Con il CCNL a 13 mensilità (K3) la quattordicesima di luglio non viene pagata affatto (31.468,12 € nel cliente A): nessun controllo guarda un cedolino che non c'è, ma C11 vede i ratei di quattordicesima a zero da gennaio.

**Un errore nell'anagrafica si vede una volta, o mai.** Il livello sbagliato dall'assunzione (K7) espone 14 cedolini e non ne segnala nessuno: 1.877,98 € netti in più nell'anno e nessun controllo lo vede, perché ogni voce torna con il livello inserito. Il part-time inserito a giugno senza lettera (K8) e il superminimo assorbito ma non assorbibile (K9) li trova C10, ma una volta sola, nel mese in cui l'anagrafica cambia: dal mese dopo il dato sbagliato è la nuova base e tutto torna. Se quella segnalazione si chiude senza guardare la lettera di assunzione, l'errore resta per sempre: 3.234,18 € netti in meno in sette mesi per K8. Per questo C10 è ad alta priorità.

**Cosa ne segue.** I controlli aritmetici bastano per le regole: tranche, aliquote, scaglioni, divisori, ferie. Per l'anagrafica (3 errori su 9) serve un confronto con i documenti almeno una volta: all'assunzione, a ogni segnalazione C10, e a campione una volta l'anno.

## 6. Il ponte con la trasparenza retributiva e il costo del lavoro

**Perché.** I cedolini sono la fonte dei dati che chiedono la direttiva (UE) 2023/970 sulla trasparenza retributiva e il budget del personale. Se le voci vanno nel posto sbagliato, il divario retributivo è sbagliato prima di cominciare. Questa sezione collega i cedolini dell'anno (sezione 5) agli altri due strumenti del portfolio: [pay-transparency-readiness-kit](https://github.com/D0M3N1C0X/pay-transparency-readiness-kit) e [workforce-cost-model](https://github.com/D0M3N1C0X/workforce-cost-model).

**Ogni voce del cedolino ha una natura.** Il kit misura la retribuzione su tutte le voci (direttiva) e, per l'Italia, sulle sole voci fisse e continuative (il livello retributivo del recepimento, come lo legge il kit). La tabella dice dove va ogni voce nell'estratto del kit:

| Voce del cedolino | Colonna del kit | Natura | Perché |
|---|---|---|---|
| tabellare | base_pay | fissa e continuativa | minimo del livello: retribuzione di base |
| scatti | base_pay | fissa e continuativa | scatti di anzianità: maturano per regola generale |
| superminimo | base_pay | fissa e continuativa | superminimo individuale: pagato ogni mese |
| tredicesima | base_pay | fissa e continuativa | mensilità aggiuntiva dovuta dal CCNL |
| quattordicesima | base_pay | fissa e continuativa | mensilità aggiuntiva dovuta dal CCNL |
| straordinari | bonus | variabile | dipende dalle ore del mese: componente variabile (il kit non ha una colonna per lo straordinario, la colonna bonus è variabile) |
| quota tfr | fuori | esclusa | accantonamento differito, non pagato nell'anno; liquidato alla cessazione |
| malattia inps | fuori | esclusa | anticipata per conto dell'INPS: non la paga il datore di lavoro |
| maternita inps | fuori | esclusa | anticipata per conto dell'INPS: non la paga il datore di lavoro |
| integrazione datore | base_pay | sostitutiva | prende il posto della retribuzione dei giorni di assenza |
| contributi inps | fuori | esclusa | trattenuta, non retribuzione |
| irpef | fuori | esclusa | trattenuta, non retribuzione |

**L'estratto.** 177 dipendenti, la retribuzione pagata da gennaio a dicembre 2026 e le ore contrattuali del periodo, nel formato "anno di riferimento" del kit, un datore di lavoro per cliente ([data/ponte/estratto_ptk.csv](../data/ponte/estratto_ptk.csv)). Gli indicatori dell'articolo 9 calcolati qui e quelli del codice del kit, al commit 18be663, sullo stesso file coincidono su tutti i 6 clienti: la CI rifà il conto col kit a ogni modifica.

| Cliente | Dipendenti | Donne | Divario orario medio | Mediano | Divario annuo medio | Variabili: donne / uomini che le ricevono |
|---|---:|---:|---:|---:|---:|---:|
| A | 18 | 9 | 10,4% | 3,1% | 14,8% | 78% / 89% |
| B | 74 | 45 | -3,6% | 4,0% | -8,0% | 76% / 69% |
| C | 27 | 16 | -6,0% | -7,7% | -3,2% | 81% / 55% |
| D | 22 | 11 | 1,9% | 1,3% | 8,0% | 100% / 64% |
| E | 16 | 7 | 8,0% | 11,3% | 17,3% | 100% / 78% |
| F | 20 | 9 | -2,0% | 4,4% | 1,0% | 67% / 100% |

*Un divario positivo vuol dire donne pagate meno. Annuo e orario differiscono per il part-time: la paga annua lo conta, quella oraria no, ed è per questo che la direttiva chiede tutti e due. Nessun cliente ha 100 dipendenti, la soglia più bassa dell'obbligo di relazione dell'articolo 9; il diritto di informazione dell'articolo 7 vale per tutti. I dati sono inventati: i divari dicono che il ponte funziona, non qualcosa sui clienti.*

**Le categorie sono i livelli del CCNL.** Lo stesso lavoro o un lavoro di pari valore, dentro un cliente, secondo la classificazione del contratto: 40 categorie, 6 con un divario orario di almeno il 5%, 18 sotto, 16 con un solo sesso ([report/ponte_categorie.csv](ponte_categorie.csv)). Nei livelli del CCNL il minimo è uguale per tutti: un divario viene da scatti (anzianità), superminimi, part-time e straordinari, cioè da quello che il kit chiede di giustificare con criteri oggettivi. Un livello sbagliato in anagrafica (K7 della sezione 5) sposta una persona di categoria: per la trasparenza è un errore doppio.

**Il costo del lavoro: due repository, gli stessi conti.** workforce-cost-model calcola il costo italiano dal lato del datore; il suo config.py è copiato al commit bdcfa57 con il checksum fissato. IVS: 23,81% a carico del datore lì, 9,19% del dipendente qui, 33,00% in tutto, l'aliquota del Fondo pensioni lavoratori dipendenti. TFR: dodici quote mensili dei cedolini contro la retribuzione dell'anno / 13,5 del modello, per i 165 dipendenti con un anno intero allo stesso contratto: differenza mediana −1,64 €, la più grande 47,98 €. La formula è la stessa; la differenza è di calendario. La quota mensile proietta la retribuzione del mese su tutte le mensilità, la quota dell'anno guarda quello che è stato pagato: la tredicesima con la tranche di novembre, una quattordicesima che copre meno di dodici mesi per chi è entrato l'anno prima. L'articolo 2120 del codice civile guarda la retribuzione dell'anno: le quote mensili sono un acconto, da allineare a dicembre.

*Due cose che il modello di costo non fa, senza che il costo cambi. Lo 0,50% dell'imponibile che si toglie dal TFR e si versa all'INPS (L. 297/1982, art. 3) sposta 21.915 € l'anno dal fondo TFR ai contributi per questi dipendenti, ma il datore paga lo stesso totale. E le altre voci INPS e INAIL del datore (6,0% nel modello) sono illustrative lì: qui la posizione INPS di ogni cliente (CIGS, FIS) è nei parametri, ed è da lì che il modello dovrebbe prenderle per un cliente vero.*

## 7. Come lo userei in un team payroll

1. **Prima dell'invio, ogni mese:** l'export del software paghe entra nello script o nel foglio; si guardano solo le righe segnalate, a partire dalla priorità alta.
2. **C07 diventa una domanda al cliente,** non un errore: se lo straordinario c'è, si registra l'evento e il mese dopo non torna.
3. **Prima di ogni tranche contrattuale:** la tabella di novembre dice al cliente quanto costa l'aumento e chi assorbe, prima del cedolino e non dopo.
4. **Il passo successivo** è collegarlo all'export reale e misurare quante segnalazioni sono giuste nei primi due mesi, per tarare la soglia di C07.

## 8. Metodo e limiti

- **Due motori, una risposta.** Gli stessi controlli sono in Python e in formule nel foglio; il foglio Riconciliazione confronta ogni formula con Python, e la CI ricalcola il foglio con LibreOffice.
- **Contributi per posizione.** L'aliquota a carico del dipendente viene dalla media del semestre e dal settore del cliente (Parametri): va presa dalla sua posizione INPS, non stimata.
- **Scatti al livello attuale.** Il CCNL non rivaluta gli scatti già maturati con il passaggio di livello: chi ha cambiato livello va controllato a mano.
- **Quattro CCNL, impiegati.** Ogni cliente ha il suo contratto; nei dati d'esempio ci sono solo impiegati: operai e personale viaggiante hanno altre regole di malattia e preavviso e non sono controllati.
- **Un mese alla volta.** Ogni controllo guarda il mese e quello prima: le quote di malattia valgono per i primi periodi, e un evento lungo va ricontato a mano (C22). L'anno della sezione 5 mette in fila dodici mesi, ma ogni mese è ancora controllato solo col precedente.


**Le fonti al mese chiuso, ottobre 2026.** Ogni parametro che cambia nel tempo ha una data; un test ferma la pipeline se uno non copre il mese controllato. I primi a scadere, a fine dicembre 2026, sono IRPEF, detrazioni, cuneo e prima fascia INPS (F24, F25, F26, F15): vanno riletti a gennaio 2027.

| Parametro | Fonte | Vale fino a | Letto alla fonte | Il prossimo valore |
|---|---|---|---|---|
| Scaglioni IRPEF 2026 (23%, 33%, 43%) | F24 | dicembre 2026 | 2026-11-08 | legge di bilancio 2027, da rileggere a gennaio 2027 |
| Detrazioni per lavoro dipendente (art. 13 TUIR) | F25 | dicembre 2026 | 2026-11-08 | il testo in vigore scade il 31 dicembre 2026 |
| Cuneo fiscale: somma e ulteriore detrazione | F26 | dicembre 2026 | 2026-11-08 | dal 2027 cambia (D.lgs. 117/2026) |
| Prima fascia pensionabile 56.224 €, 4.685 € al mese | F15 | dicembre 2026 | 2026-11-25 | circolare INPS sui minimali e massimali 2027, di solito a fine gennaio |
| Indice FOI per la rivalutazione del TFR | F20 | ottobre 2026 | 2026-11-25 | il FOI di un mese esce verso la metà del mese dopo |
| Minimi del CCNL terziario, ultima tranche in tabella | F01 | fino al rinnovo | 2026-10-09 | dopo la tranche di febbraio 2027 in tabella, il prossimo rinnovo |
| Minimi del CCNL metalmeccanico, ultima tranche in tabella | F30-F40 | fino al rinnovo | 2026-11-09 | dopo la tranche di giugno 2027 in tabella, il prossimo rinnovo |
| Minimi del CCNL turismo, ultima tranche in tabella | F30-F40 | fino al rinnovo | 2026-11-09 | dopo la tranche di giugno 2027 in tabella, il prossimo rinnovo |
| Minimi del CCNL logistica, ultima tranche in tabella | F30-F40 | fino al rinnovo | 2026-11-09 | dopo la tranche di gennaio 2027 in tabella, il prossimo rinnovo |
