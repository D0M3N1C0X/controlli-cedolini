# Dizionario dei dati

I file in `data/`. Tutti sintetici tranne `ccnl_terziario.csv`, che riporta le tabelle del contratto (fonti in
[fonti.md](fonti.md)). `tests/test_docs.py` fallisce se una colonna, un livello, un evento o un tipo di errore
compare nei dati senza una voce qui.

## `data/ccnl_terziario.csv`: le tabelle del CCNL Terziario Confcommercio

Una riga per livello. Importi in euro al mese, a tempo pieno.

| Colonna | Tipo | Significato |
|---|---|---|
| `livello` | testo | Il livello di inquadramento (elenco sotto) |
| `paga_base` | euro | Paga base dal 1° novembre 2025 |
| `contingenza` | euro | Indennità di contingenza più EDR |
| `altri_elementi` | euro | Altri elementi della retribuzione tabellare (F02) |
| `minimo_2025_03` | euro | Minimo tabellare dal 1° marzo 2025: paga base, altri elementi, contingenza |
| `minimo_2025_11` | euro | Minimo dal 1° novembre 2025: quello che i controlli applicano a settembre 2026 |
| `minimo_2026_11` | euro | Minimo dal 1° novembre 2026: la tranche di cui si calcola il costo |
| `minimo_2027_02` | euro | Minimo dal 1° febbraio 2027, l'ultima tranche del rinnovo |
| `scatto` | euro | Importo di uno scatto di anzianità a tempo pieno (F03) |

| Livello | Significato |
|---|---|
| `Quadri` | Quadri |
| `1` | Primo livello |
| `2` | Secondo livello |
| `3` | Terzo livello |
| `4` | Quarto livello, il più numeroso nei dati |
| `5` | Quinto livello |
| `6` | Sesto livello |
| `7` | Settimo livello |

## `data/dipendenti.csv`: l'anagrafica dei 119 dipendenti in forza ad agosto

I tre assunti a settembre (B200, B201, B202) compaiono solo in `cedolini.csv`, con l'evento `assunzione`.

| Colonna | Tipo | Significato |
|---|---|---|
| `matricola` | testo | Identificativo del dipendente: lettera del cliente e numero |
| `cliente` | testo | `A`, `B` o `C` (descritti in `src/config.py`) |
| `codice_fiscale` | testo | Codice fiscale formalmente valido di una persona inventata, con comune estero (`Z...`) |
| `sesso` | testo | `F` o `M`, serve solo a costruire il codice fiscale |
| `livello` | testo | Il livello di inquadramento |
| `data_assunzione` | data | Data di assunzione, da cui si contano gli scatti |
| `part_time` | numero | Percentuale di tempo pieno: 1, 0,75 o 0,5 |
| `superminimo` | euro | Superminimo individuale al mese |
| `superminimo_assorbibile` | `True`/`False` | Se il superminimo può assorbire gli aumenti contrattuali: nella realtà sta nella lettera di assunzione |

## `data/cedolini.csv`: i cedolini di agosto e settembre 2026

Una riga per dipendente e mese. Gli importi sono quelli "trovati" che i controlli verificano: contengono gli
errori elencati in `errori_inseriti.csv`.

