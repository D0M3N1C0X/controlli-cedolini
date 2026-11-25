"""
Scrive report/rapporto.md: il rapporto di controllo del mese, per chi elabora le paghe e per il
responsabile del team. Ogni numero viene da controlli.run() e da robustezza.py.
"""
import pandas as pd

import anno
import config as C
import controlli
import fonti
import ponte
import robustezza
import statistica

COSA_FARE = {
    "C01": "Aggiornare il tabellare al minimo in vigore e pagare la differenza dei mesi arretrati",
    "C02": "Inserire lo scatto maturato e verificare la data di decorrenza",
    "C03": "Correggere l'aliquota nella posizione INPS del cliente: CIGS e FIS dipendono dalla media dei dipendenti "
           "nel semestre; sopra 4.685 € al mese si aggiunge l'1%",
    "C04": "Ricalcolare il rateo includendo scatti e superminimo",
    "C05": "Riallineare il residuo: maturazione del mese non registrata",
    "C06": "Ricontrollare le voci: il cedolino non quadra",
    "C07": "Chiedere al cliente l'evento che giustifica la variazione",
    "C08": "Integrare la delega prima della scadenza del versamento",
    "C09": "Correggere il codice fiscale in anagrafica",
    "C10": "Verificare il cambio con il cliente e con i documenti: se non c'è stato, correggere l'anagrafica",
    "C11": "Ricontare i dodicesimi dalla data di assunzione e correggere i ratei prima della tredicesima di dicembre",
    "C12": "Ricalcolare la mensilità con i dodicesimi giusti, da gennaio per la tredicesima e da luglio per la "
           "quattordicesima, e regolare la differenza: pagarla se manca, recuperarla se è stata pagata in più",
    "C13": "Ricalcolare le ferie non godute con la quota giornaliera del CCNL (1/26 della retribuzione mensile, 1/22 "
           "nella Logistica) e regolare la differenza: pagarla se manca, recuperarla se è in più",
    "C14": "Verificare la data della lettera. Licenziamento: i giorni di preavviso non lavorati si pagano come "
           "indennità sostitutiva. Dimissioni: il preavviso non dato si può trattenere come indennità a carico "
           "del dipendente",
    "C15": "Ricalcolare l'indennità sulla retribuzione del mese prima × mensilità / 12 / 30, al 50% dal 4° al 20° "
           "giorno e al 66,66% dopo (80% nei pubblici esercizi; niente per gli impiegati dell'industria), e "
           "correggere il conguaglio con l'INPS nel flusso UniEmens",
    "C16": "Applicare la regola del CCNL. Terziario: dal quinto evento dell'anno la carenza non si paga, salvo "
           "ricovero, prognosi di almeno 12 giorni, terapie salvavita o gravidanza. Metalmeccanico: dal quarto evento "
           "breve il 66%, poi il 50%. Turismo: si paga se la malattia supera i 5 giorni. Se è dovuta e manca, pagarla",
    "C17": "Ricalcolare l'indennità all'80% della retribuzione media giornaliera, ratei compresi, e correggere il "
           "conguaglio con l'INPS; l'integrazione al 100% resta a carico dell'azienda",
    "C18": "Rifare la maturazione dei permessi con le ore del CCNL (Terziario 72 o 56 di riduzione d'orario più 32 "
           "di ex festività; Metalmeccanico e Turismo 104; Logistica 72), in proporzione al part-time e con la regola "
           "dei nuovi assunti dove c'è",
    "C19": "Rifare il conteggio: coefficiente ISTAT del mese giusto (dal 15 in poi conta il mese), imposta "
           "sostitutiva del 17% sulla rivalutazione, 0,50% tolto dalle quote dell'anno; regolare la differenza",
    "C20": "Controllare la tabella IRPEF del software (33% sul secondo scaglione dal 2026), l'ulteriore detrazione e "
           "la somma del cuneo fiscale, il trattamento integrativo; rifare la ritenuta e correggere nel mese dopo",
    "C21": "Rifare il conguaglio: imposta dell'anno sull'imponibile da gennaio, detrazioni e trattamento integrativo "
           "rapportati ai giorni di lavoro, meno quanto trattenuto o erogato; consegnare il conteggio con la CU",
    "C22": "Ricalcolare l'integrazione con la regola del CCNL (Terziario: il netto non sotto il 75% dal 4° al 20° "
           "giorno e il 100% dopo; Metalmeccanico e Logistica: la retribuzione intera meno l'indennità INPS) e pagare "
           "la differenza nel mese dopo",
    "C23": "Ricalcolare l'indennità sui giorni che mancano al preavviso del CCNL, alla retribuzione dell'anno / 12 / "
           "30 per giorno, ratei compresi, e pagare o recuperare la differenza con le competenze di fine rapporto",
}


