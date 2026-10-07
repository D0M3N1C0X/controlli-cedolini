"""
Scrive report/rapporto.md: il rapporto di controllo del mese, per chi elabora le paghe e per il
responsabile del team. Ogni numero viene da controlli.run() e da robustezza.py.
"""
import pandas as pd

import config as C
import controlli
import robustezza
import statistica

COSA_FARE = {
    "C01": "Aggiornare il tabellare al minimo in vigore e pagare la differenza dei mesi arretrati",
    "C02": "Inserire lo scatto maturato e verificare la data di decorrenza",
    "C03": "Correggere l'aliquota nella posizione del dipendente",
    "C04": "Ricalcolare il rateo includendo scatti e superminimo",
    "C05": "Riallineare il residuo: maturazione del mese non registrata",
    "C06": "Ricontrollare le voci: il cedolino non quadra",
    "C07": "Chiedere al cliente l'evento che giustifica la variazione",
    "C08": "Integrare la delega prima della scadenza del versamento",
    "C09": "Correggere il codice fiscale in anagrafica",
    "C10": "Verificare il cambio con il cliente e con i documenti: se non c'è stato, correggere l'anagrafica",
}


def euro(x, d=2):
    s = f"{abs(x):,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{'−' if x < 0 else ''}{s} €"


def num(x, d=2):
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x, d=0):
    return f"{x * 100:.{d}f}%".replace(".", ",")


def table(head, rows, align):
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


