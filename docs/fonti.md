# Fonti e verifiche

Ogni regola che i controlli applicano, da dove viene e quanto è stata verificata. Controllato il
**6 ottobre 2026**, minimi e contributi ricontrollati sulle fonti primarie il **9 ottobre 2026**; le regole F14-F23
lette il **6 novembre 2026**. Non è consulenza del lavoro.

**Stato**

- **Primaria**: letta nel testo ufficiale, o nel documento di una parte firmataria o dell'ente che fissa la regola.
- **Fonti concordi**: due o più fonti secondarie indipendenti dicono la stessa cosa.
- **Conoscenza generale**: regola nota del sistema paghe, non ricontrollata in questa sessione.
- **Scelta**: una decisione del modello, con il suo motivo.

| # | Regola | Fonte | Stato |
|---|---|---|---|
| F01 | Minimi mensili del CCNL Terziario Confcommercio per livello (paga base + altri elementi + contingenza ed EDR), tranche di marzo 2025, novembre 2025, novembre 2026 e febbraio 2027 | [Confcommercio, circolare n. 16 del 29 marzo 2024](https://www.dottrinalavoro.it/wp-content/uploads/2024/04/Confcommercio-chiarimenti-operativi-Rinnovo-del-CCNL-e-Accordo-Integrativo-del-28-marzo-2024.pdf), chiarimenti operativi sul rinnovo del 22 marzo 2024 e sull'accordo integrativo del 28 marzo 2024: tabella "Paga base dal 1/3/2025" (p. 8) più gli aumenti per tranche dell'art. 213 (p. 7). I valori di `data/ccnl_terziario.csv` sono ricostruiti così, al centesimo | Primaria (parte firmataria) |
| F02 | "Altri elementi" compresi nel minimo: 260,76 € per i Quadri, 5,16 € al 7° livello; nessuno negli altri livelli | Stessa circolare, colonna "Altri el." delle tabelle di p. 8 | Primaria (parte firmataria) |
| F03 | Scatti: 10 trienni, dal primo giorno del mese successivo al triennio; importi mensili Quadri 25,46 €, 1° 24,84, 2° 22,83, 3° 21,95, 4° 20,66, 5° 20,30, 6° 19,73, 7° 19,47 | [Sintesi Filcams CGIL del CCNL Terziario](https://cgil-agb.it/images/Filcams/pdf/commercio/TERZIARIO_confcommercio.pdf) e [Lexplain](https://www.lexplain.it/scatti-di-anzianita-nel-contratto-commercio-come-cambia-lo-stipendio/): stessi importi | Fonti concordi |
| F04 | Ferie: 26 giorni lavorativi l'anno, per dodicesimi nell'anno di assunzione | Sintesi Filcams CGIL | Fonti concordi |
| F05 | Contributo IVS a carico del dipendente: 9,19% | Aliquota generale del Fondo pensioni lavoratori dipendenti; sotto il 10%, e per questo soggetta all'1% aggiuntivo di F15 (INPS, circ. 6/2026, § 5) | Conoscenza generale · coerente con la fonte primaria di F15 |
| F06 | TFR: quota annua pari alla retribuzione annua divisa per 13,5 | Art. 2120 del Codice civile | Conoscenza generale |
| F07 | Tredicesima e quattordicesima | Sintesi Filcams CGIL | Fonti concordi |
| F08 | Carattere di controllo del codice fiscale | DM 23 dicembre 1976; algoritmo verificato sull'esempio `RSSMRA85T10A562S` | Conoscenza generale |
| F09 | Ritenute su redditi di lavoro dipendente versate in F24 con codice tributo 1001 | Prassi Agenzia delle Entrate | Conoscenza generale |
| F10 | L'imponibile contributivo si espone in unità di euro e il contributo si arrotonda al centesimo (millesimi da 5 a 9 per eccesso): l'aliquota si applica all'imponibile arrotondato all'euro, 1.779,00 × 9,19% = 163,49 € | [INPS, Documento tecnico UniEmens individuale, versione 4.33 del 29/09/2026](https://www.inps.it/content/dam/inps-site/pdf/prestazioni-e-servizi/uniemens-aziende-private/UniEMENSind.pdf): importi interi e contributivi (p. 31), elemento `<Imponibile>` di `<DatiRetributivi>` (p. 52). Esempio di calcolo: [ODCEC Torino, "Conosci la tua busta paga?"](https://odcec.torino.it/public/pagine/slides.pdf), p. 24 | Primaria per il formato; il calcolo sull'imponibile arrotondato è prassi, confermata dall'esempio |
| F11 | Ratei di tredicesima e quattordicesima: per il servizio inferiore all'anno, tanti dodicesimi quanti i mesi interi di servizio; le frazioni di mese di almeno 15 giorni contano come mese intero. La tredicesima matura nell'anno solare e si paga alla vigilia di Natale; la quattordicesima si paga entro il 1° luglio sulla retribuzione al 30 giugno, quindi matura da luglio a giugno | [Sintesi Filcams CGIL del CCNL Terziario](https://cgil-agb.it/images/Filcams/pdf/commercio/TERZIARIO_confcommercio.pdf), p. 11, "Mensilità aggiuntive" e "Norme comuni" | Primaria (parte firmataria, sintesi) · il periodo luglio-giugno della quattordicesima è dedotto dalla data di pagamento |

| F12 | La quota giornaliera della retribuzione si ottiene dividendo la retribuzione mensile per 26; alla cessazione le ferie maturate e non godute si pagano con un'indennità sostitutiva, a quota giornaliera per giorno di residuo | [Sintesi Filcams CGIL del CCNL Terziario](https://cgil-agb.it/images/Filcams/pdf/commercio/TERZIARIO_confcommercio.pdf), p. 4, "Quota oraria e giornaliera", e p. 18, "Ferie" | Primaria (parte firmataria, sintesi) · l'indennità per le ferie non godute alla quota giornaliera è prassi, la sintesi non la scrive in formula |
| F13 | Preavviso in giorni di calendario, per livello e anni di servizio (fino a 5, dal 6° al 10°, oltre il 10°): dimissioni Quadri e 1° 45/60/90, 2° e 3° 20/30/45, 4° e 5° 15/20/30, 6° e 7° 10/15/15; licenziamento Quadri e 1° 60/90/120, 2° e 3° 30/45/60, 4° e 5° 20/30/45, 6° e 7° 15/20/20 | [Sintesi Filcams CGIL del CCNL Terziario](https://cgil-agb.it/images/Filcams/pdf/commercio/TERZIARIO_confcommercio.pdf), pp. 24-25, "Estinzione del rapporto · Preavviso" | Primaria (parte firmataria, sintesi) |

| F14 | FIS: contributo ordinario 0,50% per chi occupa in media fino a 5 dipendenti nel semestre di riferimento, 0,80% oltre, due terzi a carico del datore di lavoro e un terzo del lavoratore. CIGS: 0,90%, di cui 0,30% a carico del lavoratore, per i datori di lavoro del FIS con più di 15 dipendenti di media nel semestre (art. 20, c. 3-bis, D.lgs. 148/2015) | [INPS, circolare n. 76 del 30 giugno 2022](https://www.inps.it/content/dam/inps-site/it/scorporati/circolari-e-messaggi/2022/06/Circolare_13870/Allegati/15008_Circolare-numero-76-del-30-06-2022.pdf), §§ 4, 4.1, 6.1 | Primaria · la riduzione del 40% per chi resta fino a 5 dipendenti senza integrazioni da 24 mesi (circ. 5/2025) non è modellata |
| F15 | Aliquota aggiuntiva dell'1% a carico del lavoratore sulla retribuzione oltre la prima fascia pensionabile: 56.224,00 € l'anno nel 2026, mensilizzata 4.685,00 € | [INPS, circolare n. 6 del 30 gennaio 2026](https://www.inps.it/content/dam/inps-site/it/scorporati/circolari-e-messaggi/2026/01/Circolare_15151/Allegati/16546_Circolare-numero-6-del-30-01-2026.pdf), § 5 | Primaria |
| F16 | Indennità di malattia INPS: 50% della retribuzione media giornaliera dal 4° al 20° giorno, 66,66% dal 21° al 180°, per tutti i giorni coperti da certificato; anticipata dal datore di lavoro. CCNL Terziario: integrazione fino al 100%, 75% e 100% della retribuzione netta; quella dei primi 3 giorni al 100% per i primi 2 eventi dell'anno, 66% al 3°, 50% al 4°, niente dal 5°, salvo ricovero, prognosi iniziale di almeno 12 giorni, terapie salvavita e gravidanza | [INPS, scheda "Indennità di malattia"](https://www.inps.it/it/it/dettaglio-approfondimento.schede-informative.indennit--di-malattia-e-visite-mediche-di-controllo.html); [sintesi Filcams CGIL del CCNL Terziario](https://cgil-agb.it/images/Filcams/pdf/commercio/TERZIARIO_confcommercio.pdf), "Malattia" | Primaria per l'INPS · CCNL: parte firmataria, sintesi del rinnovo 2011 (vedi la nota sotto) |
| F17 | Retribuzione media globale giornaliera degli impiegati: retribuzione teorica del mese prima dell'inizio dell'evento, per il numero di mensilità diviso 12, divisa per 30 (esempio dell'INPS: 1.500 × 14/12 / 30 = 58,33 €) | [INPS, circolare n. 94 del 22 luglio 2009](https://servizi2.inps.it/servizi/Bussola/VisualizzaDoc.aspx?sVirtualURL=%2FCircolari%2FCircolare+numero+94+del+22-07-2009.htm), § A | Primaria · la retribuzione teorica è presa come tabellare, scatti e superminimo del mese prima |
| F18 | Indennità di maternità: 80% della retribuzione per tutto il congedo, con gli stessi criteri della malattia; il CCNL Terziario integra al 100% del netto per i primi 5 mesi | [D.lgs. 151/2001, art. 22](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2001-03-26;151~art22), c. 1-2; sintesi Filcams, "Maternità" | Primaria |
| F19 | Rivalutazione del TFR: tasso dell'1,5% annuo fisso più il 75% dell'aumento dell'indice ISTAT FOI rispetto a dicembre; per frazioni d'anno il mese conta dal 15 | Art. 2120 c.c.: il coefficiente ricostruito da F20 coincide al sesto decimale con quello pubblicato ([dottrinalavoro.it](https://www.dottrinalavoro.it/notizie-c/tfr-aggiornato-il-coefficiente-di-rivalutazione-per-il-mese-di-agosto-2026-2), finestre dal 15 al 14) | Fonti concordi · Normattiva non ha restituito il testo dell'articolo in questa sessione |
| F20 | Indici FOI senza tabacchi: dicembre 2025 121,5 (base 2015); agosto 2026 103,7 e settembre 2026 104,3 (base 2025); coefficiente di raccordo 1,214. Coefficienti TFR: agosto 3,710988%, settembre 4,285617% | ISTAT, comunicati definitivi [dicembre 2025](https://www.istat.it/wp-content/uploads/2026/01/CS_Prezzi-al-consumo_Def_Dic2025_rev2.pdf), [agosto 2026](https://www.istat.it/wp-content/uploads/2026/09/CS_Prezzi-al-consumo_Def_Agosto2026.pdf), [settembre 2026](https://www.istat.it/wp-content/uploads/2026/10/Prezzi-al-consumo-def-Set2026-1.pdf); [indice per le rivalutazioni monetarie](https://www.istat.it/notizia/indice-dei-prezzi-per-le-rivalutazioni-monetarie/) | Primaria |
| F21 | Imposta sostitutiva del 17% sulla rivalutazione del fondo TFR | D.lgs. 33/2025, testo unico versamenti e riscossione; l'art. 11, c. 3, D.lgs. 47/2000 che la prevedeva risulta abrogato su [Normattiva](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2000-02-18;47~art11) | Fonti concordi · l'articolo del testo unico non è stato individuato |
| F22 | Lo 0,50% della retribuzione imponibile, aggiunto ai contributi del datore di lavoro, si toglie dalla quota di TFR del periodo | [L. 297/1982, art. 3](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:1982-05-29;297~art3) | Primaria |
| F23 | Permessi: riduzione d'orario di 56 ore l'anno, 72 nelle aziende con più di 15 dipendenti, in gruppi di 4 o 8 ore; per chi è iscritto al libro unico dopo il 1° marzo 2011, al 50% dopo 2 anni e al 100% dopo 4; ex festività: 4 giornate (32 ore), per dodicesimi. Il part-time è riproporzionato | Sintesi Filcams, "Riduzione annua" ed "Ex festività"; [D.lgs. 81/2015, art. 7, c. 2](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2015-06-15;81~art7) | Primaria (parte firmataria, sintesi del 2011) · part-time: Primaria |

**Le sintesi Filcams sono del rinnovo 2011-2013.** F03, F04, F07, F11-F13, F16, F18 e F23 vengono dalla sintesi
del CCNL 2011-2013 pubblicata dalla Filcams. La [circolare Confcommercio n. 16/2024](https://www.dottrinalavoro.it/wp-content/uploads/2024/04/Confcommercio-chiarimenti-operativi-Rinnovo-del-CCNL-e-Accordo-Integrativo-del-28-marzo-2024.pdf)
elenca gli articoli cambiati dal rinnovo del 2024 (artt. 4, 16, 16 bis, 23, 39, 71 bis, 75, 95, 104, 115, 171 bis,
198, 213, 216, 258, 259): malattia, maternità, permessi, scatti, mensilità e preavviso non ci sono. Il rinnovo del
2015 non è stato riletto: il testo vigente va confrontato con l'archivio del CNEL prima dell'uso su dati veri.

## Prima di usarlo su dati veri

- **Ricontrollare F03 (scatti) sul testo del CCNL**: gli importi vengono da due fonti secondarie concordi.
  I minimi (F01, F02) sono invece ricostruiti al centesimo dalla circolare Confcommercio del 29 marzo 2024.
- **La media dei dipendenti nel semestre va presa dalla posizione INPS del cliente**: decide CIGS e FIS
  (F14). Non sono modellati la riduzione del FIS per i piccoli datori di lavoro, i fondi bilaterali diversi
  dal FIS e gli esoneri contributivi.
- **Confrontare malattia, maternità e permessi con il testo vigente del CCNL** (vedi la nota sulle sintesi
  Filcams), e aggiungere ai Parametri l'indice FOI di ogni mese in cui c'è una cessazione.
- **L'assorbibilità del superminimo** dipende dalla lettera di assunzione e dagli accordi aziendali.

## Scelte del modello

| # | Scelta | Motivo |
|---|---|---|
| S01 | Tolleranza di un centesimo su ogni importo | Gli arrotondamenti dei software paghe differiscono al centesimo |
| S02 | Soglia del 20% sulla variazione del netto | Da tarare sui primi mesi di uso reale |
| S03 | Rateo TFR mensile = retribuzione ordinaria × 14 / 13,5 / 12 | Accantonamento mensile che include tredicesima e quattordicesima |
| S04 | Scatti valorizzati al livello attuale | Il CCNL non rivaluta gli scatti già maturati con il passaggio di livello: chi ha cambiato livello va controllato a mano |
| S05 | Arrotondamento al centesimo come ROUND di Excel, metà per eccesso | Python e foglio di calcolo devono dare lo stesso risultato |
| S06 | C10 confronta livello, part-time, superminimo e data di assunzione con il mese prima; un cambio senza evento è una segnalazione | Un errore coerente spesso nasce da un cambio di anagrafica: il cedolino torna, ma il dato è cambiato senza motivo |
| S07 | Gli anni per la regola dei permessi dei nuovi assunti (2 e 4) si contano all'ultimo giorno del mese | Il CCNL dice "decorsi 2 anni dall'assunzione" senza dire come si tratta il mese in cui scadono: il mese che li compie matura alla nuova misura |

## Correzioni

- **6 novembre 2026, contributi reali.** C03 usava il 9,19% per tutti, e l'errore inserito nei dati di esempio era
  un 9,49%: per un cliente del commercio con più di 15 dipendenti di media l'aliquota giusta è 9,7567% (IVS, CIGS e
  un terzo del FIS, F14), quindi il 9,49% era più vicino al vero del valore considerato corretto. Ora l'aliquota è
  per posizione, con l'1% oltre la prima fascia (F15), e gli errori inseriti sono quelli veri: CIGS e FIS non
  trattenuti, CIGS trattenuta sotto i 15 dipendenti, 1% dimenticato.
- **6 novembre 2026, fonti del CCNL.** Le sintesi Filcams usate per scatti, ratei, quota giornaliera e preavviso sono
  del rinnovo 2011-2013, non del CCNL vigente: segnalato sopra, con gli articoli che il rinnovo 2024 ha cambiato.
- **6 novembre 2026, assenze, permessi e TFR.** Aggiunti C15-C19 (F16-F23), con cinque decisioni (D21-D25).

- **23 ottobre 2026, revisione indipendente.** Una revisione a più mani ha trovato e fatto correggere:
  il foglio non contava C01, C02 e C14 se il livello era incollato come numero (ora lo cerca come testo e,
  se manca dal CCNL, segna ERRORE come Python); C11 e C12 contavano in modo diverso i dodicesimi di chi lascia
  prima del 15 (ora entrambi fino alla data di uscita); C12 segnalava una quattordicesima giusta pagata a luglio
  (ora è quella del periodo chiuso il 30 giugno); lo strumento nel browser leggeva male i CSV con punto e virgola
  e decimali col punto, le matricole numeriche, il part-time in percentuale e alcuni formati del mese. Aggiunta
  un'uscita corretta a metà mese nei dati di esempio, per tenere provati questi casi.

- **23 ottobre 2026, cessazioni.** Aggiunti C12 (F11), C13 (F12) e C14 (F13): tredicesima e quattordicesima
  pagate, ferie non godute e preavviso. Cinque cessazioni nei dati di esempio, tre con un errore inserito.

- **12 ottobre 2026, ratei.** Aggiunto C11 (F11). I file modello dello strumento nel browser avevano ancora
  i contributi di prima della correzione F10: ora sono generati dai dati.

- **9 ottobre 2026, minimi.** Il confronto con la circolare Confcommercio n. 16/2024 ha trovato tre differenze
  rispetto alle fonti secondarie usate prima: ai Quadri mancavano gli "altri elementi" di 260,76 € al mese;
  contingenza ed EDR di Quadri, 1° e 2° livello erano sbagliate di 1-2 centesimi; il 6° livello di febbraio 2027
  di un centesimo. Tabella ricostruita dalla fonte primaria, dati e risultati rigenerati.
- **9 ottobre 2026, contributi.** C03 applicava l'aliquota al lordo al centesimo; ora all'imponibile arrotondato
  all'euro (F10). Su cedolini veri la versione precedente avrebbe dato falsi allarmi di pochi centesimi.