def euro(x, d=2) -> str:
    s = f"{abs(x):,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{'−' if x < 0 else ''}{s} €"


def num(x, d=2) -> str:
    s = f"{abs(x):,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{'−' if x < 0 and s.strip('0,.') else ''}{s}"


def pct(x, d=0) -> str:
    return f"{x * 100:.{d}f}%".replace(".", ",")


def table(head, rows, align) -> str:
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---:" if a == "r" else "---" for a in align) + "|"]
    return "\n".join(out + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])


def fatti(o: dict, rob: pd.DataFrame, coerente: dict) -> dict:
    an, rn, v = o["anomalie"], o["riepilogo_novembre"], o["valutazione"]
    f24 = o["riconciliazione_f24"].set_index("cliente")
    sopra = rob[rob["ampiezza"] > C.TOLLERANZA]
    return {
        "cedolini": len(o["mese"]), "clienti": len(C.CLIENTI), "segnalazioni": len(an),
        "cedolini_segnalati": an.loc[an["matricola"] != "", "matricola"].nunique(),
        "f24_segnalati": int((an["controllo"] == "C08").sum()),
        "sotto_minimo": int(((an["controllo"] == "C01") & (an["differenza"] < 0)).sum()),
        "alta": int((an["priorita"] == "alta").sum()), "media": int((an["priorita"] == "media").sum()),
        "per_cliente": an.groupby("cliente").size().reindex(list(C.CLIENTI), fill_value=0),
        "f24_c": float(f24.loc["C", "diff_ritenute"]),
        "nov_da_pagare": float(rn["da_pagare"].sum()), "nov_aumento": float(rn["aumento"].sum()),
        "nov_assorbito": float(rn["assorbito"].sum()), "nov_annuo": float(rn["costo_annuo"].sum()),
        "nov_assorbimenti": int(rn["con_assorbimento"].sum()), "nov_dipendenti": int(rn["dipendenti"].sum()),
        "inseriti": int(v["inseriti"].sum()), "trovati": int(v["trovati"].sum()), "falsi": int(v["falsi_allarmi"].sum()),
        "prove": len(rob), "prove_sopra": len(sopra), "trovate_sopra": float(sopra["trovato"].mean()),
        "coerente": coerente,
        "arretrati_minimo": float(-an.loc[an["controllo"] == "C01", "differenza"].sum()),
    }


