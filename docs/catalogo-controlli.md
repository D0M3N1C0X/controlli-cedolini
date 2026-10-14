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

## C01 · Minimo tabellare

**Priorità alta.** Tabellare diverso dal minimo del livello (paga base, altri elementi, contingenza), part-time compreso.

**La regola.** Il tabellare è il minimo del livello in vigore (paga base, altri elementi, contingenza ed EDR) per la percentuale di part-time, arrotondato al centesimo.

**Fonti.** [F01](fonti.md), [F02](fonti.md).

**Nel foglio** (foglio Mese, riga 5; le altre righe sono uguali):

```
X  Tabellare atteso
    =IF($A5="","",ROUND(INDEX(CCNL!$F$5:$F$12,MATCH(D5,CCNL!$A$5:$A$12,0))*F5,2))
AK  C01 Minimo
    =IF($A5="","",IF(ABS(I5-X5)>Parametri!$C$11,"ERRORE","OK"))
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
    =IF($A5="","",ROUND(INDEX(CCNL!$I$5:$I$12,MATCH(D5,CCNL!$A$5:$A$12,0))*Z5*F5,2))
AL  C02 Scatti
    =IF($A5="","",IF(ABS(K5-AA5)>Parametri!$C$11,"ERRORE","OK"))
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
    =IF($A5="","",ROUND(I5+K5+L5+M5,2))
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

**Un esempio dal mese di settembre 2026.** Cliente C: somma dei cedolini 6.345,71 €, nell'F24 6.133,31 €, differenza −212,40 €.

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
    =IF($A5="","",IF(E5<=DATE(YEAR(Parametri!$C$5),1,1),MONTH(Parametri!$C$5),(YEAR(Parametri!$C$5)*12+MONTH(Parametri!$C$5))-(YEAR(E5)*12+MONTH(E5))+IF(DAY(EOMONTH(E5,0))-DAY(E5)+1>=Parametri!$C$14,1,0)))
AX  Ratei 14ª attesi
    =IF($A5="","",IF(E5<=DATE(YEAR(Parametri!$C$5)-IF(MONTH(Parametri!$C$5)<7,1,0),7,1),(YEAR(Parametri!$C$5)*12+MONTH(Parametri!$C$5))-(YEAR(DATE(YEAR(Parametri!$C$5)-IF(MONTH(Parametri!$C$5)<7,1,0),7,1))*12+MONTH(DATE(YEAR(Parametri!$C$5)-IF(MONTH(Parametri!$C$5)<7,1,0),7,1)))+1,(YEAR(Parametri!$C$5)*12+MONTH(Parametri!$C$5))-(YEAR(E5)*12+MONTH(E5))+IF(DAY(EOMONTH(E5,0))-DAY(E5)+1>=Parametri!$C$14,1,0)))
AY  C11 Ratei
    =IF($A5="","",IF(AND(AU5="",AV5=""),"OK",IF(OR(AU5<>AW5,AV5<>AX5),"ERRORE","OK")))
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