| Colonna | Tipo | Significato |
|---|---|---|
| `mese` | testo | `2026-08` (mese precedente) o `2026-09` (mese controllato) |
| `matricola` | testo | Il dipendente |
| `cliente` | testo | Il cliente |
| `codice_fiscale` | testo | Come risulta sul cedolino, a volte trascritto male di proposito |
| `livello` | testo | Livello sul cedolino |
| `data_assunzione` | data | Data di assunzione sul cedolino |
| `part_time` | numero | Percentuale di tempo pieno sul cedolino |
| `superminimo_assorbibile` | `True`/`False` | Come in anagrafica |
| `evento` | testo | Cosa spiega una variazione nel mese (elenco sotto); vuoto se nulla |
| `tabellare` | euro | Paga base più contingenza e altri elementi, riproporzionati al part-time |
| `scatti_n` | intero | Numero di scatti in pagamento |
| `scatti` | euro | Importo degli scatti |
| `superminimo` | euro | Superminimo pagato nel mese |
| `straordinari` | euro | Straordinari pagati nel mese |
| `lordo` | euro | Totale delle voci di retribuzione |
| `contributi_inps` | euro | Contributi a carico del dipendente: IVS, CIGS, quota FIS e l'1% sopra la prima fascia |
| `imponibile_irpef` | euro | Lordo meno contributi |
| `irpef` | euro | Ritenuta IRPEF del mese (C20); nel cedolino di uscita, il conguaglio (C21): negativa se è un rimborso |
| `bonus_cuneo` | euro | Somma del cuneo fiscale erogata nel mese (L. 207/2024, art. 1 c. 4): non concorre al reddito; nel cedolino di uscita, la differenza di conguaglio |
| `trattamento_integrativo` | euro | Trattamento integrativo del mese (D.L. 3/2020); all'uscita, la differenza di conguaglio |
| `imponibile_fiscale_anno` | euro | Solo all'uscita: imponibile fiscale da gennaio, mese di uscita compreso |
| `giorni_lavoro_anno` | giorni | Solo all'uscita: giorni dal 1° gennaio (o dall'assunzione) all'uscita |
| `ritenute_anno_prec` | euro | Solo all'uscita: IRPEF trattenuta nei mesi prima |
| `cuneo_anno_prec` | euro | Solo all'uscita: somma del cuneo fiscale erogata nei mesi prima |
| `ti_anno_prec` | euro | Solo all'uscita: trattamento integrativo erogato nei mesi prima |
| `altre_trattenute` | euro | Trattenute sintetiche (1,5% dell'imponibile), al posto di addizionali e altre voci |
| `netto` | euro | Imponibile meno IRPEF e altre trattenute |
| `quota_tfr` | euro | Quota di TFR maturata nel mese |
| `ferie_maturate` | giorni | Ferie maturate nel mese: 26 l'anno diviso 12 |
| `ferie_godute` | giorni | Ferie godute nel mese |
| `ferie_residuo` | giorni | Residuo ferie a fine mese |
| `ratei_13` | intero | Dodicesimi di tredicesima maturati nell'anno, fino al mese compreso (F11) |
| `ratei_14` | intero | Dodicesimi di quattordicesima maturati da luglio, fino al mese compreso (F11) |
| `data_cessazione` | data | Ultimo giorno di lavoro; vuoto per chi resta |
| `tipo_cessazione` | testo | `dimissioni` o `licenziamento`; vuoto per chi resta |
| `preavviso_giorni` | intero | Giorni di calendario di preavviso dati o ricevuti (F13); vuoto per chi resta |
| `tredicesima` | euro | Tredicesima pagata nel mese: a dicembre o alla cessazione; vuoto se non pagata |
| `quattordicesima` | euro | Quattordicesima pagata nel mese: a luglio o alla cessazione; vuoto se non pagata |
| `ferie_liquidate` | euro | Ferie non godute pagate alla cessazione (F12); vuoto per chi resta |
| `malattia_dal` | data | Primo giorno dell'evento di malattia; vuoto se nel mese non c'è |
| `malattia_al` | data | Ultimo giorno dell'evento di malattia |
| `malattia_evento_n` | intero | Numero dell'evento di malattia nell'anno solare (una ricaduta è lo stesso evento) |
| `malattia_esente` | `true`/`false` | Ricovero, prognosi iniziale di almeno 12 giorni, terapie salvavita o gravidanza: niente limiti alla carenza (F16) |
| `malattia_inps` | euro | Indennità di malattia anticipata per conto dell'INPS (F16, F17) |
| `malattia_carenza` | euro | Integrazione dei primi 3 giorni pagata dall'azienda |
| `maternita_dal` | data | Primo giorno del congedo di maternità; vuoto se nel mese non c'è |
| `maternita_al` | data | Ultimo giorno previsto del congedo |
| `maternita_inps` | euro | Indennità di maternità anticipata per conto dell'INPS (F18) |
| `permessi_maturati` | ore | Ore di riduzione d'orario ed ex festività maturate nel mese (F23) |
| `permessi_goduti` | ore | Ore di permesso godute nel mese |
| `permessi_residuo` | ore | Residuo delle ore di permesso a fine mese |
| `fondo_tfr_prec` | euro | Fondo TFR al 31 dicembre dell'anno prima; solo per chi cessa |
| `tfr_quote_anno` | euro | Quote di TFR lorde dell'anno, fino alla cessazione |
| `imponibile_anno` | euro | Imponibile previdenziale dello stesso periodo, per lo 0,50% (F22) |
| `tfr_liquidato` | euro | TFR lordo liquidato alla cessazione (F19-F22) |

| Evento | Significato |
|---|---|
| `assunzione` | Assunto nel mese: nessun cedolino il mese prima |
| `straordinari` | Straordinari che spiegano un netto più alto |
| `variazione part-time` | Cambio di percentuale di part-time, comunicato |
| `cessazione` | Ultimo cedolino: con data, tipo e preavviso, le mensilità aggiuntive, le ferie non godute e il TFR |
| `malattia` | Un evento di malattia nel mese, con l'indennità INPS e la carenza |
| `maternità` | Inizio del congedo di maternità, con l'indennità INPS |

## `data/f24.csv`: le deleghe F24 di settembre 2026, una per cliente

| Colonna | Tipo | Significato |
|---|---|---|
| `cliente` | testo | Il cliente |
| `mese` | testo | Il mese di riferimento |
| `ritenute_1001` | euro | Ritenute IRPEF versate con codice tributo 1001 |
| `contributi_dipendente` | euro | Contributi a carico dei dipendenti versati (semplificato: nell'F24 vero la sezione INPS riporta il totale, quota azienda compresa) |

## `data/errori_inseriti.csv`: gli errori messi apposta nei dati

Servono a misurare i controlli: ogni errore deve essere trovato, e nient'altro deve essere segnalato.

| Colonna | Tipo | Significato |
|---|---|---|
| `matricola` | testo | Il dipendente; vuoto per l'errore sull'F24 |
| `cliente` | testo | Il cliente |
| `tipo` | testo | Il tipo di errore (elenco sotto), che corrisponde a un controllo |
| `nota` | testo | Cosa è stato alterato, in parole |

| Tipo | Controllo | Errore |
|---|---|---|
| `minimo` | C01 | Tabellare fermo a una tranche vecchia |
| `scatto` | C02 | Scatto maturato non applicato |
| `inps` | C03 | Aliquota della posizione sbagliata, o 1% aggiuntivo dimenticato |
| `tfr` | C04 | TFR calcolato su una base sbagliata |
| `ferie` | C05 | Residuo ferie che non torna |
| `netto` | C06 | Lordo o netto che non quadrano con le voci |
| `variazione` | C07 | Netto cambiato oltre il 20% senza un evento |
| `f24` | C08 | F24 diverso dalla somma dei cedolini |
| `codice_fiscale` | C09 | Codice fiscale trascritto male |
| `anagrafica` | C10 | Livello o superminimo cambiati senza un evento |
| `ratei` | C11 | Dodicesimi di tredicesima o quattordicesima che non corrispondono ai mesi di servizio |
| `tredicesima` | C12 | Mensilità aggiuntiva pagata con i dodicesimi sbagliati |
| `ferie_liquidate` | C13 | Ferie non godute pagate con un divisore diverso da 26 |
| `preavviso` | C14 | Preavviso più corto del minimo del CCNL |
| `malattia` | C15 | Indennità di malattia INPS con la base giornaliera sbagliata |
| `carenza` | C16 | Carenza pagata quando non è più dovuta |
| `maternita` | C17 | Indennità di maternità senza i ratei nella base |
| `permessi` | C18 | Permessi maturati come un tempo pieno con anzianità |
| `tfr_liquidato` | C19 | TFR liquidato con il coefficiente, l'imposta o il contributo sbagliati |
| `irpef` | C20 | Ritenuta con la tabella del 2025, ulteriore detrazione del cuneo non applicata, somma del cuneo non erogata |
| `conguaglio` | C21 | Conguaglio alla cessazione con le detrazioni dell'anno intero, o non fatto |