def write(o: dict, rob: pd.DataFrame, coerente: dict, an_: dict | None = None, po: dict | None = None) -> dict:
    f = fatti(o, rob, coerente)
    an_ = anno.run() if an_ is None else an_
    po = ponte.run() if po is None else po
    an, n = o["anomalie"], o["riepilogo_novembre"]
    L = []
    add = L.append
    add("# Controlli sui cedolini di settembre 2026")
    add("")
    add(f"**Perimetro:** {f['clienti']} clienti con quattro CCNL (Terziario, Metalmeccanico industria, Turismo e "
        f"Logistica), {f['cedolini']} cedolini di settembre confrontati con quelli di agosto e con gli F24")
    add("**Dati:** Clienti e dipendenti inventati, con errori inseriti apposta; minimi, scatti e regole dei CCNL reali, con le "
        "fonti in [docs/fonti.md](../docs/fonti.md)")
    add("**Strumenti:** Uno script Python, lo stesso controllo in un [foglio di calcolo](../deliverables/foglio_controllo_cedolini.xlsx) "
        "e uno [strumento nel browser](https://d0m3n1c0x.github.io/controlli-cedolini/strumento/) dove i file restano sul computer")
    add("")
    add("> Ventitré controlli da passare prima di mandare i cedolini al cliente. I controlli ricalcolano "
        "ogni voce dalle regole del contratto e dell'INPS, o la confrontano con il mese prima e con l'F24: "
        "non serve sapere come l'ha calcolata il software paghe. "
        "Non è consulenza del lavoro.")
    add("")
    add("## In sintesi")
    add("")
    add(f"- **{f['segnalazioni']} segnalazioni: {f['cedolini_segnalati']} cedolini e {f['f24_segnalati']} F24**, {f['alta']} ad alta priorità; "
        + ", ".join(f"cliente {c} {k}" for c, k in f["per_cliente"].items()) + ".")
    add(f"- **{f['sotto_minimo']} dipendenti sono pagati sotto il minimo:** il tabellare è fermo alla tranche precedente "
        f"del loro CCNL, o senza l'elemento perequativo nella Logistica. Mancano {euro(f['arretrati_minimo'])} al mese "
        "in tutto, più gli arretrati dalla tranche mancata.")
    add(f"- **L'F24 del cliente C ha {euro(-f['f24_c'])} di ritenute in meno** della somma dei cedolini: va integrato "
        "prima della scadenza del versamento.")
    add(f"- **Dal 1° novembre 2026 i minimi del Terziario salgono:** {euro(f['nov_aumento'])} al mese per "
        f"{f['nov_dipendenti']} dipendenti. Il superminimo assorbibile ne copre {euro(f['nov_assorbito'])} in {f['nov_assorbimenti']} casi; "
        f"restano {euro(f['nov_da_pagare'])} al mese, {euro(f['nov_annuo'], 0)} l'anno su 14 mensilità.")
    add(f"- **I controlli trovano ogni alterazione sopra il centesimo:** tutte le {num(f['prove_sopra'], 0)} delle "
        f"{num(f['prove'], 0)} prove casuali che superano il centesimo (sezione 4). Un errore coerente lo vedono solo se nasce da un cambio rispetto al mese prima (C10).")
    e = an_["errori"]
    reg = e[e["tipo"] == "regola"]
    add(f"- **Su un anno intero, nove errori di configurazione del software paghe** (sezione 5): i "
        f"{len(reg)} errori di regola sono segnalati dal primo mese e in ogni mese dopo; dei "
        f"{len(e) - len(reg)} di anagrafica, uno sbagliato dall'assunzione non lo vede nessun controllo, gli altri due "
        "li vede C10 una volta sola. L'anno pulito non dà falsi allarmi.")
    add("- **Gli stessi cedolini alimentano gli altri strumenti** (sezione 6): l'estratto per il kit della trasparenza "
        "retributiva dà gli stessi divari al codice del kit e a questo, e INPS e TFR tornano con il modello del costo "
        "del lavoro.")
    add("")

    add("## 1. Le segnalazioni, cedolino per cedolino")
    add("")
    rows = []
    for t in an.itertuples(index=False):
        if t.controllo == "C09":
            atteso, trovato, diff = "valido", f"`{t.trovato}`", "-"
        elif t.controllo in ("C10", "C11"):
            atteso, trovato, diff = t.atteso, t.trovato, "-"
        elif t.controllo == "C16":            # la quota di carenza dovuta, contro l'importo pagato
            atteso, trovato, diff = f"carenza {t.atteso}", euro(t.trovato), "-"
        elif t.controllo == "C18":
            atteso, trovato, diff = f"{num(t.atteso, 2)} ore", f"{num(t.trovato, 2)} ore", f"{num(t.differenza, 2)} ore"
        elif t.controllo == "C14":
            d = 0 if float(t.atteso).is_integer() else 1          # mezza giornata nelle dimissioni della Logistica
            atteso, trovato, diff = f"{num(t.atteso, d)} gg", f"{num(t.trovato, 0)} gg", f"{num(t.differenza, d)} gg"
        elif t.controllo == "C05":
            atteso, trovato, diff = f"{num(t.atteso, 2)} gg", f"{num(t.trovato, 2)} gg", f"{num(t.differenza, 2)} gg"
        else:
            atteso, trovato, diff = euro(t.atteso), euro(t.trovato), euro(t.differenza)
        rows.append([t.matricola or "F24", t.cliente, t.controllo, t.priorita, atteso, trovato, diff])
    add(table(["Matricola", "Cliente", "Controllo", "Priorità", "Atteso", "Trovato", "Differenza"], rows, "lllrrrr"))
    add("")
    add("**Cosa fare, per controllo**")
    add("")
    presenti = [k for k in controlli.CONTROLLI if k in set(an["controllo"])]
    add(table(["Controllo", "Cosa fare"], [[f"{k} {controlli.CONTROLLI[k][0]}", COSA_FARE[k]] for k in presenti], "ll"))
    add("")
    add("*C07 non dice che il cedolino è sbagliato: dice che il netto è cambiato di oltre il 20% senza un evento "
        "registrato. Le assunzioni del mese, gli straordinari dichiarati e il passaggio a part-time non sono segnalati.*")
    add("")

    add("## 2. F24 contro cedolini")
    add("")
    rec = o["riconciliazione_f24"]
    add(table(["Cliente", "Ritenute in F24 (1001)", "Ritenute nei cedolini", "Differenza", "Contributi in F24",
               "Contributi nei cedolini", "Differenza"],
              [[r.cliente, euro(r.ritenute_1001), euro(r.irpef), euro(r.diff_ritenute), euro(r.contributi_dipendente),
                euro(r.contributi_inps), euro(r.diff_contributi)] for r in rec.itertuples(index=False)], "lrrrrrr"))
    add("")
    add("*Le ritenute dei cedolini seguono le regole IRPEF 2026, che C20 ricalcola: qui conta che la delega porti la "
        "loro somma.*")
    add("")

    add("## 3. La tranche del 1° novembre 2026")
    add("")
    add("Il rinnovo del CCNL Terziario del 22 marzo 2024 alza i minimi a novembre 2026 e di nuovo a febbraio 2027; "
        "gli altri tre CCNL hanno la prossima tranche nel 2027 (Logistica a gennaio, Metalmeccanico e Turismo a "
        "giugno), e i loro clienti non sono in questa tabella. "
        "Per ogni dipendente: l'aumento del livello, riproporzionato al part-time; quanto ne assorbe il superminimo, "
        "se la lettera di assunzione lo dice assorbibile; quanto resta da pagare.")
    add("")
    add(table(["Cliente", "Dipendenti", "Aumento al mese", "Assorbito", "Da pagare al mese", "Costo annuo (14 mensilità)"],
              [[f"Cliente {r.cliente}", r.dipendenti, euro(r.aumento), euro(r.assorbito), euro(r.da_pagare),
                euro(r.costo_annuo, 0)] for r in n.itertuples(index=False)], "lrrrrr"))
    add("")
    add("*Lordo dipendente, senza i contributi a carico dell'azienda. L'assorbibilità del superminimo dipende dalla "
        "lettera di assunzione e dagli accordi aziendali: va verificata dipendente per dipendente prima di comunicarla.*")
    add("")

    add("## 4. Quanto ci si può fidare dei controlli")
    add("")
    v = o["valutazione"]
    add(f"**Sugli errori inseriti.** {f['trovati']} su {f['inseriti']}, nessun falso allarme. Dimostra che i controlli "
        "fanno quello che dicono, non che troverebbero errori reali: gli errori li ho scelti io.")
    add("")
    add(table(["Controllo", "Errori inseriti", "Trovati", "Mancati", "Falsi allarmi"],
              [[f"{r.controllo} {r.voce}", r.inseriti, r.trovati, r.mancati, r.falsi_allarmi] for r in v.itertuples(index=False)],
              "lrrrr"))
    add("")
    t = robustezza.tabella(rob)
    add(f"**Su alterazioni casuali.** {num(f['prove'], 0)} prove: una voce a caso di un cedolino corretto, cambiata "
        "di un importo a caso. La tabella dice quante volte almeno un controllo se ne accorge.")
    add("")
    amp = list(t.columns)
    add(table(["Voce alterata", *[("± " + num(a, 3 if a < 0.01 else 2) + " €") for a in amp]],
              [[voce.replace("_", " "), *[pct(t.loc[voce, a]) for a in amp]] for voce in t.index], "l" + "r" * len(amp)))
    add("")
    add(f"*Sotto la tolleranza di un centesimo l'alterazione si confonde con un arrotondamento, ed è giusto che passi. "
        f"Sopra, la trovano tutte: {pct(f['trovate_sopra'])}. Per le ferie l'importo è in giorni.*")
    add("")
    sv = statistica.valutazione()
    add("**Perché regole e non un modello statistico.** Un rilevatore che non sa nulla del contratto confronta ogni "
        "cedolino con gli altri dello stesso cliente su quattro rapporti (contributi su lordo, TFR su retribuzione ordinaria, netto su lordo, "
        "netto sul mese prima) e segnala chi si allontana dalla mediana. Sugli stessi errori:")
    add("")
    add(table(["Metodo", "Cedolini sbagliati", "Trovati", "Falsi allarmi", "Precisione"],
              [[r.metodo, r.errori, r.trovati, r.falsi_allarmi, pct(r.precisione)] for r in sv.itertuples(index=False)],
              "lrrrr"))
    add("")
    pt = statistica.per_tipo()
    nomi = {"minimo": "minimi", "scatto": "scatti", "inps": "contributi", "tfr": "TFR", "ferie": "ferie", "netto": "netto",
            "variazione": "variazioni del netto", "codice_fiscale": "codice fiscale", "anagrafica": "anagrafica",
            "ratei": "ratei", "tredicesima": "mensilità aggiuntive", "ferie_liquidate": "ferie non godute",
            "preavviso": "preavviso", "tfr_liquidato": "TFR liquidato", "malattia": "malattia", "carenza": "carenza",
            "maternita": "maternità", "permessi": "permessi", "irpef": "IRPEF del mese", "conguaglio": "conguaglio",
            "integrazione": "integrazione del datore",
            "indennita_preavviso": "indennità di preavviso"}
    uscita = {"tredicesima", "ferie_liquidate", "preavviso", "tfr_liquidato", "conguaglio", "indennita_preavviso"}
    visti = ", ".join(nomi[t] for t in pt.loc[(pt["trovati_statistico"] > 0) & ~pt["tipo"].isin(uscita), "tipo"])
    add(f"*Il rilevatore confronta ogni cedolino con quelli dello stesso cliente, perché posizioni INPS diverse non "
        f"sono anomalie. Vede solo gli errori che spostano un rapporto ({visti}); minimi, scatti, ferie, codice "
        f"fiscale, anagrafica, IRPEF, assenze e permessi richiedono di conoscere il contratto e le regole INPS, e lì non trova "
        f"nulla. I cedolini di uscita li segnala "
        f"tutti, giusti o sbagliati, perché il netto salta rispetto al mese prima: così prende anche gli errori di "
        f"cessazione, ma i cedolini di uscita corretti diventano falsi allarmi. Su un dominio scritto in regole, le "
        f"regole vincono; la statistica serve dove una regola non c'è.*")
    add("")
    c = f["coerente"]
    add(f"**Il limite, e come C10 lo restringe.** Un errore coerente passa i controlli aritmetici: il dipendente "
        f"{c['matricola']} è assunto al 4° livello; inserito al 5° e ricalcolato da capo, il cedolino torna in ogni voce e "
        f"prende {euro(c['netto_giusto'] - c['netto_pagato'])} netti in meno al mese. Se l'errore nasce da un cambio "
        f"rispetto al mese prima, senza un evento che lo spieghi, lo trova C10: i due errori di anagrafica inseriti "
        f"(un livello, un superminimo azzerato) sono segnalati. Resta invisibile solo se è sbagliato fin "
        f"dall'assunzione: lì serve il confronto con i documenti del cliente, lettera di assunzione e mansioni.")
    add("")

    sezione_anno(add, an_)
    sezione_ponte(add, po)

    add("## 7. Come lo userei in un team payroll")
    add("")
    add("1. **Prima dell'invio, ogni mese:** l'export del software paghe entra nello script o nel foglio; si guardano "
        "solo le righe segnalate, a partire dalla priorità alta.")
    add("2. **C07 diventa una domanda al cliente,** non un errore: se lo straordinario c'è, si registra l'evento e il "
        "mese dopo non torna.")
    add("3. **Prima di ogni tranche contrattuale:** la tabella di novembre dice al cliente quanto costa l'aumento e chi "
        "assorbe, prima del cedolino e non dopo.")
    add("4. **Il passo successivo** è collegarlo all'export reale e misurare quante segnalazioni sono giuste nei primi "
        "due mesi, per tarare la soglia di C07.")
    add("")

    add("## 8. Metodo e limiti")
    add("")
    add("- **Due motori, una risposta.** Gli stessi controlli sono in Python e in formule nel foglio; il foglio "
        "Riconciliazione confronta ogni formula con Python, e la CI ricalcola il foglio con LibreOffice.")
    add("- **Contributi per posizione.** L'aliquota a carico del dipendente viene dalla media del semestre e dal "
        "settore del cliente (Parametri): va presa dalla sua posizione INPS, non stimata.")
    add("- **Scatti al livello attuale.** Il CCNL non rivaluta gli scatti già maturati con il passaggio di livello: chi "
        "ha cambiato livello va controllato a mano.")
    add("- **Quattro CCNL, impiegati.** Ogni cliente ha il suo contratto; nei dati d'esempio ci sono solo impiegati: "
        "operai e personale viaggiante hanno altre regole di malattia e preavviso e non sono controllati.")
    add("- **Un mese alla volta.** Ogni controllo guarda il mese e quello prima: le quote di malattia valgono per i "
        "primi periodi, e un evento lungo va ricontato a mano (C22). L'anno della sezione 5 mette in fila dodici "
        "mesi, ma ogni mese è ancora controllato solo col precedente.")
    add("")
    sezione_fonti(add)
    C.REPORT.mkdir(exist_ok=True)
    (C.REPORT / "rapporto.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    return f


def sezione_anno(add, a: dict) -> None:
    """Sezione 5: l'anno intero e gli errori di configurazione (anno.py)."""
    mesi, e = a["mesi"], a["errori"]
    ced, segn = int(mesi["cedolini"].sum()), len(a["segnalazioni"])
    extra = len(a["extra"])
    add("## 5. Un anno intero e gli errori di configurazione")
    add("")
    add(f"**Perché.** Gli errori inseriti e le prove casuali toccano una voce di un cedolino. Un software paghe "
        "configurato male sbaglia la regola, per tutti i dipendenti del cliente e per tutti i mesi, e ricalcola a valle: "
        "lordo, contributi, imponibile, IRPEF e netto tornano fra loro. Per vedere cosa succede, i dipendenti "
        f"dell'anagrafica passano un anno intero, gennaio-dicembre 2026: {num(ced, 0)} cedolini mensili e "
        f"{extra} cedolini a parte di quattordicesima (luglio) e tredicesima (dicembre), con le tranche dei minimi "
        "nel mese in cui entrano in vigore (Metalmeccanico e Turismo a giugno, Terziario a novembre), gli scatti che "
        "maturano, ferie, permessi, straordinari, tre passaggi di livello e una trasformazione in part-time.")
    add("")
    add(f"**L'anno pulito: {segn} segnalazioni su {num(ced + extra, 0)} cedolini.** Nessun falso allarme in "
        "nessun mese, compresi giugno e novembre, quando cambiano i minimi. Ma i cedolini li genera lo stesso codice che scrive le regole: dice che i "
        "controlli non inventano errori dove le regole sono rispettate, non quanti falsi allarmi darebbe un export "
        "reale. Gli eventi contano: se i quattro eventi legittimi non fossero registrati sul cedolino, "
        f"le segnalazioni sarebbero {len(a['senza_evento'])} "
        f"({', '.join(f'{c} {n}' for c, n in a['senza_evento']['controllo'].value_counts().sort_index().items())}), "
        "ed è giusto: un cambio di livello o di orario senza un documento è una domanda da fare al cliente.")
    add("")
    add("**Nove errori di configurazione.** Ognuno su un cliente o su un dipendente, da un mese a dicembre. "
        "*Esposti*: i cedolini che l'errore cambia (mensili e mensilità aggiuntive); *segnalati*: quelli su cui almeno un "
        "controllo scatta. L'effetto è la differenza nell'anno rispetto all'anno pulito, dal lato del dipendente.")
    add("")
    add(table(["Errore", "Tipo", "Cliente", "Dal", "Esposti", "Segnalati", "Prima segnalazione", "Controlli",
               "Netto nell'anno", "Contributi"],
              [[f"{r.codice} {r.titolo}", r.tipo, r.cliente, r.dal, r.esposti, r.segnalati,
                r.primo_segnalato or "mai", r.controlli or "nessuno", euro(r.netto_anno), euro(r.contributi_anno)]
               for r in e.itertuples(index=False)], "lllrrrllrr"))
    add("")
    regola, anag = e[e["tipo"] == "regola"], e[e["tipo"] == "anagrafica"]
    subito = int((regola["primo_segnalato"] == regola["primo_esposto"]).sum())
    k = e.set_index("codice")
    add(f"**Un errore nella regola si vede subito, e ogni mese.** {subito} dei {len(regola)} errori di regola sono "
        "segnalati nel primo mese in cui cambiano un cedolino, e poi in ogni mese dopo, perché i controlli ricalcolano "
        "la regola da capo e non si fidano del software. Quanti cedolini espongono dipende dall'errore, non dai "
        f"controlli: gli scaglioni IRPEF del 2025 toccano solo chi supera i 28.000 € l'anno ({k.loc['K4', 'esposti']} "
        f"cedolini su {k.loc['K4', 'dipendenti'] * 12}), lo scatto anticipato solo il mese prima della maturazione "
        f"({k.loc['K5', 'esposti']} cedolini). Le ferie a 22 giorni non cambiano il netto, ma a dicembre il cliente B ha "
        f"{num(-k.loc['K6', 'ferie_dicembre'], 0)} giorni di ferie in meno nei residui dei suoi {k.loc['K6', 'dipendenti']} "
        "dipendenti: quattro a testa, meno per chi è entrato nell'anno. Quello che sfugge sono le mensilità aggiuntive costruite su una base "
        f"sbagliata: C12 rifà il conto sul tabellare del cedolino, e quel tabellare l'ha già segnalato C01. Con il CCNL "
        f"a 13 mensilità (K3) la quattordicesima di luglio non viene pagata affatto ({euro(-k.loc['K3', 'mensilita_aggiuntive'])} "
        "nel cliente A): nessun controllo guarda un cedolino che non c'è, ma C11 vede i ratei di quattordicesima a zero "
        "da gennaio.")
    add("")
    add(f"**Un errore nell'anagrafica si vede una volta, o mai.** Il livello sbagliato dall'assunzione (K7) espone "
        f"{k.loc['K7', 'esposti']} cedolini e non ne segnala nessuno: {euro(k.loc['K7', 'netto_anno'])} netti in più "
        "nell'anno e nessun controllo lo vede, perché ogni voce torna con il livello inserito. Il part-time inserito a "
        f"giugno senza lettera (K8) e il superminimo assorbito ma non assorbibile (K9) li trova C10, ma una volta sola, "
        "nel mese in cui l'anagrafica cambia: dal mese dopo il dato sbagliato è la nuova base e tutto torna. Se quella "
        "segnalazione si chiude senza guardare la lettera di assunzione, l'errore resta per sempre: "
        f"{euro(-k.loc['K8', 'netto_anno'])} netti in meno in sette mesi per K8. Per questo C10 è ad alta priorità.")
    add("")
    add("**Cosa ne segue.** I controlli aritmetici bastano per le regole: tranche, aliquote, scaglioni, divisori, "
        f"ferie. Per l'anagrafica ({len(anag)} errori su {len(e)}) serve un confronto con i documenti almeno una volta: "
        "all'assunzione, a ogni segnalazione C10, e a campione una volta l'anno.")
    add("")


_mese = fonti.nome_mese


def sezione_fonti(add) -> None:
    """In coda a Metodo e limiti: fino a quando vale ogni parametro con una data (fonti.py)."""
    s = fonti.prima_scadenza()
    primi = [x.fonte for x in fonti.scadenze() if x.al == s.al]
    add("")
    add(f"**Le fonti al mese chiuso, {_mese(fonti.ULTIMO_MESE_CHIUSO)}.** Ogni parametro che cambia nel tempo ha "
        "una data; un test ferma la pipeline se uno non copre il mese controllato. I primi a scadere, a fine "
        f"{_mese(s.al)}, sono IRPEF, detrazioni, cuneo e prima fascia INPS ({', '.join(primi)}): vanno riletti a "
        "gennaio 2027.")
    add("")
    add(table(["Parametro", "Fonte", "Vale fino a", "Letto alla fonte", "Il prossimo valore"],
              [[x.parametro, x.fonte, _mese(x.al), x.letto, x.prossima] for x in fonti.scadenze()], "lllll"))


def sezione_ponte(add, p: dict) -> None:
    """Sezione 6: dai cedolini dell'anno alla trasparenza retributiva e al costo del lavoro (ponte.py)."""
    e, ind, cat, t, ivs = p["estratto"], p["indicatori"], p["categorie"], p["tfr"], p["ivs"]
    ptk = p["ptk"]
    add("## 6. Il ponte con la trasparenza retributiva e il costo del lavoro")
    add("")
    add("**Perché.** I cedolini sono la fonte dei dati che chiedono la direttiva (UE) 2023/970 sulla trasparenza "
        "retributiva e il budget del personale. Se le voci vanno nel posto sbagliato, il divario retributivo è "
        "sbagliato prima di cominciare. Questa sezione collega i cedolini dell'anno (sezione 5) agli altri due "
        "strumenti del portfolio: [pay-transparency-readiness-kit]"
        f"({ponte.PTK_REPO}) e [workforce-cost-model]({ponte.WCM_REPO}).")
    add("")
    d = p["dizionario"]
    add("**Ogni voce del cedolino ha una natura.** Il kit misura la retribuzione su tutte le voci (direttiva) e, per "
        "l'Italia, sulle sole voci fisse e continuative (il livello retributivo del recepimento, come lo legge il kit). "
        "La tabella dice dove va ogni voce nell'estratto del kit:")
    add("")
    add(table(["Voce del cedolino", "Colonna del kit", "Natura", "Perché"],
              [[r.voce.replace("_", " "), r.colonna_ptk or "fuori", r.natura, r.motivo] for r in d.itertuples(index=False)],
              "llll"))
    add("")
    uguali = ptk is not None and all(
        abs((ptk["clienti"][r.country][k] or 0) - (0 if pd.isna(getattr(r, k)) else getattr(r, k))) < 1e-9
        for r in ind.itertuples(index=False) for k in ptk["clienti"][r.country] if k not in ("workers", "women", "men"))
    add(f"**L'estratto.** {len(e)} dipendenti, la retribuzione pagata da gennaio a dicembre 2026 e le ore contrattuali "
        "del periodo, nel formato \"anno di riferimento\" del kit, un datore di lavoro per cliente "
        "([data/ponte/estratto_ptk.csv](../data/ponte/estratto_ptk.csv)). Gli indicatori dell'articolo 9 calcolati qui "
        + (f"e quelli del codice del kit, al commit {ptk['kit_commit']}, sullo stesso file coincidono su tutti i "
           f"{len(ind)} clienti" if uguali else "e quelli del kit NON coincidono")
        + ": la CI rifà il conto col kit a ogni modifica.")
    add("")
    add(table(["Cliente", "Dipendenti", "Donne", "Divario orario medio", "Mediano", "Divario annuo medio",
               "Variabili: donne / uomini che le ricevono"],
              [[r.country, r.workers, r.women, pct(r.a_mean_gap_hourly, 1), pct(r.c_median_gap_hourly, 1),
                pct(r.a_mean_gap_annual, 1), f"{pct(r.e_share_women_receiving)} / {pct(r.e_share_men_receiving)}"]
               for r in ind.itertuples(index=False)], "lrrrrrr"))
    add("")
    conta = cat["stato"].value_counts()
    add("*Un divario positivo vuol dire donne pagate meno. Annuo e orario differiscono per il part-time: la paga "
        "annua lo conta, quella oraria no, ed è per questo che la direttiva chiede tutti e due. Nessun cliente "
        "ha 100 dipendenti, la soglia più bassa dell'obbligo di relazione dell'articolo 9; il diritto di "
        "informazione dell'articolo 7 vale per tutti. I dati sono inventati: i divari dicono che il ponte funziona, "
        "non qualcosa sui clienti.*")
    add("")
    add(f"**Le categorie sono i livelli del CCNL.** Lo stesso lavoro o un lavoro di pari valore, dentro un cliente, "
        f"secondo la classificazione del contratto: {len(cat)} categorie, {conta.get('da giustificare', 0)} con un "
        f"divario orario di almeno il 5%, {conta.get('sotto il 5%', 0)} sotto, {conta.get('un solo sesso', 0)} con un "
        "solo sesso ([report/ponte_categorie.csv](ponte_categorie.csv)). Nei livelli del CCNL il minimo è uguale per "
        "tutti: un divario viene da scatti (anzianità), superminimi, part-time e straordinari, cioè da quello che il "
        "kit chiede di giustificare con criteri oggettivi. Un livello sbagliato in anagrafica (K7 della sezione 5) "
        "sposta una persona di categoria: per la trasparenza è un errore doppio.")
    add("")
    w = p["wcm"]
    add(f"**Il costo del lavoro: due repository, gli stessi conti.** workforce-cost-model calcola il costo italiano dal "
        f"lato del datore; il suo config.py è copiato al commit {ponte.WCM_COMMIT} con il checksum fissato. "
        f"IVS: {pct(ivs['datore'], 2)} a carico del datore lì, {pct(ivs['dipendente'], 2)} del dipendente qui, "
        f"{pct(ivs['somma'], 2)} in tutto, l'aliquota del Fondo pensioni lavoratori dipendenti. "
        f"TFR: dodici quote mensili dei cedolini contro la retribuzione dell'anno / {num(w['TFR_DIVISOR'], 1)} del "
        f"modello, per i {len(t)} dipendenti con un anno intero allo stesso contratto: differenza mediana "
        f"{euro(t['differenza'].median())}, la più grande {euro(t['differenza'].abs().max())}. La formula è la "
        "stessa; la differenza è di calendario. La quota mensile proietta la retribuzione del mese su tutte le "
        "mensilità, la quota dell'anno guarda quello che è stato pagato: la tredicesima con la tranche di novembre, una "
        "quattordicesima che copre meno di dodici mesi per chi è entrato l'anno prima. L'articolo 2120 del codice "
        "civile guarda la retribuzione dell'anno: le quote mensili sono un acconto, da allineare a dicembre.")
    add("")
    add(f"*Due cose che il modello di costo non fa, senza che il costo cambi. Lo 0,50% dell'imponibile che si toglie "
        f"dal TFR e si versa all'INPS (L. 297/1982, art. 3) sposta {euro(t['contributo_050'].sum(), 0)} l'anno dal "
        "fondo TFR ai contributi per questi dipendenti, ma il datore paga lo stesso totale. E le altre voci INPS e "
        f"INAIL del datore ({pct(w['IT_OTHER'], 1)} nel modello) sono illustrative lì: qui la posizione INPS di "
        "ogni cliente (CIGS, FIS) è nei parametri, ed è da lì che il modello dovrebbe prenderle per un cliente "
        "vero.*")
    add("")


def main() -> None:
    import report_html
    o = controlli.run()
    rob = robustezza.run()
    write(o, rob, robustezza.errore_coerente())
    report_html.build()
    print("rapporto -> report/rapporto.md, report/index.html")


if __name__ == "__main__":
    main()
