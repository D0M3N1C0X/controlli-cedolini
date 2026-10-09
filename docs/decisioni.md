# Registro delle decisioni

Le scelte che determinano i risultati, con l'alternativa che ciascuna ha sostituito. Le regole del contratto e
le loro fonti sono in [fonti.md](fonti.md); qui c'è il metodo.

| # | Decisione | Alternativa scartata | Perché |
|---|---|---|---|
| D1 | Ogni controllo ricalcola il valore atteso dalle regole del contratto e lo confronta con il cedolino | Confrontare il cedolino solo con il mese prima | Il confronto col mese prima non vede un errore che si ripete ogni mese. Il ricalcolo è indipendente da come il software paghe ha calcolato |
| D2 | Tolleranza di un centesimo (un centesimo di giorno per le ferie) | Tolleranza zero, o una percentuale | Con tolleranza zero ogni differenza di arrotondamento diventa un allarme; una percentuale nasconderebbe errori piccoli sugli importi grandi |
| D3 | Arrotondare come ROUND di Excel ovunque: 15 cifre significative, metà per eccesso | L'arrotondamento di Python e di pandas (metà al pari, sul valore binario) | Python, foglio e strumento nel browser devono dare lo stesso risultato al centesimo, anche sui totali e sulle differenze |
| D4 | Contributi sull'imponibile arrotondato all'euro (F10) | Aliquota sul lordo al centesimo | È così che l'imponibile si espone in UniEmens e che lo calcolano i software paghe: senza, il controllo darebbe falsi allarmi di pochi centesimi su quasi ogni cedolino vero |
| D5 | Una sola segnalazione C06 per cedolino: se il lordo non torna, il netto non si controlla | Segnalare lordo e netto separatamente | Il netto dipende dal lordo: due segnalazioni per lo stesso errore raddoppiano il lavoro di chi le legge |
| D6 | C07 segnala un netto oltre il 20% sopra o sotto il mese prima solo se manca un evento | Una soglia statistica, o nessun controllo di variazione | Un evento dichiarato (assunzione, straordinari, part-time) spiega la variazione; senza, la variazione è il segnale |
| D7 | C10 confronta l'anagrafica con il mese prima | Nessun controllo sull'anagrafica | Un livello cambiato senza evento dà un cedolino che torna in ogni voce. C10 lo vede se nasce da un cambio; se è sbagliato dall'assunzione resta invisibile, e il limite è dichiarato e tenuto vero da un test |
| D8 | Regole esplicite, non un modello che impara le anomalie | Un rilevatore statistico | Misurato sugli stessi dati (`statistica.py`): le regole trovano 28 cedolini sbagliati su 28 senza falsi allarmi, il rilevatore circa un terzo con falsi allarmi, e non vede il contratto |
| D9 | Tre versioni degli stessi controlli (Python, foglio con formule, browser) verificate tra loro in CI | Una sola versione | Ogni squadra lavora con uno strumento diverso. Tre versioni che concordano sono anche un controllo l'una dell'altra: il confronto ha già trovato errori veri |
| D10 | Dati sintetici con errori inseriti apposta e registrati | Dati veri | I cedolini sono dati personali. Con errori noti si misurano richiamo e falsi allarmi, cosa impossibile su dati veri senza una revisione manuale completa |
| D11 | Lo strumento gira tutto nel browser, senza server | Un'applicazione con caricamento dei file | I file non lasciano il computer: nessun trattamento di dati personali da autorizzare, nessuna installazione |
| D12 | Nell'F24 si riconciliano solo le ritenute 1001 e i contributi a carico dei dipendenti | Ricostruire tutta la sezione INPS | Il modello non ha la quota a carico dell'azienda; la semplificazione è dichiarata nel dizionario dei dati e nei limiti |
| D13 | La tranche di novembre si assorbe solo con superminimo assorbibile, fino al minore tra superminimo e aumento | Assorbire sempre, o mai | È la regola dell'assorbimento; l'assorbibilità sta nella lettera di assunzione, e per questo è un dato da verificare cliente per cliente |