def write(o: dict, rob: pd.DataFrame, coerente: dict) -> dict:
    f = fatti(o, rob, coerente)
    an, n = o["anomalie"], o["riepilogo_novembre"]
    L = []
    add = L.append
    add("# Controlli sui cedolini di settembre 2026")
    add("")
    add(f"**Perimetro:** {f['clienti']} clienti con il CCNL Terziario Confcommercio, {f['cedolini']} cedolini di "
        f"settembre confrontati con quelli di agosto e con gli F24")
    add("**Dati:** Clienti e dipendenti inventati, con errori inseriti apposta; minimi e scatti del CCNL reali, con le "
        "fonti in [docs/fonti.md](../docs/fonti.md)")
    add("**Strumenti:** Uno script Python, lo stesso controllo in un [foglio di calcolo](../deliverables/foglio_controllo_cedolini.xlsx) "
        "e uno [strumento nel browser](https://d0m3n1c0x.github.io/controlli-cedolini/strumento/) dove i file restano sul computer")
    add("")
    add("> Dieci controlli da passare prima di mandare i cedolini al cliente. I controlli ricalcolano "
        "ogni voce dalle regole del contratto, o la confrontano con il mese prima e con l'F24: non serve sapere come "
        "l'ha calcolata il software paghe. "
        "Non è consulenza del lavoro.")
    add("")
    add("## In sintesi")
    add("")
    add(f"- **{f['segnalazioni']} segnalazioni: {f['cedolini_segnalati']} cedolini e {f['f24_segnalati']} F24**, {f['alta']} ad alta priorità; "
        + ", ".join(f"cliente {c} {k}" for c, k in f["per_cliente"].items()) + ".")
    add(f"- **{f['sotto_minimo']} dipendenti sono pagati sotto il minimo:** il tabellare è fermo alla tranche di marzo 2025. Mancano "
        f"{euro(f['arretrati_minimo'])} al mese in tutto, più gli arretrati da novembre 2025.")
    add(f"- **L'F24 del cliente C ha {euro(-f['f24_c'])} di ritenute in meno** della somma dei cedolini: va integrato "
        "prima della scadenza del versamento.")
    add(f"- **Dal 1° novembre 2026 i minimi salgono:** {euro(f['nov_aumento'])} al mese per {f['nov_dipendenti']} "
        f"dipendenti. Il superminimo assorbibile ne copre {euro(f['nov_assorbito'])} in {f['nov_assorbimenti']} casi; "
        f"restano {euro(f['nov_da_pagare'])} al mese, {euro(f['nov_annuo'], 0)} l'anno su 14 mensilità.")
    add(f"- **I controlli trovano ogni alterazione sopra il centesimo** in {num(f['prove_sopra'], 0)} prove casuali "
        f"(sezione 4). Un errore coerente lo vedono solo se nasce da un cambio rispetto al mese prima (C10).")
    add("")

    add("## 1. Le segnalazioni, cedolino per cedolino")
    add("")
    rows = []
    for t in an.itertuples(index=False):
        if t.controllo == "C09":
            atteso, trovato, diff = "valido", f"`{t.trovato}`", "-"
        elif t.controllo == "C10":
            atteso, trovato, diff = t.atteso, t.trovato, "-"
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
    add("*Le ritenute IRPEF dei dati sintetici non sono calcolate con le regole fiscali: servono solo a mostrare la "
        "riconciliazione.*")
    add("")

    add("## 3. La tranche del 1° novembre 2026")
    add("")
    add("Il rinnovo del CCNL Terziario del 22 marzo 2024 alza i minimi a novembre 2026 e di nuovo a febbraio 2027. "
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
    st = sv[sv["metodo"].str.startswith("Statistico")]
    rg = sv[sv["metodo"].str.startswith("Regole")].iloc[0]
    add("**Perché regole e non un modello statistico.** Un rilevatore che non sa nulla del contratto confronta ogni "
        "cedolino con gli altri su quattro rapporti (contributi su lordo, TFR su retribuzione ordinaria, netto su lordo, "
        "netto sul mese prima) e segnala chi si allontana dalla mediana. Sugli stessi errori:")
    add("")
    add(table(["Metodo", "Cedolini sbagliati", "Trovati", "Falsi allarmi", "Precisione"],
              [[r.metodo, r.errori, r.trovati, r.falsi_allarmi, pct(r.precisione)] for r in sv.itertuples(index=False)],
              "lrrrr"))
    add("")
    pt = statistica.per_tipo()
    nomi = {"minimo": "minimi", "scatto": "scatti", "inps": "contributi", "tfr": "TFR", "ferie": "ferie", "netto": "netto",
            "variazione": "variazioni del netto", "codice_fiscale": "codice fiscale", "anagrafica": "anagrafica"}
    visti = ", ".join(nomi[t] for t in pt.loc[pt["trovati_statistico"] > 0, "tipo"])
    add(f"*Il rilevatore vede solo gli errori che spostano un rapporto ({visti}); minimi, scatti, ferie, codice fiscale "
        f"e anagrafica richiedono di conoscere il contratto, e lì non trova nulla. Su un dominio scritto in regole, le "
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

    add("## 5. Come lo userei in un team payroll")
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

    add("## 6. Metodo e limiti")
    add("")
    add("- **Due motori, una risposta.** Gli stessi controlli sono in Python e in formule nel foglio; il foglio "
        "Riconciliazione confronta ogni formula con Python, e la CI ricalcola il foglio con LibreOffice.")
    add("- **Contributi semplificati.** Un'aliquota a carico del dipendente (9,19%) per tutti, senza FIS, CIGS e "
        "contributo aggiuntivo dell'1%: in uso reale l'aliquota viene dalla posizione INPS del cliente.")
    add("- **Scatti al livello attuale.** Il CCNL non rivaluta gli scatti già maturati con il passaggio di livello: chi "
        "ha cambiato livello va controllato a mano.")
    add("- **Un CCNL, un mese.** Tredicesima, quattordicesima, malattia, cessazioni e conguagli non sono controllati.")
    add("")
    C.REPORT.mkdir(exist_ok=True)
    (C.REPORT / "rapporto.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    return f


def main() -> None:
    import report_html
    o = controlli.run()
    rob = robustezza.run()
    write(o, rob, robustezza.errore_coerente())
    report_html.build()
    print("rapporto -> report/rapporto.md, report/index.html")


if __name__ == "__main__":
    main()
