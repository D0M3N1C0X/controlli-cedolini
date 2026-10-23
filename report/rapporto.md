# Controlli sui cedolini di settembre 2026

**Perimetro:** 3 clienti con il CCNL Terziario Confcommercio, 122 cedolini di settembre confrontati con quelli di agosto e con gli F24
**Dati:** Clienti e dipendenti inventati, con errori inseriti apposta; minimi e scatti del CCNL reali, con le fonti in [docs/fonti.md](../docs/fonti.md)
**Strumenti:** Uno script Python, lo stesso controllo in un [foglio di calcolo](../deliverables/foglio_controllo_cedolini.xlsx) e uno [strumento nel browser](https://d0m3n1c0x.github.io/controlli-cedolini/strumento/) dove i file restano sul computer

> Quattordici controlli da passare prima di mandare i cedolini al cliente. I controlli ricalcolano ogni voce dalle regole del contratto, o la confrontano con il mese prima e con l'F24: non serve sapere come l'ha calcolata il software paghe. Non è consulenza del lavoro.

## In sintesi

- **35 segnalazioni: 34 cedolini e 1 F24**, 24 ad alta priorità; cliente A 7, cliente B 21, cliente C 7.
- **6 dipendenti sono pagati sotto il minimo:** il tabellare è fermo alla tranche di marzo 2025. Mancano 175,44 € al mese in tutto, più gli arretrati da novembre 2025.
- **L'F24 del cliente C ha 212,40 € di ritenute in meno** della somma dei cedolini: va integrato prima della scadenza del versamento.
- **Dal 1° novembre 2026 i minimi salgono:** 3.792,05 € al mese per 117 dipendenti. Il superminimo assorbibile ne copre 1.385,82 € in 42 casi; restano 2.406,23 € al mese, 33.687 € l'anno su 14 mensilità.
- **I controlli trovano ogni alterazione sopra il centesimo** in 885 prove casuali (sezione 4). Un errore coerente lo vedono solo se nasce da un cambio rispetto al mese prima (C10).

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
| A003 | A | C03 | alta | 182,15 € | 188,09 € | 5,94 € |
| A012 | A | C03 | alta | 139,04 € | 143,58 € | 4,54 € |
| B087 | B | C03 | alta | 125,63 € | 129,73 € | 4,10 € |
| C098 | C | C03 | alta | 198,87 € | 205,36 € | 6,49 € |
| B033 | B | C04 | media | 194,92 € | 171,27 € | −23,65 € |
| B059 | B | C04 | media | 179,38 € | 171,27 € | −8,11 € |
| C101 | C | C04 | media | 157,22 € | 143,28 € | −13,94 € |
| A009 | A | C05 | media | 22,96 gg | 20,79 gg | -2,17 gg |
| B055 | B | C05 | media | 13,40 gg | 11,23 gg | -2,17 gg |
| B084 | B | C05 | media | 17,97 gg | 15,80 gg | -2,17 gg |
| A001 | A | C06 | alta | 1.310,00 € | 1.347,50 € | 37,50 € |
| C093 | C | C06 | alta | 1.528,20 € | 1.628,20 € | 100,00 € |
| B090 | B | C07 | media | 1.752,08 € | 2.374,82 € | 622,74 € |
| C099 | C | C07 | media | 1.467,12 € | 2.045,04 € | 577,92 € |
| F24 | C | C08 | alta | 7.214,66 € | 7.002,26 € | −212,40 € |
| B058 | B | C09 | alta | valido | `GFZPLG92P01Z321A` | - |
| C107 | C | C09 | alta | valido | `ZCCGMF94M55Z282A` | - |
| B070 | B | C10 | alta | superminimo 150 | superminimo 0 | - |
| C100 | C | C10 | alta | livello 4 | livello 5 | - |
| B034 | B | C11 | media | 13ª 7; 14ª 3 | 13ª 8; 14ª 3 | - |
| B040 | B | C11 | media | 13ª 9; 14ª 3 | 13ª 9; 14ª 9 | - |
| B079 | B | C11 | media | 13ª 9; 14ª 3 | 13ª 8; 14ª 3 | - |
| B092 | B | C12 | alta | 452,38 € | 1.357,13 € | 904,75 € |
| A011 | A | C13 | alta | 2.148,97 € | 1.862,44 € | −286,53 € |
| B045 | B | C14 | alta | 20 gg | 10 gg | -10 gg |

**Cosa fare, per controllo**

| Controllo | Cosa fare |
|---|---|
| C01 Minimo tabellare | Aggiornare il tabellare al minimo in vigore e pagare la differenza dei mesi arretrati |
| C02 Scatti di anzianità | Inserire lo scatto maturato e verificare la data di decorrenza |
| C03 Contributi INPS | Correggere l'aliquota nella posizione del dipendente |
| C04 Quota TFR | Ricalcolare il rateo includendo scatti e superminimo |
| C05 Residuo ferie | Riallineare il residuo: maturazione del mese non registrata |
| C06 Quadratura | Ricontrollare le voci: il cedolino non quadra |
| C07 Variazione del netto | Chiedere al cliente l'evento che giustifica la variazione |
| C08 Riconciliazione F24 | Integrare la delega prima della scadenza del versamento |
| C09 Codice fiscale | Correggere il codice fiscale in anagrafica |
| C10 Anagrafica | Verificare il cambio con il cliente e con i documenti: se non c'è stato, correggere l'anagrafica |
| C11 Ratei 13ª e 14ª | Ricontare i dodicesimi dalla data di assunzione e correggere i ratei prima della tredicesima di dicembre |
| C12 Tredicesima e quattordicesima pagate | Ricalcolare la mensilità con i dodicesimi giusti, da gennaio per la tredicesima e da luglio per la quattordicesima, e pagare la differenza |
| C13 Ferie non godute | Ricalcolare le ferie non godute a 1/26 della retribuzione mensile per giorno e pagare la differenza |
| C14 Preavviso | Verificare la data della lettera: se il preavviso non è stato lavorato tutto, va pagata l'indennità sostitutiva per i giorni mancanti |

*C07 non dice che il cedolino è sbagliato: dice che il netto è cambiato di oltre il 20% senza un evento registrato. Le assunzioni del mese, gli straordinari dichiarati e il passaggio a part-time non sono segnalati.*

## 2. F24 contro cedolini

| Cliente | Ritenute in F24 (1001) | Ritenute nei cedolini | Differenza | Contributi in F24 | Contributi nei cedolini | Differenza |
|---|---:|---:|---:|---:|---:|---:|
| A | 5.754,05 € | 5.754,05 € | 0,00 € | 3.417,42 € | 3.417,42 € | 0,00 € |
| B | 20.771,00 € | 20.771,00 € | 0,00 € | 13.566,61 € | 13.566,61 € | 0,00 € |
| C | 7.002,26 € | 7.214,66 € | −212,40 € | 4.745,96 € | 4.745,96 € | 0,00 € |

*Le ritenute IRPEF dei dati sintetici non sono calcolate con le regole fiscali: servono solo a mostrare la riconciliazione.*

## 3. La tranche del 1° novembre 2026

Il rinnovo del CCNL Terziario del 22 marzo 2024 alza i minimi a novembre 2026 e di nuovo a febbraio 2027. Per ogni dipendente: l'aumento del livello, riproporzionato al part-time; quanto ne assorbe il superminimo, se la lettera di assunzione lo dice assorbibile; quanto resta da pagare.

| Cliente | Dipendenti | Aumento al mese | Assorbito | Da pagare al mese | Costo annuo (14 mensilità) |
|---|---:|---:|---:|---:|---:|
| Cliente A | 17 | 530,41 € | 242,65 € | 287,76 € | 4.029 € |
| Cliente B | 74 | 2.420,10 € | 839,56 € | 1.580,54 € | 22.128 € |
| Cliente C | 26 | 841,54 € | 303,61 € | 537,93 € | 7.531 € |

*Lordo dipendente, senza i contributi a carico dell'azienda. L'assorbibilità del superminimo dipende dalla lettera di assunzione e dagli accordi aziendali: va verificata dipendente per dipendente prima di comunicarla.*

## 4. Quanto ci si può fidare dei controlli

**Sugli errori inseriti.** 35 su 35, nessun falso allarme. Dimostra che i controlli fanno quello che dicono, non che troverebbero errori reali: gli errori li ho scelti io.

| Controllo | Errori inseriti | Trovati | Mancati | Falsi allarmi |
|---|---:|---:|---:|---:|
| C01 Minimo tabellare | 6 | 6 | 0 | 0 |
| C02 Scatti di anzianità | 4 | 4 | 0 | 0 |
| C03 Contributi INPS | 4 | 4 | 0 | 0 |
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

**Su alterazioni casuali.** 1.100 prove: una voce a caso di un cedolino corretto, cambiata di un importo a caso. La tabella dice quante volte almeno un controllo se ne accorge.

| Voce alterata | ± 0,005 € | ± 0,02 € | ± 1,00 € | ± 10,00 € | ± 100,00 € |
|---|---:|---:|---:|---:|---:|
| tabellare | 0% | 100% | 100% | 100% | 100% |
| scatti | 0% | 100% | 100% | 100% | 100% |
| superminimo | 0% | 100% | 100% | 100% | 100% |
| straordinari | 17% | 100% | 100% | 100% | 100% |
| lordo | 0% | 100% | 100% | 100% | 100% |
| contributi inps | 59% | 100% | 100% | 100% | 100% |
| irpef | 5% | 100% | 100% | 100% | 100% |
| altre trattenute | 0% | 100% | 100% | 100% | 100% |
| netto | 0% | 100% | 100% | 100% | 100% |
| quota tfr | 0% | 100% | 100% | 100% | 100% |
| ferie residuo | 0% | 100% | 100% | 100% | 100% |

*Sotto la tolleranza di un centesimo l'alterazione si confonde con un arrotondamento, ed è giusto che passi. Sopra, la trovano tutte: 100%. Per le ferie l'importo è in giorni.*

**Perché regole e non un modello statistico.** Un rilevatore che non sa nulla del contratto confronta ogni cedolino con gli altri su quattro rapporti (contributi su lordo, TFR su retribuzione ordinaria, netto su lordo, netto sul mese prima) e segnala chi si allontana dalla mediana. Sugli stessi errori:

| Metodo | Cedolini sbagliati | Trovati | Falsi allarmi | Precisione |
|---|---:|---:|---:|---:|
| Statistico, z oltre 3 | 34 | 13 | 10 | 57% |
| Statistico, z oltre 3,5 | 34 | 12 | 6 | 67% |
| Statistico, z oltre 5 | 34 | 10 | 2 | 83% |
| Regole (C01-C14) | 34 | 34 | 0 | 100% |

*Il rilevatore vede solo gli errori che spostano un rapporto (contributi, TFR, variazioni del netto); minimi, scatti, ferie, codice fiscale e anagrafica richiedono di conoscere il contratto, e lì non trova nulla. I cedolini di uscita li segnala tutti, giusti o sbagliati, perché il netto salta rispetto al mese prima: così prende anche gli errori di cessazione, ma i cedolini di uscita corretti diventano falsi allarmi. Su un dominio scritto in regole, le regole vincono; la statistica serve dove una regola non c'è.*

**Il limite, e come C10 lo restringe.** Un errore coerente passa i controlli aritmetici: il dipendente A010 è assunto al 4° livello; inserito al 5° e ricalcolato da capo, il cedolino torna in ogni voce e prende 61,29 € netti in meno al mese. Se l'errore nasce da un cambio rispetto al mese prima, senza un evento che lo spieghi, lo trova C10: i due errori di anagrafica inseriti (un livello, un superminimo azzerato) sono segnalati. Resta invisibile solo se è sbagliato fin dall'assunzione: lì serve il confronto con i documenti del cliente, lettera di assunzione e mansioni.

## 5. Come lo userei in un team payroll

1. **Prima dell'invio, ogni mese:** l'export del software paghe entra nello script o nel foglio; si guardano solo le righe segnalate, a partire dalla priorità alta.
2. **C07 diventa una domanda al cliente,** non un errore: se lo straordinario c'è, si registra l'evento e il mese dopo non torna.
3. **Prima di ogni tranche contrattuale:** la tabella di novembre dice al cliente quanto costa l'aumento e chi assorbe, prima del cedolino e non dopo.
4. **Il passo successivo** è collegarlo all'export reale e misurare quante segnalazioni sono giuste nei primi due mesi, per tarare la soglia di C07.

## 6. Metodo e limiti

- **Due motori, una risposta.** Gli stessi controlli sono in Python e in formule nel foglio; il foglio Riconciliazione confronta ogni formula con Python, e la CI ricalcola il foglio con LibreOffice.
- **Contributi semplificati.** Un'aliquota a carico del dipendente (9,19%) per tutti, senza FIS, CIGS e contributo aggiuntivo dell'1%: in uso reale l'aliquota viene dalla posizione INPS del cliente.
- **Scatti al livello attuale.** Il CCNL non rivaluta gli scatti già maturati con il passaggio di livello: chi ha cambiato livello va controllato a mano.
- **Un CCNL, un mese.** Tredicesima, quattordicesima, malattia, cessazioni e conguagli non sono controllati.

