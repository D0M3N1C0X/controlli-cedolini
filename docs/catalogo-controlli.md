# Catalogo dei controlli

Una scheda per controllo: cosa controlla, da quale regola, dove sta nel foglio, un esempio vero e cosa fare. Generato da `src/build_catalogo.py`: nome, priorità, formule ed esempi vengono dal codice e dal foglio, quindi non restano indietro.

| Controllo | Priorità | Cosa controlla |
|---|---|---|
| [C01 · Minimo tabellare](#c01--minimo-tabellare) | alta | Tabellare diverso dal minimo del livello (paga base, altri elementi, contingenza), part-time compreso |
| [C02 · Scatti di anzianità](#c02--scatti-di-anzianità) | alta | Importo degli scatti diverso da quelli maturati dalla data di assunzione |
| [C03 · Contributi INPS](#c03--contributi-inps) | alta | Contributo a carico del dipendente diverso da imponibile arrotondato all'euro × aliquota della posizione (IVS, CIGS, FIS), più l'1% oltre la prima fascia pensionabile |
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
| [C15 · Indennità di malattia INPS](#c15--indennità-di-malattia-inps) | alta | Indennità anticipata diversa dal 50% (4°-20° giorno) e 66,66% (21°-180°) della retribuzione media giornaliera del mese prima |
| [C16 · Carenza di malattia](#c16--carenza-di-malattia) | media | Integrazione dei primi 3 giorni pagata dal 5° evento dell'anno, o non pagata quando è dovuta |
| [C17 · Indennità di maternità INPS](#c17--indennità-di-maternità-inps) | alta | Indennità anticipata diversa dall'80% della retribuzione media giornaliera del mese prima |
| [C18 · Permessi ROL ed ex festività](#c18--permessi-rol-ed-ex-festività) | media | Residuo ore diverso da residuo del mese prima + maturate - godute, con la maturazione del CCNL |
| [C19 · TFR liquidato](#c19--tfr-liquidato) | alta | Alla cessazione, TFR diverso dal fondo rivalutato con l'indice ISTAT, al netto dell'imposta sostitutiva, più le quote dell'anno meno lo 0,50% |
| [C20 · IRPEF del mese](#c20--irpef-del-mese) | alta | Ritenuta, somma del cuneo fiscale o trattamento integrativo diversi da quelli delle regole 2026: scaglioni ragguagliati al mese, detrazioni per un dodicesimo sul reddito presunto dell'anno |
| [C21 · Conguaglio IRPEF alla cessazione](#c21--conguaglio-irpef-alla-cessazione) | alta | Imposta dell'anno, detrazioni e trattamento integrativo rapportati ai giorni di lavoro, meno quanto già trattenuto o erogato: il cedolino di uscita porta una differenza diversa |

## C01 · Minimo tabellare

**Priorità alta.** Tabellare diverso dal minimo del livello (paga base, altri elementi, contingenza), part-time compreso.

**La regola.** Il tabellare è il minimo del livello in vigore (paga base, altri elementi, contingenza ed EDR) per la percentuale di part-time, arrotondato al centesimo.

**Fonti.** [F01](fonti.md), [F02](fonti.md).

**Nel foglio** (foglio Mese, riga 5; le altre righe sono uguali):

```
X  Tabellare atteso
    =IF($A5="","",IFERROR(ROUND(INDEX(CCNL!$F$5:$F$12,MATCH(D5&"",CCNL!$A$5:$A$12,0))*F5,2),""))
AK  C01 Minimo
    =IF($A5="","",IF(ISNUMBER(X5),IF(ABS(I5-X5)>Parametri!$C$19,"ERRORE","OK"),"ERRORE"))
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
    =IF($A5="","",MIN(Parametri!$C$21,MAX(0,INT((Y5-1)/36))))
AA  Importo scatti atteso
    =IF($A5="","",IFERROR(ROUND(INDEX(CCNL!$I$5:$I$12,MATCH(D5&"",CCNL!$A$5:$A$12,0))*Z5*F5,2),""))
AL  C02 Scatti
    =IF($A5="","",IF(ISNUMBER(AA5),IF(ABS(K5-AA5)>Parametri!$C$19,"ERRORE","OK"),"OK"))
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

**Priorità alta.** Contributo a carico del dipendente diverso da imponibile arrotondato all'euro × aliquota della posizione (IVS, CIGS, FIS), più l'1% oltre la prima fascia pensionabile.

**La regola.** Il contributo a carico del dipendente è l'imponibile arrotondato all'euro per l'aliquota della posizione INPS del cliente: IVS 9,19%, più la CIGS (0,30%) se nel semestre la media supera 15 dipendenti, più un terzo del FIS (0,50% fino a 5 dipendenti, 0,80% oltre); più l'1% sulla parte oltre la prima fascia pensionabile mensilizzata (4.685 € nel 2026). Al centesimo.

**Fonti.** [F05](fonti.md), [F10](fonti.md), [F14](fonti.md), [F15](fonti.md).

**Nel foglio** (foglio Mese, riga 5; le altre righe sono uguali):

```
AB  Contributi attesi
    =IF($A5="","",ROUND(ROUND(N5,0)*INDEX(Parametri!$E$77:$E$89,MATCH(B5,Parametri!$B$77:$B$89,0))+MAX(0,ROUND(N5,0)-Parametri!$C$14)*Parametri!$C$13,2))
AM  C03 INPS
    =IF($A5="","",IF(ABS(O5-AB5)>Parametri!$C$19,"ERRORE","OK"))
```

**Un esempio dal mese di settembre 2026.** Dipendente A009, cliente A: atteso 159,63 €, sul cedolino 164,69 €, differenza 5,06 €.

**Cause tipiche.**

- Posizione INPS impostata senza CIGS o FIS, o con la CIGS quando la media del semestre è sotto 15.
- Contributo aggiuntivo dell'1% dimenticato sulle retribuzioni alte.
- Imponibile non arrotondato all'euro, o arrotondato due volte.

**Cosa fare.** Correggere l'aliquota nella posizione INPS del cliente: CIGS e FIS dipendono dalla media dei dipendenti nel semestre; sopra 4.685 € al mese si aggiunge l'1%.

**Limiti.**

- La media del semestre va presa dalla posizione INPS del cliente: il controllo usa quella indicata.
- Non considera la riduzione del FIS per chi non ha chiesto integrazioni da 24 mesi, né fondi bilaterali diversi dal FIS.
- L'imponibile è il lordo: voci escluse dall'imponibile non sono gestite.

## C04 · Quota TFR

**Priorità media.** Rateo TFR diverso da retribuzione ordinaria × 14 / 13,5 / 12.

**La regola.** Il rateo mensile di TFR è la retribuzione ordinaria (tabellare, scatti, superminimo) per 14 mensilità, diviso 13,5 e diviso 12.

**Fonti.** [F06](fonti.md), [S03](fonti.md).

**Nel foglio** (foglio Mese, riga 5; le altre righe sono uguali):

```
AC  TFR atteso
    =IF($A5="","",ROUND((I5+K5+L5)*Parametri!$C$16/Parametri!$C$15/12,2))
AN  C04 TFR
    =IF($A5="","",IF(ABS(T5-AC5)>Parametri!$C$19,"ERRORE","OK"))
```

**Un esempio dal mese di settembre 2026.** Dipendente A001, cliente A: atteso 146,02 €, sul cedolino 133,06 €, differenza −12,96 €.

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
    =IF($A5="","",ROUND(AD5+ROUND(Parametri!$C$17/12,4)-V5,4))
AO  C05 Ferie
    =IF($A5="","",IF(ABS(W5-AE5)>Parametri!$C$20,"ERRORE","OK"))
```

**Un esempio dal mese di settembre 2026.** Dipendente A015, cliente A: residuo atteso 29,6064 giorni, sul cedolino 27,4397.

**Cause tipiche.**

- Maturazione del mese non registrata.
- Ferie godute non scaricate dal residuo.

**Cosa fare.** Riallineare il residuo: maturazione del mese non registrata.

**Limiti.**

- Ferie in giorni, non in ore; ROL ed ex festività sono in C18.
- Per chi è assunto nel mese il residuo di partenza è zero.

## C06 · Quadratura

**Priorità alta.** Lordo diverso dalla somma delle voci, o netto diverso da lordo meno trattenute.

**La regola.** Il lordo è la somma di tabellare, scatti, superminimo e straordinari; il netto è il lordo meno contributi, IRPEF e altre trattenute, più la somma del cuneo fiscale e il trattamento integrativo.

**Fonti.** [S01](fonti.md).

**Nel foglio** (foglio Mese, riga 5; le altre righe sono uguali):

```
AF  Lordo atteso
    =IF($A5="","",ROUND(I5+K5+L5+M5+N(BC5)+N(BD5)+N(BE5),2))
AG  Netto atteso
    =IF($A5="","",ROUND(N5-O5-Q5-R5+N(CY5)+N(CZ5),2))
AP  C06 Quadratura
    =IF($A5="","",IF(OR(ABS(N5-AF5)>Parametri!$C$19,ABS(S5-AG5)>Parametri!$C$19),"ERRORE","OK"))
```

**Un esempio dal mese di settembre 2026.** Dipendente A005, cliente A: atteso 1.336,88 €, sul cedolino 1.374,38 €, differenza 37,50 €.

**Cause tipiche.**

- Una voce aggiunta a mano e non sommata.
- Una trattenuta inserita due volte.

**Cosa fare.** Ricontrollare le voci: il cedolino non quadra.

**Limiti.**

- Una sola segnalazione per cedolino: se il lordo non torna, il netto non si controlla (D5).
- L'IRPEF la ricalcola C20 (C21 all'uscita): qui conta solo che il netto torni con le voci del cedolino.

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
    =IF($A5="","",IF(AI5="","OK",IF(AND(ABS(AI5)>Parametri!$C$18,G5=""),"ERRORE","OK")))
```

**Un esempio dal mese di settembre 2026.** Dipendente A008, cliente A: netto di agosto 1.637,54 €, di settembre 2.095,61 € (+28%), nessun evento sul cedolino.

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
    =IF(OR(ABS(D5)>Parametri!$C$19,ABS(G5)>Parametri!$C$19),"ERRORE","OK")
```

**Un esempio dal mese di settembre 2026.** Cliente C: somma dei cedolini 3.608,60 €, nell'F24 3.396,20 €, differenza −212,40 €.

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

**Un esempio dal mese di settembre 2026.** Dipendente B040, cliente B: il codice «CPTFPV79H01Z105A» ha un carattere di controllo non valido.

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
    =IF($A5="","",IF(ISNA(MATCH(A5,'Mese precedente'!$A$5:$A$254,0)),"OK",IF(AND(G5="",OR(INDEX('Mese precedente'!$E$5:$E$254,MATCH(A5,'Mese precedente'!$A$5:$A$254,0))&""<>D5&"",ABS(INDEX('Mese precedente'!$F$5:$F$254,MATCH(A5,'Mese precedente'!$A$5:$A$254,0))-F5)>Parametri!$C$19,ABS(INDEX('Mese precedente'!$G$5:$G$254,MATCH(A5,'Mese precedente'!$A$5:$A$254,0))-L5)>Parametri!$C$19,INDEX('Mese precedente'!$H$5:$H$254,MATCH(A5,'Mese precedente'!$A$5:$A$254,0))<>E5)),"ERRORE","OK")))
```

**Un esempio dal mese di settembre 2026.** Dipendente B061, cliente B: atteso «livello 4», sul cedolino «livello 5».

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
    =IF($A5="","",IF(AZ5<>"",IF(AZ5<MAX(E5,DATE(YEAR(AZ5),1,1)),0,IF((YEAR(AZ5)*12+MONTH(AZ5))=(YEAR(MAX(E5,DATE(YEAR(AZ5),1,1)))*12+MONTH(MAX(E5,DATE(YEAR(AZ5),1,1)))),IF(AZ5-MAX(E5,DATE(YEAR(AZ5),1,1))+1>=Parametri!$C$22,1,0),(YEAR(AZ5)*12+MONTH(AZ5))-(YEAR(MAX(E5,DATE(YEAR(AZ5),1,1)))*12+MONTH(MAX(E5,DATE(YEAR(AZ5),1,1))))-1+IF(DAY(EOMONTH(MAX(E5,DATE(YEAR(AZ5),1,1)),0))-DAY(MAX(E5,DATE(YEAR(AZ5),1,1)))+1>=Parametri!$C$22,1,0)+IF(DAY(AZ5)>=Parametri!$C$22,1,0))),IF(E5<=DATE(YEAR(Parametri!$C$5),1,1),MONTH(Parametri!$C$5),(YEAR(Parametri!$C$5)*12+MONTH(Parametri!$C$5))-(YEAR(E5)*12+MONTH(E5))+IF(DAY(EOMONTH(E5,0))-DAY(E5)+1>=Parametri!$C$22,1,0))))
AX  Ratei 14ª attesi
    =IF($A5="","",IF(AZ5<>"",IF(AZ5<MAX(E5,DATE(YEAR(AZ5)-IF(MONTH(AZ5)<7,1,0),7,1)),0,IF((YEAR(AZ5)*12+MONTH(AZ5))=(YEAR(MAX(E5,DATE(YEAR(AZ5)-IF(MONTH(AZ5)<7,1,0),7,1)))*12+MONTH(MAX(E5,DATE(YEAR(AZ5)-IF(MONTH(AZ5)<7,1,0),7,1)))),IF(AZ5-MAX(E5,DATE(YEAR(AZ5)-IF(MONTH(AZ5)<7,1,0),7,1))+1>=Parametri!$C$22,1,0),(YEAR(AZ5)*12+MONTH(AZ5))-(YEAR(MAX(E5,DATE(YEAR(AZ5)-IF(MONTH(AZ5)<7,1,0),7,1)))*12+MONTH(MAX(E5,DATE(YEAR(AZ5)-IF(MONTH(AZ5)<7,1,0),7,1))))-1+IF(DAY(EOMONTH(MAX(E5,DATE(YEAR(AZ5)-IF(MONTH(AZ5)<7,1,0),7,1)),0))-DAY(MAX(E5,DATE(YEAR(AZ5)-IF(MONTH(AZ5)<7,1,0),7,1)))+1>=Parametri!$C$22,1,0)+IF(DAY(AZ5)>=Parametri!$C$22,1,0))),IF(E5<=DATE(YEAR(Parametri!$C$5)-IF(MONTH(Parametri!$C$5)<7,1,0),7,1),(YEAR(Parametri!$C$5)*12+MONTH(Parametri!$C$5))-(YEAR(DATE(YEAR(Parametri!$C$5)-IF(MONTH(Parametri!$C$5)<7,1,0),7,1))*12+MONTH(DATE(YEAR(Parametri!$C$5)-IF(MONTH(Parametri!$C$5)<7,1,0),7,1)))+1,(YEAR(Parametri!$C$5)*12+MONTH(Parametri!$C$5))-(YEAR(E5)*12+MONTH(E5))+IF(DAY(EOMONTH(E5,0))-DAY(E5)+1>=Parametri!$C$22,1,0))))
AY  C11 Ratei
    =IF($A5="","",IF(OR(AU5="",AV5=""),"OK",IF(OR(AU5<>AW5,AV5<>AX5),"ERRORE","OK")))
```

**Un esempio dal mese di settembre 2026.** Dipendente A011, cliente A: atteso «13ª 9; 14ª 3», sul cedolino «13ª 9; 14ª 9».

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
    =IF($A5="","",IF(AND(AZ5="",MONTH(Parametri!$C$5)>=7),IF(DATE(YEAR(Parametri!$C$5),6,30)<MAX(E5,DATE(YEAR(Parametri!$C$5)-1,7,1)),0,IF((YEAR(DATE(YEAR(Parametri!$C$5),6,30))*12+MONTH(DATE(YEAR(Parametri!$C$5),6,30)))=(YEAR(MAX(E5,DATE(YEAR(Parametri!$C$5)-1,7,1)))*12+MONTH(MAX(E5,DATE(YEAR(Parametri!$C$5)-1,7,1)))),IF(DATE(YEAR(Parametri!$C$5),6,30)-MAX(E5,DATE(YEAR(Parametri!$C$5)-1,7,1))+1>=Parametri!$C$22,1,0),(YEAR(DATE(YEAR(Parametri!$C$5),6,30))*12+MONTH(DATE(YEAR(Parametri!$C$5),6,30)))-(YEAR(MAX(E5,DATE(YEAR(Parametri!$C$5)-1,7,1)))*12+MONTH(MAX(E5,DATE(YEAR(Parametri!$C$5)-1,7,1))))-1+IF(DAY(EOMONTH(MAX(E5,DATE(YEAR(Parametri!$C$5)-1,7,1)),0))-DAY(MAX(E5,DATE(YEAR(Parametri!$C$5)-1,7,1)))+1>=Parametri!$C$22,1,0)+IF(DAY(DATE(YEAR(Parametri!$C$5),6,30))>=Parametri!$C$22,1,0))),AX5))
BI  Tredicesima attesa
    =IF($A5="","",ROUND(BF5*BG5/12,2))
BJ  Quattordicesima attesa
    =IF($A5="","",ROUND(BF5*BH5/12,2))
BK  C12 Mensilità
    =IF($A5="","",IF(IF(BC5="",FALSE,ABS(BC5-BI5)>Parametri!$C$19),"ERRORE",IF(IF(BD5="",FALSE,ABS(BD5-BJ5)>Parametri!$C$19),"ERRORE","OK")))
```

**Un esempio dal mese di settembre 2026.** Dipendente B062, cliente B: atteso 470,59 €, sul cedolino 1.411,76 €, differenza 941,17 €.

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
    =IF($A5="","",IF(AZ5="","",ROUND(BF5/Parametri!$C$23*W5,2)))
BM  C13 Ferie
    =IF($A5="","",IF(OR(AZ5="",BE5=""),"OK",IF(ABS(BE5-BL5)>Parametri!$C$19,"ERRORE","OK")))
```

**Un esempio dal mese di settembre 2026.** Dipendente B027, cliente B: atteso 1.980,46 €, sul cedolino 1.716,40 €, differenza −264,06 €.

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

**Un esempio dal mese di settembre 2026.** Dipendente B076, cliente B: preavviso minimo 20 giorni, sul cedolino 10 giorni.

**Cause tipiche.**

- Tabella delle dimissioni usata per un licenziamento.
- Anni di servizio contati male, sulla soglia dei 5 o dei 10 anni.

**Cosa fare.** Verificare la data della lettera. Licenziamento: i giorni di preavviso non lavorati si pagano come indennità sostitutiva. Dimissioni: il preavviso non dato si può trattenere come indennità a carico del dipendente.

**Limiti.**

- Controlla i giorni di preavviso, non l'importo dell'indennità sostitutiva (D18).
- Non applica le anzianità convenzionali che il CCNL riconosce ad alcune categorie, né le regole degli operatori di vendita.
- Si applica solo a dimissioni e licenziamento: per giusta causa o altri tipi di cessazione il preavviso non è dovuto e il controllo tace.

## C15 · Indennità di malattia INPS

**Priorità alta.** Indennità anticipata diversa dal 50% (4°-20° giorno) e 66,66% (21°-180°) della retribuzione media giornaliera del mese prima.

**La regola.** L'indennità di malattia anticipata per conto dell'INPS è il 50% della retribuzione media globale giornaliera per i giorni dal 4° al 20° dell'evento e il 66,66% dal 21° al 180°, domeniche comprese; la retribuzione media è quella del mese prima per 14/12, divisa per 30.

**Fonti.** [F16](fonti.md), [F17](fonti.md).

**Nel foglio** (foglio Mese, riga 5; le altre righe sono uguali):

```
CG  Retribuzione mese prima
    =IF($A5="","",IFERROR(INDEX('Mese precedente'!$I$5:$I$254,MATCH(A5,'Mese precedente'!$A$5:$A$254,0)),""))
CH  Retribuzione media giornaliera
    =IF($A5="","",IF(CG5="","",ROUND(CG5*Parametri!$C$16/12/Parametri!$C$24,2)))
CI  Giorni di carenza
    =IF($A5="","",IF(BQ5="","",MAX(0,MIN(BQ5+Parametri!$C$25-1,BR5,EOMONTH(Parametri!$C$5,0))-MAX(BQ5,BQ5,Parametri!$C$5)+1)))
CJ  Giorni al 50%
    =IF($A5="","",IF(BQ5="","",MAX(0,MIN(BQ5+Parametri!$C$26-1,BR5,EOMONTH(Parametri!$C$5,0))-MAX(BQ5+Parametri!$C$25+1-1,BQ5,Parametri!$C$5)+1)))
CK  Giorni al 66,66%
    =IF($A5="","",IF(BQ5="","",MAX(0,MIN(BQ5+Parametri!$C$28-1,BR5,EOMONTH(Parametri!$C$5,0))-MAX(BQ5+Parametri!$C$26+1-1,BQ5,Parametri!$C$5)+1)))
CL  Malattia attesa
    =IF($A5="","",IF(OR(BQ5="",CH5=""),"",IF(BQ5<Parametri!$C$5,"",ROUND(CH5*Parametri!$C$27*CJ5+CH5*Parametri!$C$29*CK5,2))))
CM  C15 Malattia
    =IF($A5="","",IF(OR(CL5="",BU5=""),"OK",IF(ABS(BU5-CL5)>Parametri!$C$19,"ERRORE","OK")))
```

**Un esempio dal mese di settembre 2026.** Dipendente B080, cliente B: atteso 682,94 €, sul cedolino 675,46 €, differenza −7,48 €.

**Cause tipiche.**

- Base giornaliera calcolata dividendo per 26 invece che per 30, o senza i ratei di tredicesima e quattordicesima.
- Giorni contati dall'inizio del mese invece che dall'inizio dell'evento.
- Carenza indennizzata dall'INPS, o 66,66% applicato prima del 21° giorno.

**Cosa fare.** Ricalcolare l'indennità sulla retribuzione del mese prima × 14/12 / 30, al 50% dal 4° al 20° giorno e al 66,66% dopo, e correggere il conguaglio con l'INPS nel flusso UniEmens.

**Limiti.**

- Controlla l'indennità INPS, non l'integrazione dell'azienda: il CCNL la fissa sulla retribuzione netta, che richiede il calcolo fiscale (D21).
- Gli eventi iniziati prima del mese non sono controllati: la base sarebbe un cedolino che il controllo non ha.
- Vale per gli impiegati del terziario; operai, pubblici esercizi e ricoveri hanno altre misure.

## C16 · Carenza di malattia

**Priorità media.** Integrazione dei primi 3 giorni pagata dal 5° evento dell'anno, o non pagata quando è dovuta.

**La regola.** L'integrazione dei primi 3 giorni è dovuta per intero ai primi 2 eventi di malattia dell'anno, al 66% al 3°, al 50% al 4°, e non più dal 5°; senza limiti per ricovero, prognosi iniziale di almeno 12 giorni, terapie salvavita e malattie in gravidanza.

**Fonti.** [F16](fonti.md).

**Nel foglio** (foglio Mese, riga 5; le altre righe sono uguali):

```
CI  Giorni di carenza
    =IF($A5="","",IF(BQ5="","",MAX(0,MIN(BQ5+Parametri!$C$25-1,BR5,EOMONTH(Parametri!$C$5,0))-MAX(BQ5,BQ5,Parametri!$C$5)+1)))
CN  Quota di carenza dovuta
    =IF($A5="","",IF(OR(BQ5="",BS5=""),"",IF(ISNUMBER(MATCH(LOWER(TRIM(BT5&"")),{"true","vero","1","si","sì","yes","x"},0)),1,IF(AND(BS5>=1,BS5<=ROWS(Parametri!$C$108:$C$111)),INDEX(Parametri!$C$108:$C$111,BS5),0))))
CO  C16 Carenza
    =IF($A5="","",IF(OR(CN5="",N(CI5)=0),"OK",IF(OR(AND(CN5=0,N(BV5)>Parametri!$C$19),AND(CN5>0,N(BV5)<=Parametri!$C$19)),"ERRORE","OK")))
```

**Un esempio dal mese di settembre 2026.** Dipendente B026, cliente B: atteso non dovuta, sul cedolino 151,65 €, differenza .

**Cause tipiche.**

- Eventi dell'anno non contati: carenza pagata anche dal quinto.
- Esenzione non registrata, e carenza negata a chi ne ha diritto.

**Cosa fare.** Contare gli eventi di malattia dell'anno: dal quinto la carenza non si paga, salvo ricovero, prognosi di almeno 12 giorni, terapie salvavita o gravidanza; se è dovuta e manca, pagarla.

**Limiti.**

- Controlla se la carenza è pagata quando serve, non l'importo: anche quello è sul netto.
- Il numero dell'evento e l'esenzione vengono dal cedolino: una ricaduta conta come lo stesso evento, e va registrata così.

## C17 · Indennità di maternità INPS

**Priorità alta.** Indennità anticipata diversa dall'80% della retribuzione media giornaliera del mese prima.

**La regola.** L'indennità di maternità anticipata per conto dell'INPS è l'80% della retribuzione media globale giornaliera del mese prima dell'inizio del congedo, per ogni giorno del mese.

**Fonti.** [F17](fonti.md), [F18](fonti.md).

**Nel foglio** (foglio Mese, riga 5; le altre righe sono uguali):

```
CH  Retribuzione media giornaliera
    =IF($A5="","",IF(CG5="","",ROUND(CG5*Parametri!$C$16/12/Parametri!$C$24,2)))
CP  Maternità attesa
    =IF($A5="","",IF(OR(BW5="",CH5="",BY5=""),"",IF(BW5<Parametri!$C$5,"",ROUND(CH5*Parametri!$C$30*MAX(0,MIN(BX5,EOMONTH(Parametri!$C$5,0))-MAX(BW5,Parametri!$C$5)+1),2))))
CQ  C17 Maternità
    =IF($A5="","",IF(OR(CP5="",BY5=""),"OK",IF(ABS(BY5-CP5)>Parametri!$C$19,"ERRORE","OK")))
```

**Un esempio dal mese di settembre 2026.** Dipendente C095, cliente C: atteso 1.005,12 €, sul cedolino 861,60 €, differenza −143,52 €.

**Cause tipiche.**

- Base senza i ratei di tredicesima e quattordicesima.
- Integrazione dell'azienda al 100% registrata come indennità INPS.

**Cosa fare.** Ricalcolare l'indennità all'80% della retribuzione media giornaliera, ratei compresi, e correggere il conguaglio con l'INPS; l'integrazione al 100% resta a carico dell'azienda.

**Limiti.**

- Controlla la quota INPS: l'integrazione al 100% del netto per i primi cinque mesi è dell'azienda.
- I congedi iniziati prima del mese non sono controllati, per la stessa ragione di C15.

## C18 · Permessi ROL ed ex festività

**Priorità media.** Residuo ore diverso da residuo del mese prima + maturate - godute, con la maturazione del CCNL.

**La regola.** Il residuo dei permessi è il residuo del mese prima più un dodicesimo delle ore annue, meno le ore godute: 72 ore di riduzione d'orario (56 fino a 15 dipendenti) e 32 di ex festività, in proporzione al part-time; per chi è entrato dopo il 1° marzo 2011 la riduzione d'orario spetta al 50% dopo 2 anni e al 100% dopo 4.

**Fonti.** [F23](fonti.md), [S07](fonti.md).

**Nel foglio** (foglio Mese, riga 5; le altre righe sono uguali):

```
CR  Residuo permessi mese prima
    =IF($A5="","",IFERROR(INDEX('Mese precedente'!$J$5:$J$254,MATCH(A5,'Mese precedente'!$A$5:$A$254,0)),0))
CS  Permessi maturati attesi
    =IF($A5="","",IFERROR(ROUND((IF(INDEX(Parametri!$D$77:$D$89,MATCH(B5,Parametri!$B$77:$B$89,0))>Parametri!$C$33,Parametri!$C$32,Parametri!$C$31)*IF(E5>Parametri!$C$35,IF((YEAR(EOMONTH(Parametri!$C$5,0))-YEAR(E5)-IF(OR(MONTH(EOMONTH(Parametri!$C$5,0))<MONTH(E5),AND(MONTH(EOMONTH(Parametri!$C$5,0))=MONTH(E5),DAY(EOMONTH(Parametri!$C$5,0))<DAY(E5))),1,0))<2,0,IF((YEAR(EOMONTH(Parametri!$C$5,0))-YEAR(E5)-IF(OR(MONTH(EOMONTH(Parametri!$C$5,0))<MONTH(E5),AND(MONTH(EOMONTH(Parametri!$C$5,0))=MONTH(E5),DAY(EOMONTH(Parametri!$C$5,0))<DAY(E5))),1,0))<4,0.5,1)),1)+Parametri!$C$34)/12*F5,4),""))
CT  Residuo permessi atteso
    =IF($A5="","",IF(CS5="","",ROUND(CR5+CS5-N(CA5),4)))
CU  C18 Permessi
    =IF($A5="","",IF(OR(CB5="",CT5=""),"OK",IF(ABS(CB5-CT5)>Parametri!$C$36,"ERRORE","OK")))
```

**Un esempio dal mese di settembre 2026.** Dipendente A017, cliente A: atteso 33,16 €, sul cedolino 39,82 €, differenza 6,67 €.

**Cause tipiche.**

- Riduzione d'orario maturata per intero da un neoassunto.
- Part-time che matura le ore di un tempo pieno.
- Soglia dei 15 dipendenti sbagliata nella configurazione del cliente.

**Cosa fare.** Rifare la maturazione dei permessi: 72 o 56 ore di riduzione d'orario secondo i dipendenti, più 32 di ex festività, in proporzione al part-time e con la regola dei 2 e 4 anni per chi è entrato dopo marzo 2011.

**Limiti.**

- Non riduce la maturazione per assenze non retribuite, né per le articolazioni d'orario che assorbono i permessi (39 o 38 ore settimanali).
- Gli anni di anzianità si contano all'ultimo giorno del mese (S07).

## C19 · TFR liquidato

**Priorità alta.** Alla cessazione, TFR diverso dal fondo rivalutato con l'indice ISTAT, al netto dell'imposta sostitutiva, più le quote dell'anno meno lo 0,50%.

**La regola.** Il TFR liquidato è il fondo al 31 dicembre, più la rivalutazione (1,5% annuo fisso per i mesi interi e il 75% dell'aumento dell'indice ISTAT FOI su dicembre; il mese conta se si esce dal 15) meno l'imposta sostitutiva del 17% sulla rivalutazione, più le quote dell'anno meno lo 0,50% dell'imponibile previdenziale.

**Fonti.** [F19](fonti.md), [F20](fonti.md), [F21](fonti.md), [F22](fonti.md).

**Nel foglio** (foglio Mese, riga 5; le altre righe sono uguali):

```
CV  Coefficiente ISTAT %
    =IF($A5="","",IF(AZ5="","",IF(IF(DAY(AZ5)>=15,MONTH(AZ5),MONTH(AZ5)-1)=0,0,IFERROR(ROUND(Parametri!$C$37*IF(DAY(AZ5)>=15,MONTH(AZ5),MONTH(AZ5)-1)/12+Parametri!$C$38*((INDEX(Parametri!$C$93:$C$104,MATCH(DATE(YEAR(AZ5),IF(DAY(AZ5)>=15,MONTH(AZ5),MONTH(AZ5)-1),1),Parametri!$B$93:$B$104,0))*Parametri!$C$40/Parametri!$C$39-1)*100),6),""))))
CW  TFR atteso
    =IF($A5="","",IF(OR(CV5="",CC5="",CD5="",CE5=""),"",ROUND(CC5+ROUND(CC5*CV5/100,2)-ROUND(ROUND(CC5*CV5/100,2)*Parametri!$C$41,2)+CD5-ROUND(CE5*Parametri!$C$42,2),2)))
CX  C19 TFR
    =IF($A5="","",IF(OR(CW5="",CF5=""),"OK",IF(ABS(CF5-CW5)>Parametri!$C$19,"ERRORE","OK")))
```

**Un esempio dal mese di settembre 2026.** Dipendente B027, cliente B: atteso 23.446,76 €, sul cedolino 23.604,31 €, differenza 157,55 €.

**Cause tipiche.**

- Coefficiente del mese di uscita usato per chi esce prima del 15.
- Imposta sostitutiva non tolta dalla rivalutazione.
- Contributo dello 0,50% non tolto dalle quote dell'anno.

**Cosa fare.** Rifare il conteggio: coefficiente ISTAT del mese giusto (dal 15 in poi conta il mese), imposta sostitutiva del 17% sulla rivalutazione, 0,50% tolto dalle quote dell'anno; regolare la differenza.

**Limiti.**

- Controlla il lordo: la tassazione separata e le quote versate a fondi pensione o al Fondo di Tesoreria dell'INPS restano fuori.
- Fondo al 31 dicembre, quote e imponibile dell'anno vengono dal cedolino, non sono ricalcolati.
- Serve l'indice FOI del mese nei Parametri: per i mesi che mancano il controllo tace.

## C20 · IRPEF del mese

**Priorità alta.** Ritenuta, somma del cuneo fiscale o trattamento integrativo diversi da quelli delle regole 2026: scaglioni ragguagliati al mese, detrazioni per un dodicesimo sul reddito presunto dell'anno.

**La regola.** La ritenuta del mese applica all'imponibile fiscale gli scaglioni del 2026 (23%, 33%, 43%) ragguagliati al mese, e toglie un dodicesimo della detrazione per lavoro dipendente e dell'ulteriore detrazione del cuneo fiscale, calcolate sul reddito presunto dell'anno (imponibile del mese per 14 mensilità). Fino a 20.000 € di reddito spetta la somma del cuneo (7,1%, 5,3% o 4,8% dell'imponibile del mese), fino a 15.000 € un dodicesimo del trattamento integrativo.

**Fonti.** [F24](fonti.md), [F25](fonti.md), [F26](fonti.md), [F27](fonti.md), [F28](fonti.md), [S08](fonti.md), [S09](fonti.md), [S10](fonti.md), [S11](fonti.md).

**Nel foglio** (foglio Mese, riga 5; le altre righe sono uguali):

```
DF  Reddito presunto dell'anno
    =IF($A5="","",P5*Parametri!$C$16)
DG  IRPEF attesa
    =IF($A5="","",ROUND(MAX(0,(MAX(0,MIN(P5,Parametri!$C$43/12))*Parametri!$C$44+MAX(0,MIN(P5,Parametri!$C$45/12)-Parametri!$C$43/12)*Parametri!$C$46+MAX(0,P5-Parametri!$C$45/12)*Parametri!$C$47)-(IF(DF5<=Parametri!$C$52,Parametri!$C$48,IF(DF5<=Parametri!$C$53,Parametri!$C$50+Parametri!$C$51*ROUND((Parametri!$C$53-DF5)/(Parametri!$C$53-Parametri!$C$52),Parametri!$C$58),IF(DF5<=Parametri!$C$54,Parametri!$C$50*ROUND((Parametri!$C$54-DF5)/(Parametri!$C$54-Parametri!$C$53),Parametri!$C$58),0)))+IF(AND(DF5>Parametri!$C$56,DF5<=Parametri!$C$57),Parametri!$C$55,0))/12-IF(AND(DF5>Parametri!$C$66,DF5<=Parametri!$C$67),Parametri!$C$65,IF(AND(DF5>Parametri!$C$67,DF5<=Parametri!$C$68),Parametri!$C$65*ROUND((Parametri!$C$68-DF5)/(Parametri!$C$68-Parametri!$C$67),Parametri!$C$58),0))/12),2))
DH  Cuneo atteso
    =IF($A5="","",IF(DF5<=Parametri!$C$59,ROUND(P5*IF(DF5<=Parametri!$C$60,Parametri!$C$61,IF(DF5<=Parametri!$C$62,Parametri!$C$63,Parametri!$C$64)),2),0))
DI  Tratt. integrativo atteso
    =IF($A5="","",ROUND(IF(DF5<=Parametri!$C$70,IF((MAX(0,MIN(DF5,Parametri!$C$43))*Parametri!$C$44+MAX(0,MIN(DF5,Parametri!$C$45)-Parametri!$C$43)*Parametri!$C$46+MAX(0,DF5-Parametri!$C$45)*Parametri!$C$47)>(IF(DF5<=Parametri!$C$52,Parametri!$C$48,IF(DF5<=Parametri!$C$53,Parametri!$C$50+Parametri!$C$51*ROUND((Parametri!$C$53-DF5)/(Parametri!$C$53-Parametri!$C$52),Parametri!$C$58),IF(DF5<=Parametri!$C$54,Parametri!$C$50*ROUND((Parametri!$C$54-DF5)/(Parametri!$C$54-Parametri!$C$53),Parametri!$C$58),0)))+IF(AND(DF5>Parametri!$C$56,DF5<=Parametri!$C$57),Parametri!$C$55,0))-Parametri!$C$72*1,Parametri!$C$69*1,0),IF(AND(DF5<=Parametri!$C$71,(IF(DF5<=Parametri!$C$52,Parametri!$C$48,IF(DF5<=Parametri!$C$53,Parametri!$C$50+Parametri!$C$51*ROUND((Parametri!$C$53-DF5)/(Parametri!$C$53-Parametri!$C$52),Parametri!$C$58),IF(DF5<=Parametri!$C$54,Parametri!$C$50*ROUND((Parametri!$C$54-DF5)/(Parametri!$C$54-Parametri!$C$53),Parametri!$C$58),0)))+IF(AND(DF5>Parametri!$C$56,DF5<=Parametri!$C$57),Parametri!$C$55,0))>(MAX(0,MIN(DF5,Parametri!$C$43))*Parametri!$C$44+MAX(0,MIN(DF5,Parametri!$C$45)-Parametri!$C$43)*Parametri!$C$46+MAX(0,DF5-Parametri!$C$45)*Parametri!$C$47)),MIN(Parametri!$C$69*1,(IF(DF5<=Parametri!$C$52,Parametri!$C$48,IF(DF5<=Parametri!$C$53,Parametri!$C$50+Parametri!$C$51*ROUND((Parametri!$C$53-DF5)/(Parametri!$C$53-Parametri!$C$52),Parametri!$C$58),IF(DF5<=Parametri!$C$54,Parametri!$C$50*ROUND((Parametri!$C$54-DF5)/(Parametri!$C$54-Parametri!$C$53),Parametri!$C$58),0)))+IF(AND(DF5>Parametri!$C$56,DF5<=Parametri!$C$57),Parametri!$C$55,0))-(MAX(0,MIN(DF5,Parametri!$C$43))*Parametri!$C$44+MAX(0,MIN(DF5,Parametri!$C$45)-Parametri!$C$43)*Parametri!$C$46+MAX(0,DF5-Parametri!$C$45)*Parametri!$C$47)),0))/12,2))
DJ  C20 IRPEF
    =IF($A5="","",IF(AZ5<>"","OK",IF(OR(ABS(Q5-DG5)>Parametri!$C$19,ABS(N(CY5)-DH5)>Parametri!$C$19,ABS(N(CZ5)-DI5)>Parametri!$C$19),"ERRORE","OK")))
```

**Un esempio dal mese di settembre 2026.** Dipendente B030, cliente B: atteso 60,47 €, sul cedolino 0,00 €, differenza −60,47 €.

**Cause tipiche.**

- Tabella IRPEF del 2025 ancora nel software: 35% invece di 33% sul secondo scaglione.
- Ulteriore detrazione del cuneo fiscale non applicata tra 20.000 e 40.000 € di reddito.
- Somma del cuneo non erogata, o erogata a chi supera i 20.000 €.

**Cosa fare.** Controllare la tabella IRPEF del software (33% sul secondo scaglione dal 2026), l'ulteriore detrazione e la somma del cuneo fiscale, il trattamento integrativo; rifare la ritenuta e correggere nel mese dopo.

**Limiti.**

- Il reddito dell'anno è presunto dall'imponibile del mese (S09): un software che lo stima dall'anno progressivo dà ritenute diverse nei mesi, uguali al conguaglio.
- Niente detrazioni per familiari a carico, oneri o altri redditi dichiarati dal dipendente (S11).
- Le mensilità aggiuntive pagate in un mese ordinario si tassano senza detrazioni: il controllo vale per i mesi senza tredicesima o quattordicesima.
- Addizionali regionale e comunale fuori dal controllo: si trattengono a rate sull'anno prima.

## C21 · Conguaglio IRPEF alla cessazione

**Priorità alta.** Imposta dell'anno, detrazioni e trattamento integrativo rapportati ai giorni di lavoro, meno quanto già trattenuto o erogato: il cedolino di uscita porta una differenza diversa.

**La regola.** Alla cessazione il sostituto fa il conguaglio: imposta dell'anno sull'imponibile fiscale da gennaio, meno detrazione per lavoro dipendente e ulteriore detrazione rapportate ai giorni di lavoro (con il minimo di 690 € fino a 15.000 €), meno quanto già trattenuto. La somma del cuneo e il trattamento integrativo spettanti per il periodo si confrontano con quelli già erogati: la differenza si paga o si recupera nel cedolino di uscita.

**Fonti.** [F24](fonti.md), [F25](fonti.md), [F26](fonti.md), [F27](fonti.md), [F29](fonti.md), [S10](fonti.md), [S11](fonti.md).

**Nel foglio** (foglio Mese, riga 5; le altre righe sono uguali):

```
DK  Frazione d'anno
    =IF($A5="","",IF(AND(AZ5<>"",DA5<>"",DB5<>"",DC5<>"",DD5<>"",DE5<>""),DB5/Parametri!$C$73,""))
DL  Imposta lorda dell'anno
    =IF($A5="","",IF(DK5="","",(MAX(0,MIN(DA5,Parametri!$C$43))*Parametri!$C$44+MAX(0,MIN(DA5,Parametri!$C$45)-Parametri!$C$43)*Parametri!$C$46+MAX(0,DA5-Parametri!$C$45)*Parametri!$C$47)))
DM  Detrazione rapportata
    =IF($A5="","",IF(DK5="","",IF(DA5<=Parametri!$C$52,MAX((IF(DA5<=Parametri!$C$52,Parametri!$C$48,IF(DA5<=Parametri!$C$53,Parametri!$C$50+Parametri!$C$51*ROUND((Parametri!$C$53-DA5)/(Parametri!$C$53-Parametri!$C$52),Parametri!$C$58),IF(DA5<=Parametri!$C$54,Parametri!$C$50*ROUND((Parametri!$C$54-DA5)/(Parametri!$C$54-Parametri!$C$53),Parametri!$C$58),0)))+IF(AND(DA5>Parametri!$C$56,DA5<=Parametri!$C$57),Parametri!$C$55,0))*DK5,Parametri!$C$49),(IF(DA5<=Parametri!$C$52,Parametri!$C$48,IF(DA5<=Parametri!$C$53,Parametri!$C$50+Parametri!$C$51*ROUND((Parametri!$C$53-DA5)/(Parametri!$C$53-Parametri!$C$52),Parametri!$C$58),IF(DA5<=Parametri!$C$54,Parametri!$C$50*ROUND((Parametri!$C$54-DA5)/(Parametri!$C$54-Parametri!$C$53),Parametri!$C$58),0)))+IF(AND(DA5>Parametri!$C$56,DA5<=Parametri!$C$57),Parametri!$C$55,0))*DK5)))
DN  Imposta netta dell'anno
    =IF($A5="","",IF(DK5="","",ROUND(MAX(0,DL5-DM5-IF(AND(DA5>Parametri!$C$66,DA5<=Parametri!$C$67),Parametri!$C$65,IF(AND(DA5>Parametri!$C$67,DA5<=Parametri!$C$68),Parametri!$C$65*ROUND((Parametri!$C$68-DA5)/(Parametri!$C$68-Parametri!$C$67),Parametri!$C$58),0))*DK5),2)))
DO  IRPEF di conguaglio attesa
    =IF($A5="","",IF(DK5="","",ROUND(DN5-DC5,2)))
DP  Cuneo di conguaglio atteso
    =IF($A5="","",IF(DK5="","",ROUND(IF(DA5<=Parametri!$C$59,ROUND(DA5*IF(DA5*Parametri!$C$73/DB5<=Parametri!$C$60,Parametri!$C$61,IF(DA5*Parametri!$C$73/DB5<=Parametri!$C$62,Parametri!$C$63,Parametri!$C$64)),2),0)-DD5,2)))
DQ  Tratt. integrativo di conguaglio atteso
    =IF($A5="","",IF(DK5="","",ROUND(ROUND(IF(DA5<=Parametri!$C$70,IF(DL5>DM5-Parametri!$C$72*DK5,Parametri!$C$69*DK5,0),IF(AND(DA5<=Parametri!$C$71,DM5>DL5),MIN(Parametri!$C$69*DK5,DM5-DL5),0)),2)-DE5,2)))
DR  C21 Conguaglio
    =IF($A5="","",IF(DK5="","OK",IF(OR(ABS(Q5-DO5)>Parametri!$C$19,ABS(N(CY5)-DP5)>Parametri!$C$19,ABS(N(CZ5)-DQ5)>Parametri!$C$19),"ERRORE","OK")))
```

**Un esempio dal mese di settembre 2026.** Dipendente B027, cliente B: atteso 1.194,70 €, sul cedolino 444,85 €, differenza −749,85 €.

**Cause tipiche.**

- Detrazioni dell'anno intero invece che dei giorni di lavoro: conguaglio troppo leggero.
- Conguaglio non fatto: ritenuta calcolata come in un mese qualsiasi.
- Somma del cuneo non recuperata quando il reddito dell'anno supera i 20.000 €.

**Cosa fare.** Rifare il conguaglio: imposta dell'anno sull'imponibile da gennaio, detrazioni e trattamento integrativo rapportati ai giorni di lavoro, meno quanto trattenuto o erogato; consegnare il conteggio con la CU.

**Limiti.**

- Imponibile da gennaio, giorni e somme dei mesi prima vengono dal cedolino: non sono ricostruiti.
- Nessun altro reddito comunicato dal dipendente (art. 23 c. 4): con un precedente datore di lavoro il conguaglio cambia.
- Alla cessazione si recupera tutto subito: le rate (oltre 60 €) valgono per il conguaglio di fine anno.
