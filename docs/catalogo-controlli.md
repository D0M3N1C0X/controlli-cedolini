# Catalogo dei controlli

Una scheda per controllo: cosa controlla, da quale regola, dove sta nel foglio, un esempio vero e cosa fare. Generato da `src/build_catalogo.py`: nome, priorità, formule ed esempi vengono dal codice e dal foglio, quindi non restano indietro.

| Controllo | Priorità | Cosa controlla |
|---|---|---|
| [C01 · Minimo tabellare](#c01--minimo-tabellare) | alta | Tabellare diverso dal minimo del livello (paga base, altri elementi, contingenza), part-time compreso |
| [C02 · Scatti di anzianità](#c02--scatti-di-anzianità) | alta | Importo degli scatti diverso da quelli maturati dalla data di assunzione |
| [C03 · Contributi INPS](#c03--contributi-inps) | alta | Contributo a carico del dipendente diverso da imponibile arrotondato all'euro × aliquota |
| [C04 · Quota TFR](#c04--quota-tfr) | media | Rateo TFR diverso da retribuzione ordinaria × 14 / 13,5 / 12 |
| [C05 · Residuo ferie](#c05--residuo-ferie) | media | Residuo diverso da residuo del mese prima + maturate - godute |
| [C06 · Quadratura](#c06--quadratura) | alta | Lordo diverso dalla somma delle voci, o netto diverso da lordo meno trattenute |
| [C07 · Variazione del netto](#c07--variazione-del-netto) | media | Netto oltre il 20% sopra o sotto il mese prima, senza un evento che lo spieghi |
| [C08 · Riconciliazione F24](#c08--riconciliazione-f24) | alta | Ritenute o contributi in F24 diversi dalla somma dei cedolini del cliente |
| [C09 · Codice fiscale](#c09--codice-fiscale) | alta | Carattere di controllo non valido |
| [C10 · Anagrafica](#c10--anagrafica) | alta | Livello, part-time, superminimo o data di assunzione diversi dal mese prima, senza un evento |
| [C11 · Ratei 13ª e 14ª](#c11--ratei-13ª-e-14ª) | media | Dodicesimi maturati diversi dai mesi di servizio nel periodo (frazione di 15 giorni intera) |
| [C12 · Tredicesima e quattordicesima pagate](#c12--tredicesima-e-quattordicesima-pagate) | alta | Importo diverso dalla retribuzione mensile per i dodicesimi maturati, a dicembre o alla cessazione |
| [C13 · Ferie non godute](#c13--ferie-non-godute) | alta | Alla cessazione, ferie residue pagate diversamente da 1/26 della retribuzione mensile al giorno |
| [C14 · Preavviso](#c14--preavviso) | alta | Alla cessazione, giorni di preavviso sotto il minimo del CCNL per livello e anni di servizio |

## C01 · Minimo tabellare

**Priorità alta.** Tabellare diverso dal minimo del livello (paga base, altri elementi, contingenza), part-time compreso.

**La regola.** Il tabellare è il minimo del livello in vigore (paga base, altri elementi, contingenza ed EDR) per la percentuale di part-time, arrotondato al centesimo.

**Fonti.** [F01](fonti.md), [F02](fonti.md).

**Nel foglio** (foglio Mese, riga 5; le altre righe sono uguali):

```
X  Tabellare atteso
    =IF($A5="","",IFERROR(ROUND(INDEX(CCNL!$F$5:$F$12,MATCH(D5&"",CCNL!$A$5:$A$12,0))*F5,2),""))
AK  C01 Minimo
    =IF($A5="","",IF(ISNUMBER(X5),IF(ABS(I5-X5)>Parametri!$C$11,"ERRORE","OK"),"ERRORE"))
```

**Un esempio dal mese di settembre 2026.** Dipendente B031, cliente B: atteso 890,84 €, sul cedolino 873,34 €, differenza −17,50 €.

**Cause tipiche.**

- La tranche del CCNL non è stata caricata nel software paghe.
- Livello sbagliato in anagrafica.
- Part-time non riproporzionato, o riproporzionato due volte.

**Cosa fare.** Aggiornare il tabellare al minimo in vigore e pagare la differenza dei mesi arretrati.

**Limiti.**

- Non controlla il superminimo né il suo assorbimento: quello è nel foglio Novembre 2026.
- Vale per il CCNL Terziario Confcommercio: un altro contratto richiede la sua tabella.

## C02 · Scatti di anzianità

**Priorità alta.** Importo degli scatti diverso da quelli maturati dalla data di assunzione.

**La regola.** Uno scatto per ogni triennio dalla data di assunzione, in pagamento dal mese dopo il compimento, fino a 10; l'importo è quello del livello per il numero di scatti e per il part-time.

**Fonti.** [F03](fonti.md), [S04](fonti.md).

**Nel foglio** (foglio Mese, riga 5; le altre righe sono uguali):

```
Y  Mesi di servizio
    =IF($A5="","",(YEAR(Parametri!$C$5)*12+MONTH(Parametri!$C$5))-(YEAR(E5)*12+MONTH(E5)))
Z  Scatti attesi
    =IF($A5="","",MIN(Parametri!$C$13,MAX(0,INT((Y5-1)/36))))
AA  Importo scatti atteso
    =IF($A5="","",IFERROR(ROUND(INDEX(CCNL!$I$5:$I$12,MATCH(D5&"",CCNL!$A$5:$A$12,0))*Z5*F5,2),""))
AL  C02 Scatti
    =IF($A5="","",IF(ISNUMBER(AA5),IF(ABS(K5-AA5)>Parametri!$C$11,"ERRORE","OK"),"OK"))
```

**Un esempio dal mese di settembre 2026.** Dipendente A007, cliente A: atteso 49,68 €, sul cedolino 24,84 €, differenza −24,84 €.

**Cause tipiche.**

- Scatto maturato e non attivato nel software.
- Data di assunzione sbagliata in anagrafica.
- Scatti rimasti al livello precedente dopo un passaggio.

**Cosa fare.** Inserire lo scatto maturato e verificare la data di decorrenza.

**Limiti.**

- Valorizza tutti gli scatti al livello attuale (S04): chi ha cambiato livello va controllato a mano.
- Non considera anzianità convenzionali o periodi non utili alla maturazione.

## C03 · Contributi INPS

**Priorità alta.** Contributo a carico del dipendente diverso da imponibile arrotondato all'euro × aliquota.

**La regola.** Il contributo IVS a carico del dipendente è l'imponibile arrotondato all'euro per l'aliquota (9,19% se il cliente non ne indica un'altra), arrotondato al centesimo.

**Fonti.** [F05](fonti.md), [F10](fonti.md).

**Nel foglio** (foglio Mese, riga 5; le altre righe sono uguali):

```
AB  Contributi attesi
    =IF($A5="","",ROUND(ROUND(N5,0)*Parametri!$C$6,2))
AM  C03 INPS
    =IF($A5="","",IF(ABS(O5-AB5)>Parametri!$C$11,"ERRORE","OK"))
```

**Un esempio dal mese di settembre 2026.** Dipendente A003, cliente A: atteso 182,15 €, sul cedolino 188,09 €, differenza 5,94 €.

**Cause tipiche.**

- Aliquota della posizione INPS sbagliata, per esempio 9,49% dove non c'è CIGS.
- Imponibile non arrotondato all'euro, o arrotondato due volte.

**Cosa fare.** Correggere l'aliquota nella posizione del dipendente.

**Limiti.**

- Un'aliquota per tutto il cliente: FIS, CIGS e il contributo aggiuntivo dell'1% non sono modellati.
- L'imponibile è il lordo: voci escluse dall'imponibile non sono gestite.

## C04 · Quota TFR

**Priorità media.** Rateo TFR diverso da retribuzione ordinaria × 14 / 13,5 / 12.

**La regola.** Il rateo mensile di TFR è la retribuzione ordinaria (tabellare, scatti, superminimo) per 14 mensilità, diviso 13,5 e diviso 12.

**Fonti.** [F06](fonti.md), [S03](fonti.md).

**Nel foglio** (foglio Mese, riga 5; le altre righe sono uguali):

```
AC  TFR atteso
    =IF($A5="","",ROUND((I5+K5+L5)*Parametri!$C$8/Parametri!$C$7/12,2))
AN  C04 TFR
    =IF($A5="","",IF(ABS(T5-AC5)>Parametri!$C$11,"ERRORE","OK"))
```

**Un esempio dal mese di settembre 2026.** Dipendente B033, cliente B: atteso 194,92 €, sul cedolino 171,27 €, differenza −23,65 €.

**Cause tipiche.**

- Base del TFR senza scatti o superminimo.
- Divisore o numero di mensilità sbagliati nella configurazione.

**Cosa fare.** Ricalcolare il rateo includendo scatti e superminimo.

**Limiti.**

- Non include voci variabili non occasionali né la rivalutazione del fondo.
- Non sottrae il contributo dello 0,50% al Fondo pensioni lavoratori dipendenti.

## C05 · Residuo ferie

**Priorità media.** Residuo diverso da residuo del mese prima + maturate - godute.

**La regola.** Il residuo ferie è il residuo del mese prima più un dodicesimo dei 26 giorni annui, meno le ferie godute nel mese, a quattro decimali.

**Fonti.** [F04](fonti.md).

**Nel foglio** (foglio Mese, riga 5; le altre righe sono uguali):

```
AD  Residuo mese prima
    =IF($A5="","",IFERROR(INDEX('Mese precedente'!$D$5:$D$254,MATCH(A5,'Mese precedente'!$A$5:$A$254,0)),0))
AE  Residuo atteso
    =IF($A5="","",ROUND(AD5+ROUND(Parametri!$C$9/12,4)-V5,4))
AO  C05 Ferie
    =IF($A5="","",IF(ABS(W5-AE5)>Parametri!$C$12,"ERRORE","OK"))
```

**Un esempio dal mese di settembre 2026.** Dipendente A009, cliente A: residuo atteso 22,9553 giorni, sul cedolino 20,7886.

**Cause tipiche.**

- Maturazione del mese non registrata.
- Ferie godute non scaricate dal residuo.

**Cosa fare.** Riallineare il residuo: maturazione del mese non registrata.

**Limiti.**

- Ferie in giorni, non in ore; ROL ed ex festività non sono gestiti.
- Per chi è assunto nel mese il residuo di partenza è zero.

## C06 · Quadratura

**Priorità alta.** Lordo diverso dalla somma delle voci, o netto diverso da lordo meno trattenute.

**La regola.** Il lordo è la somma di tabellare, scatti, superminimo e straordinari; il netto è il lordo meno contributi, IRPEF e altre trattenute.

**Fonti.** [S01](fonti.md).

**Nel foglio** (foglio Mese, riga 5; le altre righe sono uguali):

```
AF  Lordo atteso
    =IF($A5="","",ROUND(I5+K5+L5+M5+N(BC5)+N(BD5)+N(BE5),2))
AG  Netto atteso
    =IF($A5="","",ROUND(N5-O5-Q5-R5,2))
AP  C06 Quadratura
    =IF($A5="","",IF(OR(ABS(N5-AF5)>Parametri!$C$11,ABS(S5-AG5)>Parametri!$C$11),"ERRORE","OK"))
```

**Un esempio dal mese di settembre 2026.** Dipendente A001, cliente A: atteso 1.310,00 €, sul cedolino 1.347,50 €, differenza 37,50 €.

**Cause tipiche.**

- Una voce aggiunta a mano e non sommata.
- Una trattenuta inserita due volte.

**Cosa fare.** Ricontrollare le voci: il cedolino non quadra.

**Limiti.**

- Una sola segnalazione per cedolino: se il lordo non torna, il netto non si controlla (D5).
- Non ricalcola l'IRPEF: ne controlla solo l'effetto sul netto.

## C07 · Variazione del netto

**Priorità media.** Netto oltre il 20% sopra o sotto il mese prima, senza un evento che lo spieghi.

**La regola.** Il netto non deve cambiare di oltre il 20%, in su o in giù, rispetto al mese prima, a meno che il cedolino indichi un evento che lo spieghi.

**Fonti.** [S02](fonti.md).

**Nel foglio** (foglio Mese, riga 5; le altre righe sono uguali):

```
AH  Netto mese prima
    =IF($A5="","",IFERROR(INDEX('Mese precedente'!$C$5:$C$254,MATCH(A5,'Mese precedente'!$A$5:$A$254,0)),""))
AI  Variazione
    =IF($A5="","",IF(AH5="","",S5/AH5-1))
AQ  C07 Variazione
    =IF($A5="","",IF(AI5="","OK",IF(AND(ABS(AI5)>Parametri!$C$10,G5=""),"ERRORE","OK")))
```

**Un esempio dal mese di settembre 2026.** Dipendente B090, cliente B: netto di agosto 1.752,08 €, di settembre 2.374,82 € (+36%), nessun evento sul cedolino.

**Cause tipiche.**

- Straordinari o arretrati pagati senza un evento dichiarato.
- Voci duplicate, che gonfiano il netto.

**Cosa fare.** Chiedere al cliente l'evento che giustifica la variazione.

**Limiti.**

- La soglia del 20% va tarata sui primi mesi di uso reale (S02).
- Un evento dichiarato spegne il controllo, anche se l'importo è sbagliato.

## C08 · Riconciliazione F24

**Priorità alta.** Ritenute o contributi in F24 diversi dalla somma dei cedolini del cliente.

**La regola.** Per ogni cliente, le ritenute versate con il codice tributo 1001 e i contributi a carico dei dipendenti nell'F24 sono uguali alla somma dei cedolini del mese.

**Fonti.** [F09](fonti.md).

**Nel foglio** (foglio F24, riga 5; le altre righe sono uguali):

```
C  Ritenute nei cedolini
    =ROUND(SUMIFS(Mese!$Q$5:$Q$254,Mese!$B$5:$B$254,A5),2)
D  Differenza
    =ROUND(B5-C5,2)
F  Contributi nei cedolini
    =ROUND(SUMIFS(Mese!$O$5:$O$254,Mese!$B$5:$B$254,A5),2)
G  Differenza
    =ROUND(E5-F5,2)
H  C08 Esito
    =IF(OR(ABS(D5)>Parametri!$C$11,ABS(G5)>Parametri!$C$11),"ERRORE","OK")
```

**Un esempio dal mese di settembre 2026.** Cliente C: somma dei cedolini 7.214,66 €, nell'F24 7.002,26 €, differenza −212,40 €.

**Cause tipiche.**

- Un dipendente rimasto fuori dalla delega.
- Delega preparata prima di una correzione ai cedolini.

**Cosa fare.** Integrare la delega prima della scadenza del versamento.

**Limiti.**

- La sezione INPS è semplificata alla sola quota dei dipendenti (D12).
- Le addizionali regionali e comunali (codici 3802 e 3848) non sono riconciliate.

## C09 · Codice fiscale

**Priorità alta.** Carattere di controllo non valido.

**La regola.** Il carattere di controllo del codice fiscale (il sedicesimo) è quello che il DM 23 dicembre 1976 ricava dai primi quindici.

**Fonti.** [F08](fonti.md).

**Nel foglio** (foglio Mese, riga 5; le altre righe sono uguali):

```
AJ  Controllo CF
    =IF($A5="","",CHAR(65+MOD(SUMPRODUCT(SUMIF('Codice fiscale'!$A$5:$A$40,MID(C5,{1,3,5,7,9,11,13,15},1),'Codice fiscale'!$B$5:$B$40))+SUMPRODUCT(SUMIF('Codice fiscale'!$A$5:$A$40,MID(C5,{2,4,6,8,10,12,14},1),'Codice fiscale'!$C$5:$C$40)),26)))
AR  C09 Cod. fiscale
    =IF($A5="","",IF(AND(LEN(C5)=16,RIGHT(C5,1)=AJ5),"OK","ERRORE"))
```

**Un esempio dal mese di settembre 2026.** Dipendente B058, cliente B: il codice «GFZPLG92P01Z321A» ha un carattere di controllo non valido.

**Cause tipiche.**

- Codice trascritto a mano con un carattere sbagliato.

**Cosa fare.** Correggere il codice fiscale in anagrafica.

**Limiti.**

- Controlla solo il carattere di controllo, non che il codice corrisponda alla persona.
- I codici con omocodia sono validi e passano, come devono.

## C10 · Anagrafica

**Priorità alta.** Livello, part-time, superminimo o data di assunzione diversi dal mese prima, senza un evento.

**La regola.** Livello, part-time, superminimo e data di assunzione sono uguali al mese prima, a meno che il cedolino indichi un evento.

**Fonti.** [S06](fonti.md).

**Nel foglio** (foglio Mese, riga 5; le altre righe sono uguali):

```
AS  C10 Anagrafica
    =IF($A5="","",IF(ISNA(MATCH(A5,'Mese precedente'!$A$5:$A$254,0)),"OK",IF(AND(G5="",OR(INDEX('Mese precedente'!$E$5:$E$254,MATCH(A5,'Mese precedente'!$A$5:$A$254,0))&""<>D5&"",ABS(INDEX('Mese precedente'!$F$5:$F$254,MATCH(A5,'Mese precedente'!$A$5:$A$254,0))-F5)>Parametri!$C$11,ABS(INDEX('Mese precedente'!$G$5:$G$254,MATCH(A5,'Mese precedente'!$A$5:$A$254,0))-L5)>Parametri!$C$11,INDEX('Mese precedente'!$H$5:$H$254,MATCH(A5,'Mese precedente'!$A$5:$A$254,0))<>E5)),"ERRORE","OK")))
```

**Un esempio dal mese di settembre 2026.** Dipendente B070, cliente B: atteso «superminimo 150», sul cedolino «superminimo 0».

**Cause tipiche.**

- Anagrafica modificata per errore.
- Un cambio vero non comunicato come evento.

**Cosa fare.** Verificare il cambio con il cliente e con i documenti: se non c'è stato, correggere l'anagrafica.

**Limiti.**

- Un errore presente fin dall'assunzione non cambia da un mese all'altro e resta invisibile: è il limite dichiarato e tenuto vero da un test.
- Chi non ha un cedolino il mese prima non viene confrontato.

## C11 · Ratei 13ª e 14ª

**Priorità media.** Dodicesimi maturati diversi dai mesi di servizio nel periodo (frazione di 15 giorni intera).

**La regola.** I dodicesimi di tredicesima (da gennaio) e di quattordicesima (da luglio) sono i mesi di servizio nel periodo, fino al mese del cedolino; il mese di assunzione conta se ha almeno 15 giorni.

**Fonti.** [F11](fonti.md).

**Nel foglio** (foglio Mese, riga 5; le altre righe sono uguali):

```
AW  Ratei 13ª attesi
    =IF($A5="","",IF(AZ5<>"",IF(AZ5<MAX(E5,DATE(YEAR(AZ5),1,1)),0,IF((YEAR(AZ5)*12+MONTH(AZ5))=(YEAR(MAX(E5,DATE(YEAR(AZ5),1,1)))*12+MONTH(MAX(E5,DATE(YEAR(AZ5),1,1)))),IF(AZ5-MAX(E5,DATE(YEAR(AZ5),1,1))+1>=Parametri!$C$14,1,0),(YEAR(AZ5)*12+MONTH(AZ5))-(YEAR(MAX(E5,DATE(YEAR(AZ5),1,1)))*12+MONTH(MAX(E5,DATE(YEAR(AZ5),1,1))))-1+IF(DAY(EOMONTH(MAX(E5,DATE(YEAR(AZ5),1,1)),0))-DAY(MAX(E5,DATE(YEAR(AZ5),1,1)))+1>=Parametri!$C$14,1,0)+IF(DAY(AZ5)>=Parametri!$C$14,1,0))),IF(E5<=DATE(YEAR(Parametri!$C$5),1,1),MONTH(Parametri!$C$5),(YEAR(Parametri!$C$5)*12+MONTH(Parametri!$C$5))-(YEAR(E5)*12+MONTH(E5))+IF(DAY(EOMONTH(E5,0))-DAY(E5)+1>=Parametri!$C$14,1,0))))
AX  Ratei 14ª attesi
    =IF($A5="","",IF(AZ5<>"",IF(AZ5<MAX(E5,DATE(YEAR(AZ5)-IF(MONTH(AZ5)<7,1,0),7,1)),0,IF((YEAR(AZ5)*12+MONTH(AZ5))=(YEAR(MAX(E5,DATE(YEAR(AZ5)-IF(MONTH(AZ5)<7,1,0),7,1)))*12+MONTH(MAX(E5,DATE(YEAR(AZ5)-IF(MONTH(AZ5)<7,1,0),7,1)))),IF(AZ5-MAX(E5,DATE(YEAR(AZ5)-IF(MONTH(AZ5)<7,1,0),7,1))+1>=Parametri!$C$14,1,0),(YEAR(AZ5)*12+MONTH(AZ5))-(YEAR(MAX(E5,DATE(YEAR(AZ5)-IF(MONTH(AZ5)<7,1,0),7,1)))*12+MONTH(MAX(E5,DATE(YEAR(AZ5)-IF(MONTH(AZ5)<7,1,0),7,1))))-1+IF(DAY(EOMONTH(MAX(E5,DATE(YEAR(AZ5)-IF(MONTH(AZ5)<7,1,0),7,1)),0))-DAY(MAX(E5,DATE(YEAR(AZ5)-IF(MONTH(AZ5)<7,1,0),7,1)))+1>=Parametri!$C$14,1,0)+IF(DAY(AZ5)>=Parametri!$C$14,1,0))),IF(E5<=DATE(YEAR(Parametri!$C$5)-IF(MONTH(Parametri!$C$5)<7,1,0),7,1),(YEAR(Parametri!$C$5)*12+MONTH(Parametri!$C$5))-(YEAR(DATE(YEAR(Parametri!$C$5)-IF(MONTH(Parametri!$C$5)<7,1,0),7,1))*12+MONTH(DATE(YEAR(Parametri!$C$5)-IF(MONTH(Parametri!$C$5)<7,1,0),7,1)))+1,(YEAR(Parametri!$C$5)*12+MONTH(Parametri!$C$5))-(YEAR(E5)*12+MONTH(E5))+IF(DAY(EOMONTH(E5,0))-DAY(E5)+1>=Parametri!$C$14,1,0))))
AY  C11 Ratei
    =IF($A5="","",IF(OR(AU5="",AV5=""),"OK",IF(OR(AU5<>AW5,AV5<>AX5),"ERRORE","OK")))
```

**Un esempio dal mese di settembre 2026.** Dipendente B034, cliente B: atteso «13ª 7; 14ª 3», sul cedolino «13ª 8; 14ª 3».

**Cause tipiche.**

- Mese di assunzione con meno di 15 giorni contato intero.
- Quattordicesima contata da gennaio invece che da luglio.
- Un dodicesimo perso senza assenze che lo spieghino.

**Cosa fare.** Ricontare i dodicesimi dalla data di assunzione e correggere i ratei prima della tredicesima di dicembre.

**Limiti.**

- Controlla il numero di dodicesimi, non l'importo (D14).
- Non considera i periodi non retribuiti che riducono i ratei, come l'aspettativa.
- Le colonne dei ratei sono facoltative: senza, C11 non si applica (D15).

## C12 · Tredicesima e quattordicesima pagate

**Priorità alta.** Importo diverso dalla retribuzione mensile per i dodicesimi maturati, a dicembre o alla cessazione.

**La regola.** Tredicesima e quattordicesima sono la retribuzione mensile (tabellare, scatti e superminimo) per i dodicesimi maturati, diviso 12. A dicembre i dodicesimi sono quelli dei ratei; alla cessazione si contano fino alla data di uscita, e l'ultimo mese conta se ha almeno 15 giorni.

**Fonti.** [F11](fonti.md).

**Nel foglio** (foglio Mese, riga 5; le altre righe sono uguali):

```
BF  Retribuzione mensile
    =IF($A5="","",ROUND(I5+K5+L5,2))
BG  Dodicesimi 13ª
    =IF($A5="","",AW5)
BH  Dodicesimi 14ª
    =IF($A5="","",IF(AND(AZ5="",MONTH(Parametri!$C$5)>=7),IF(DATE(YEAR(Parametri!$C$5),6,30)<MAX(E5,DATE(YEAR(Parametri!$C$5)-1,7,1)),0,IF((YEAR(DATE(YEAR(Parametri!$C$5),6,30))*12+MONTH(DATE(YEAR(Parametri!$C$5),6,30)))=(YEAR(MAX(E5,DATE(YEAR(Parametri!$C$5)-1,7,1)))*12+MONTH(MAX(E5,DATE(YEAR(Parametri!$C$5)-1,7,1)))),IF(DATE(YEAR(Parametri!$C$5),6,30)-MAX(E5,DATE(YEAR(Parametri!$C$5)-1,7,1))+1>=Parametri!$C$14,1,0),(YEAR(DATE(YEAR(Parametri!$C$5),6,30))*12+MONTH(DATE(YEAR(Parametri!$C$5),6,30)))-(YEAR(MAX(E5,DATE(YEAR(Parametri!$C$5)-1,7,1)))*12+MONTH(MAX(E5,DATE(YEAR(Parametri!$C$5)-1,7,1))))-1+IF(DAY(EOMONTH(MAX(E5,DATE(YEAR(Parametri!$C$5)-1,7,1)),0))-DAY(MAX(E5,DATE(YEAR(Parametri!$C$5)-1,7,1)))+1>=Parametri!$C$14,1,0)+IF(DAY(DATE(YEAR(Parametri!$C$5),6,30))>=Parametri!$C$14,1,0))),AX5))
BI  Tredicesima attesa
    =IF($A5="","",ROUND(BF5*BG5/12,2))
BJ  Quattordicesima attesa
    =IF($A5="","",ROUND(BF5*BH5/12,2))
BK  C12 Mensilità
    =IF($A5="","",IF(IF(BC5="",FALSE,ABS(BC5-BI5)>Parametri!$C$11),"ERRORE",IF(IF(BD5="",FALSE,ABS(BD5-BJ5)>Parametri!$C$11),"ERRORE","OK")))
```

**Un esempio dal mese di settembre 2026.** Dipendente B092, cliente B: atteso 452,38 €, sul cedolino 1.357,13 €, differenza 904,75 €.

**Cause tipiche.**

- Quattordicesima liquidata con i dodicesimi da gennaio invece che da luglio.
- Ultimo mese contato intero con meno di 15 giorni di servizio.
- Mensilità calcolata sulla retribuzione senza scatti o superminimo.

**Cosa fare.** Ricalcolare la mensilità con i dodicesimi giusti, da gennaio per la tredicesima e da luglio per la quattordicesima, e regolare la differenza: pagarla se manca, recuperarla se è stata pagata in più.

**Limiti.**

- Non considera i periodi non retribuiti che riducono i dodicesimi, come l'aspettativa.
- Le colonne sono facoltative: se il cedolino non riporta l'importo, C12 non si applica (D16).
- Una quattordicesima pagata a luglio a chi resta è quella del periodo chiuso il 30 giugno (D19). Per chi lascia nei primi giorni di luglio, quella del periodo precedente, se non ancora pagata, va controllata a mano.

## C13 · Ferie non godute

**Priorità alta.** Alla cessazione, ferie residue pagate diversamente da 1/26 della retribuzione mensile al giorno.

**La regola.** Alla cessazione le ferie maturate e non godute si pagano a 1/26 della retribuzione mensile per ogni giorno di residuo.

**Fonti.** [F12](fonti.md), [F04](fonti.md).

**Nel foglio** (foglio Mese, riga 5; le altre righe sono uguali):

```
BL  Ferie liquidate attese
    =IF($A5="","",IF(AZ5="","",ROUND(BF5/Parametri!$C$15*W5,2)))
BM  C13 Ferie
    =IF($A5="","",IF(OR(AZ5="",BE5=""),"OK",IF(ABS(BE5-BL5)>Parametri!$C$11,"ERRORE","OK")))
```

**Un esempio dal mese di settembre 2026.** Dipendente A011, cliente A: atteso 2.148,97 €, sul cedolino 1.862,44 €, differenza −286,53 €.

**Cause tipiche.**

- Quota giornaliera calcolata dividendo per 30 invece che per 26.
- Residuo ferie di fine rapporto non aggiornato con la maturazione dell'ultimo mese.

**Cosa fare.** Ricalcolare le ferie non godute a 1/26 della retribuzione mensile per giorno e regolare la differenza: pagarla se manca, recuperarla se è in più.

**Limiti.**

- Usa il residuo ferie del cedolino, che C05 controlla a parte. C05 conta la maturazione dell'intero mese anche per chi lascia a metà: in quel caso il residuo va ricontrollato a mano.
- Non considera i permessi (ROL ed ex festività), che hanno un loro divisore orario (D17).

## C14 · Preavviso

**Priorità alta.** Alla cessazione, giorni di preavviso sotto il minimo del CCNL per livello e anni di servizio.

**La regola.** Il preavviso, in giorni di calendario, è almeno quello del CCNL per livello, anni di servizio (fino a 5, dal 6° al 10°, oltre il 10°) e per chi recede: dimissioni o licenziamento.

**Fonti.** [F13](fonti.md).

**Nel foglio** (foglio Mese, riga 5; le altre righe sono uguali):

```
BN  Anni di servizio
    =IF($A5="","",IF(AZ5="","",YEAR(AZ5)-YEAR(E5)-IF(OR(MONTH(AZ5)<MONTH(E5),AND(MONTH(AZ5)=MONTH(E5),DAY(AZ5)<DAY(E5))),1,0)))
BO  Preavviso minimo
    =IF($A5="","",IF(OR(AZ5="",AND(TRIM(BA5)<>"dimissioni",TRIM(BA5)<>"licenziamento")),"",IFERROR(INDEX(CCNL!$K$5:$P$12,MATCH(D5&"",CCNL!$A$5:$A$12,0),IF(TRIM(BA5)="licenziamento",3,0)+IF(BN5<5,1,IF(BN5<10,2,3))),"")))
BP  C14 Preavviso
    =IF($A5="","",IF(OR(BO5="",BB5=""),"OK",IF(BB5<BO5,"ERRORE","OK")))
```

**Un esempio dal mese di settembre 2026.** Dipendente B045, cliente B: preavviso minimo 20 giorni, sul cedolino 10 giorni.

**Cause tipiche.**

- Tabella delle dimissioni usata per un licenziamento.
- Anni di servizio contati male, sulla soglia dei 5 o dei 10 anni.

**Cosa fare.** Verificare la data della lettera. Licenziamento: i giorni di preavviso non lavorati si pagano come indennità sostitutiva. Dimissioni: il preavviso non dato si può trattenere come indennità a carico del dipendente.

**Limiti.**

- Controlla i giorni di preavviso, non l'importo dell'indennità sostitutiva (D18).
- Non applica le anzianità convenzionali che il CCNL riconosce ad alcune categorie, né le regole degli operatori di vendita.
- Si applica solo a dimissioni e licenziamento: per giusta causa o altri tipi di cessazione il preavviso non è dovuto e il controllo tace.
