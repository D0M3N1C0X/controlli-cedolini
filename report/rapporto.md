# Controlli sui cedolini di settembre 2026

**Perimetro:** 3 clienti con il CCNL Terziario Confcommercio, 124 cedolini di settembre confrontati con quelli di agosto e con gli F24
**Dati:** Clienti e dipendenti inventati, con errori inseriti apposta; minimi e scatti del CCNL reali, con le fonti in [docs/fonti.md](../docs/fonti.md)
**Strumenti:** Uno script Python, lo stesso controllo in un [foglio di calcolo](../deliverables/foglio_controllo_cedolini.xlsx) e uno [strumento nel browser](https://d0m3n1c0x.github.io/controlli-cedolini/strumento/) dove i file restano sul computer

> Diciannove controlli da passare prima di mandare i cedolini al cliente. I controlli ricalcolano ogni voce dalle regole del contratto e dell'INPS, o la confrontano con il mese prima e con l'F24: non serve sapere come l'ha calcolata il software paghe. Non è consulenza del lavoro.

## In sintesi

- **44 segnalazioni: 42 cedolini e 1 F24**, 30 ad alta priorità; cliente A 9, cliente B 27, cliente C 8.
- **6 dipendenti sono pagati sotto il minimo:** il tabellare è fermo alla tranche di marzo 2025. Mancano 175,44 € al mese in tutto, più gli arretrati da novembre 2025.
- **L'F24 del cliente C ha 212,40 € di ritenute in meno** della somma dei cedolini: va integrato prima della scadenza del versamento.
- **Dal 1° novembre 2026 i minimi salgono:** 3.892,67 € al mese per 118 dipendenti. Il superminimo assorbibile ne copre 1.443,69 € in 44 casi; restano 2.448,98 € al mese, 34.286 € l'anno su 14 mensilità.
- **I controlli trovano ogni alterazione sopra il centesimo:** tutte le 861 delle 1.100 prove casuali che superano il centesimo (sezione 4). Un errore coerente lo vedono solo se nasce da un cambio rispetto al mese prima (C10).

## 1. Le segnalazioni, cedolino per cedolino

| Matricola | Cliente | Controllo | Priorità | Atteso | Trovato | Differenza |
|---|---|---|---:|---:|---:|---:|
| B031 | B | C01 | alta | 890,84 € | 873,34 € | −17,50 € |
| B036 | B | C01 | alta | 1.486,38 € | 1.456,03 € | −30,35 € |
| B044 | B | C01 | alta | 2.233,58 € | 2.186,23 € | −47,35 € |
| B052 | B | C01 | alta | 1.658,01 € | 1.626,39 € | −31,62 € |
| B064 | B | C01 | alta | 1.395,89 € | 1.371,58 € | −24,31 € |
| B082 | B | C01 | alta | 1.395,89 € | 1.371,58 € | −24,31 € |
| A007 | A | C02 | alta | 49,68 € | 24,84 € | −24,84 € |
| A016 | A | C02 | alta | 61,98 € | 41,32 € | −20,66 € |
| B025 | B | C02 | alta | 38,94 € | 19,47 € | −19,47 € |
| B047 | B | C02 | alta | 24,84 € | 0,00 € | −24,84 € |
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
| A005 | A | C06 | alta | 1.203,07 € | 1.240,57 € | 37,50 € |
| C107 | C | C06 | alta | 1.086,81 € | 1.186,81 € | 100,00 € |
| A008 | A | C07 | media | 1.510,13 € | 2.080,50 € | 570,37 € |
| B020 | B | C07 | media | 1.960,05 € | 2.548,30 € | 588,25 € |
| F24 | C | C08 | alta | 6.032,89 € | 5.820,49 € | −212,40 € |
| B040 | B | C09 | alta | valido | `CPTFPV79H01Z105A` | - |
| B070 | B | C09 | alta | valido | `FZTSLD68R18Z151A` | - |
| B061 | B | C10 | alta | livello 4 | livello 5 | - |
| C108 | C | C10 | alta | superminimo 50 | superminimo 0 | - |
| A011 | A | C11 | media | 13ª 9; 14ª 3 | 13ª 9; 14ª 9 | - |
| B034 | B | C11 | media | 13ª 7; 14ª 3 | 13ª 8; 14ª 3 | - |
| B092 | B | C11 | media | 13ª 9; 14ª 3 | 13ª 8; 14ª 3 | - |
| B062 | B | C12 | alta | 470,59 € | 1.411,76 € | 941,17 € |
| B027 | B | C13 | alta | 1.980,46 € | 1.716,40 € | −264,06 € |
| B076 | B | C14 | alta | 20 gg | 10 gg | −10 gg |
| B080 | B | C15 | alta | 682,94 € | 675,46 € | −7,48 € |
| B026 | B | C16 | media | carenza non dovuta | 151,65 € | - |
| C095 | C | C17 | alta | 1.005,12 € | 861,60 € | −143,52 € |
| A017 | A | C18 | media | 33,16 ore | 39,82 ore | 6,67 ore |
| C103 | C | C18 | media | 51,75 ore | 53,92 ore | 2,17 ore |
| B027 | B | C19 | alta | 23.446,76 € | 23.604,31 € | 157,55 € |
| B038 | B | C19 | alta | 6.314,85 € | 6.465,86 € | 151,01 € |
| B051 | B | C19 | alta | 11.694,38 € | 11.743,95 € | 49,57 € |

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
| C13 Ferie non godute | Ricalcolare le ferie non godute a 1/26 della retribuzione mensile per giorno e regolare la differenza: pagarla se manca, recuperarla se è in più |
| C14 Preavviso | Verificare la data della lettera. Licenziamento: i giorni di preavviso non lavorati si pagano come indennità sostitutiva. Dimissioni: il preavviso non dato si può trattenere come indennità a carico del dipendente |
| C15 Indennità di malattia INPS | Ricalcolare l'indennità sulla retribuzione del mese prima × 14/12 / 30, al 50% dal 4° al 20° giorno e al 66,66% dopo, e correggere il conguaglio con l'INPS nel flusso UniEmens |
| C16 Carenza di malattia | Contare gli eventi di malattia dell'anno: dal quinto la carenza non si paga, salvo ricovero, prognosi di almeno 12 giorni, terapie salvavita o gravidanza; se è dovuta e manca, pagarla |
| C17 Indennità di maternità INPS | Ricalcolare l'indennità all'80% della retribuzione media giornaliera, ratei compresi, e correggere il conguaglio con l'INPS; l'integrazione al 100% resta a carico dell'azienda |
| C18 Permessi ROL ed ex festività | Rifare la maturazione dei permessi: 72 o 56 ore di riduzione d'orario secondo i dipendenti, più 32 di ex festività, in proporzione al part-time e con la regola dei 2 e 4 anni per chi è entrato dopo marzo 2011 |
| C19 TFR liquidato | Rifare il conteggio: coefficiente ISTAT del mese giusto (dal 15 in poi conta il mese), imposta sostitutiva del 17% sulla rivalutazione, 0,50% tolto dalle quote dell'anno; regolare la differenza |

*C07 non dice che il cedolino è sbagliato: dice che il netto è cambiato di oltre il 20% senza un evento registrato. Le assunzioni del mese, gli straordinari dichiarati e il passaggio a part-time non sono segnalati.*

## 2. F24 contro cedolini

| Cliente | Ritenute in F24 (1001) | Ritenute nei cedolini | Differenza | Contributi in F24 | Contributi nei cedolini | Differenza |
|---|---:|---:|---:|---:|---:|---:|
| A | 4.551,81 € | 4.551,81 € | 0,00 € | 3.220,04 € | 3.220,04 € | 0,00 € |
| B | 25.086,64 € | 25.086,64 € | 0,00 € | 16.043,08 € | 16.043,08 € | 0,00 € |
| C | 5.820,49 € | 6.032,89 € | −212,40 € | 4.657,16 € | 4.657,16 € | 0,00 € |

*Le ritenute IRPEF dei dati sintetici non sono calcolate con le regole fiscali: servono solo a mostrare la riconciliazione.*

## 3. La tranche del 1° novembre 2026

Il rinnovo del CCNL Terziario del 22 marzo 2024 alza i minimi a novembre 2026 e di nuovo a febbraio 2027. Per ogni dipendente: l'aumento del livello, riproporzionato al part-time; quanto ne assorbe il superminimo, se la lettera di assunzione lo dice assorbibile; quanto resta da pagare.

| Cliente | Dipendenti | Aumento al mese | Assorbito | Da pagare al mese | Costo annuo (14 mensilità) |
|---|---:|---:|---:|---:|---:|
| Cliente A | 18 | 565,41 € | 277,65 € | 287,76 € | 4.029 € |
| Cliente B | 73 | 2.454,80 € | 859,90 € | 1.594,90 € | 22.329 € |
| Cliente C | 27 | 872,46 € | 306,14 € | 566,32 € | 7.928 € |

*Lordo dipendente, senza i contributi a carico dell'azienda. L'assorbibilità del superminimo dipende dalla lettera di assunzione e dagli accordi aziendali: va verificata dipendente per dipendente prima di comunicarla.*

## 4. Quanto ci si può fidare dei controlli

**Sugli errori inseriti.** 44 su 44, nessun falso allarme. Dimostra che i controlli fanno quello che dicono, non che troverebbero errori reali: gli errori li ho scelti io.

| Controllo | Errori inseriti | Trovati | Mancati | Falsi allarmi |
|---|---:|---:|---:|---:|
| C01 Minimo tabellare | 6 | 6 | 0 | 0 |
| C02 Scatti di anzianità | 4 | 4 | 0 | 0 |
| C03 Contributi INPS | 5 | 5 | 0 | 0 |
| C04 Quota TFR | 3 | 3 | 0 | 0 |
| C05 Residuo ferie | 3 | 3 | 0 | 0 |
| C06 Quadratura | 2 | 2 | 0 | 0 |
| C07 Variazione del netto | 2 | 2 | 0 | 0 |
| C08 Riconciliazione F24 | 1 | 1 | 0 | 0 |
| C09 Codice fiscale | 2 | 2 | 0 | 0 |
| C10 Anagrafica | 2 | 2 | 0 | 0 |
| C11 Ratei 13ª e 14ª | 3 | 3 | 0 | 0 |
| C12 Tredicesima e quattordicesima pagate | 1 | 1 | 0 | 0 |
| C13 Ferie non godute | 1 | 1 | 0 | 0 |
| C14 Preavviso | 1 | 1 | 0 | 0 |
| C15 Indennità di malattia INPS | 1 | 1 | 0 | 0 |
| C16 Carenza di malattia | 1 | 1 | 0 | 0 |
| C17 Indennità di maternità INPS | 1 | 1 | 0 | 0 |
| C18 Permessi ROL ed ex festività | 2 | 2 | 0 | 0 |
| C19 TFR liquidato | 3 | 3 | 0 | 0 |

**Su alterazioni casuali.** 1.100 prove: una voce a caso di un cedolino corretto, cambiata di un importo a caso. La tabella dice quante volte almeno un controllo se ne accorge.

| Voce alterata | ± 0,005 € | ± 0,02 € | ± 1,00 € | ± 10,00 € | ± 100,00 € |
|---|---:|---:|---:|---:|---:|
| tabellare | 14% | 100% | 100% | 100% | 100% |
| scatti | 22% | 100% | 100% | 100% | 100% |
| superminimo | 12% | 100% | 100% | 100% | 100% |
| straordinari | 0% | 100% | 100% | 100% | 100% |
| lordo | 0% | 100% | 100% | 100% | 100% |
| contributi inps | 69% | 100% | 100% | 100% | 100% |
| irpef | 36% | 100% | 100% | 100% | 100% |
| altre trattenute | 0% | 100% | 100% | 100% | 100% |
| netto | 0% | 100% | 100% | 100% | 100% |
| quota tfr | 0% | 100% | 100% | 100% | 100% |
| ferie residuo | 0% | 100% | 100% | 100% | 100% |

*Sotto la tolleranza di un centesimo l'alterazione si confonde con un arrotondamento, ed è giusto che passi. Sopra, la trovano tutte: 100%. Per le ferie l'importo è in giorni.*

**Perché regole e non un modello statistico.** Un rilevatore che non sa nulla del contratto confronta ogni cedolino con gli altri dello stesso cliente su quattro rapporti (contributi su lordo, TFR su retribuzione ordinaria, netto su lordo, netto sul mese prima) e segnala chi si allontana dalla mediana. Sugli stessi errori:

| Metodo | Cedolini sbagliati | Trovati | Falsi allarmi | Precisione |
|---|---:|---:|---:|---:|
| Statistico, z oltre 3 | 42 | 16 | 10 | 62% |
| Statistico, z oltre 3,5 | 42 | 15 | 5 | 75% |
| Statistico, z oltre 5 | 42 | 13 | 4 | 76% |
| Regole (C01-C19) | 42 | 42 | 0 | 100% |

*Il rilevatore confronta ogni cedolino con quelli dello stesso cliente, perché posizioni INPS diverse non sono anomalie. Vede solo gli errori che spostano un rapporto (contributi, TFR, netto, variazioni del netto); minimi, scatti, ferie, codice fiscale, anagrafica, assenze e permessi richiedono di conoscere il contratto e le regole INPS, e lì non trova nulla. I cedolini di uscita li segnala tutti, giusti o sbagliati, perché il netto salta rispetto al mese prima: così prende anche gli errori di cessazione, ma i cedolini di uscita corretti diventano falsi allarmi. Su un dominio scritto in regole, le regole vincono; la statistica serve dove una regola non c'è.*

**Il limite, e come C10 lo restringe.** Un errore coerente passa i controlli aritmetici: il dipendente A003 è assunto al 4° livello; inserito al 5° e ricalcolato da capo, il cedolino torna in ogni voce e prende 80,04 € netti in meno al mese. Se l'errore nasce da un cambio rispetto al mese prima, senza un evento che lo spieghi, lo trova C10: i due errori di anagrafica inseriti (un livello, un superminimo azzerato) sono segnalati. Resta invisibile solo se è sbagliato fin dall'assunzione: lì serve il confronto con i documenti del cliente, lettera di assunzione e mansioni.

## 5. Come lo userei in un team payroll

1. **Prima dell'invio, ogni mese:** l'export del software paghe entra nello script o nel foglio; si guardano solo le righe segnalate, a partire dalla priorità alta.
2. **C07 diventa una domanda al cliente,** non un errore: se lo straordinario c'è, si registra l'evento e il mese dopo non torna.
3. **Prima di ogni tranche contrattuale:** la tabella di novembre dice al cliente quanto costa l'aumento e chi assorbe, prima del cedolino e non dopo.
4. **Il passo successivo** è collegarlo all'export reale e misurare quante segnalazioni sono giuste nei primi due mesi, per tarare la soglia di C07.

## 6. Metodo e limiti

- **Due motori, una risposta.** Gli stessi controlli sono in Python e in formule nel foglio; il foglio Riconciliazione confronta ogni formula con Python, e la CI ricalcola il foglio con LibreOffice.
- **Contributi semplificati.** Un'aliquota a carico del dipendente (9,19%) per tutti, senza FIS, CIGS e contributo aggiuntivo dell'1%: in uso reale l'aliquota viene dalla posizione INPS del cliente.
- **Scatti al livello attuale.** Il CCNL non rivaluta gli scatti già maturati con il passaggio di livello: chi ha cambiato livello va controllato a mano.
- **Un CCNL, un mese.** Malattia, permessi, conguagli e il TFR pagato all'uscita non sono controllati; di chi esce si controllano ratei, mensilità aggiuntive, ferie non godute e preavviso (C11–C14).

