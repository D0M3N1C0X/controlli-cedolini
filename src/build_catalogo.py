"""
Il catalogo dei controlli: una scheda per controllo, come la knowledge base interna di un team paghe.

Quello che sta già nel codice si legge dal codice, così il catalogo non può restare indietro: nome, priorità,
cosa fare (controlli.py, build_rapporto.py), la formula del foglio (dal file Excel costruito), un esempio vero
(dalle segnalazioni del mese). A mano ci sono solo la regola in parole, le cause tipiche e i limiti.

    python src/build_catalogo.py
"""
import pandas as pd
from openpyxl import load_workbook

import build_rapporto
import config as C
import controlli

OUT = C.ROOT / "docs" / "catalogo-controlli.md"
FOGLIO = C.DELIVERABLES / "foglio_controllo_cedolini.xlsx"

# Per ogni controllo: dove sta nel foglio (colonne dei valori attesi e dell'esito) e le fonti nel registro.
FOGLIO_COLONNE = {
    "C01": ("Mese", ["X"], "AK"), "C02": ("Mese", ["Y", "Z", "AA"], "AL"), "C03": ("Mese", ["AB"], "AM"),
    "C04": ("Mese", ["AC"], "AN"), "C05": ("Mese", ["AD", "AE"], "AO"), "C06": ("Mese", ["AF", "AG"], "AP"),
    "C07": ("Mese", ["AH", "AI"], "AQ"), "C08": ("F24", ["C", "D", "F", "G"], "H"), "C09": ("Mese", ["AJ"], "AR"),
    "C10": ("Mese", [], "AS"), "C11": ("Mese", ["AW", "AX"], "AY"),
    "C12": ("Mese", ["BF", "BG", "BH", "BI", "BJ"], "BK"), "C13": ("Mese", ["BL"], "BM"),
    "C14": ("Mese", ["BN", "BO"], "BP"), "C15": ("Mese", ["CG", "CH", "CI", "CJ", "CK", "CL"], "CM"),
    "C16": ("Mese", ["CI", "CN"], "CO"), "C17": ("Mese", ["CH", "CP"], "CQ"), "C18": ("Mese", ["CR", "CS", "CT"], "CU"),
    "C19": ("Mese", ["CV", "CW"], "CX"),
    "C20": ("Mese", ["DF", "DG", "DH", "DI"], "DJ"), "C21": ("Mese", ["DK", "DL", "DM", "DN", "DO", "DP", "DQ"], "DR"),
    "C22": ("Mese", ["DV", "DX", "DY", "DZ", "EA", "EB"], "EC"),
}
FONTI = {
    "C01": ["F01", "F02", "F30", "F33", "F38"], "C02": ["F03", "S04", "F30", "F33", "F38"],
    "C03": ["F05", "F10", "F14", "F15", "F31", "F41"], "C04": ["F06", "S03", "F33"], "C05": ["F04", "F32"],
    "C06": ["S01"], "C07": ["S02"], "C08": ["F09"], "C09": ["F08"], "C10": ["S06"], "C11": ["F11", "F30", "F33", "F38"],
    "C12": ["F11", "F30", "F33", "F38"], "C13": ["F12", "F04", "F36", "F38"], "C14": ["F13", "F34", "F36", "F38"],
    "C15": ["F16", "F17", "F35", "F37", "F40"], "C16": ["F16", "F35", "F37", "F39"],
    "C17": ["F17", "F18"], "C18": ["F23", "S07", "F34", "F37", "F38"], "C19": ["F19", "F20", "F21", "F22"],
    "C20": ["F24", "F25", "F26", "F27", "F28", "S08", "S09", "S10", "S11"],
    "C21": ["F24", "F25", "F26", "F27", "F29", "S10", "S11"],
    "C22": ["F16", "F18", "F35", "F39", "F41", "S12"],
}

SCHEDE = {
    "C01": {
        "regola": "Il tabellare è il minimo del livello in vigore (paga base, altri elementi, contingenza ed EDR) per la "
                  "percentuale di part-time, arrotondato al centesimo.",
        "cause": ["La tranche del CCNL non è stata caricata nel software paghe.",
                  "Livello sbagliato in anagrafica.",
                  "Part-time non riproporzionato, o riproporzionato due volte."],
        "limiti": ["Non controlla il superminimo né il suo assorbimento: quello è nel foglio Novembre 2026.",
                   "Quattro CCNL: Terziario, Metalmeccanico industria, Turismo (pubblici esercizi) e Logistica. Il "
                   "CCNL è del cliente (Parametri); un altro contratto richiede la sua tabella e le sue regole."],
    },
    "C02": {
        "regola": "Uno scatto per ogni periodo compiuto dalla data di assunzione, in pagamento dal mese dopo, fino al "
                  "massimo del CCNL: 10 triennali nel Terziario, 5 biennali nel Metalmeccanico e nella Logistica, 6 "
                  "quadriennali nel Turismo; l'importo è quello del livello per il numero di scatti e per il part-time.",
        "cause": ["Scatto maturato e non attivato nel software.",
                  "Data di assunzione sbagliata in anagrafica.",
                  "Scatti rimasti al livello precedente dopo un passaggio.",
                  "Periodicità di un altro CCNL: triennale dove è biennale."],
        "limiti": ["Valorizza tutti gli scatti al livello attuale (S04): chi ha cambiato livello va controllato a mano.",
                   "Non considera anzianità convenzionali o periodi non utili alla maturazione."],
    },
    "C03": {
        "regola": "Il contributo a carico del dipendente è l'imponibile arrotondato all'euro per l'aliquota della "
                  "posizione INPS del cliente: IVS 9,19%, più la CIGS (0,30%) se nel semestre la media supera 15 "
                  "dipendenti, più un terzo del FIS (0,50% fino a 5 dipendenti, 0,80% oltre) se il cliente lo versa "
                  "(un'impresa industriale ha la CIGO, a carico suo); più l'1% sulla parte oltre la prima fascia "
                  "pensionabile mensilizzata (4.685 € nel 2026). Al centesimo. L'imponibile è il lordo senza le "
                  "indennità INPS di malattia e maternità, che non sono retribuzione (F41).",
        "cause": ["Posizione INPS impostata senza CIGS o FIS, o con la CIGS quando la media del semestre è sotto 15.",
                  "Contributo aggiuntivo dell'1% dimenticato sulle retribuzioni alte.",
                  "Imponibile non arrotondato all'euro, o arrotondato due volte."],
        "limiti": ["La media del semestre va presa dalla posizione INPS del cliente: il controllo usa quella indicata.",
                   "Non considera la riduzione del FIS per chi non ha chiesto integrazioni da 24 mesi, né fondi "
                   "bilaterali diversi dal FIS.",
                   "Dal lordo si tolgono solo le indennità INPS: altre voci escluse dall'imponibile non sono gestite."],
    },
    "C04": {
        "regola": "Il rateo mensile di TFR è la retribuzione ordinaria (tabellare, scatti, superminimo) per le "
                  "mensilità del CCNL (14, 13 nel Metalmeccanico; nel Turismo la quattordicesima senza scatti), diviso "
                  "13,5 e diviso 12. Nel mese di malattia si calcola sulla retribuzione normale (art. 2120 c.c.).",
        "cause": ["Base del TFR senza scatti o superminimo.",
                  "Divisore o numero di mensilità sbagliati nella configurazione."],
        "limiti": ["Non include voci variabili non occasionali né la rivalutazione del fondo.",
                   "Non sottrae il contributo dello 0,50% al Fondo pensioni lavoratori dipendenti."],
    },
    "C05": {
        "regola": "Il residuo ferie è il residuo del mese prima più un dodicesimo delle ferie annue del CCNL, meno le "
                  "ferie godute nel mese, a quattro decimali: 26 giorni nel Terziario e nel Turismo, 22 nella Logistica "
                  "(settimana di 5 giorni), nel Metalmeccanico 24 (4 settimane di 6 giorni), 25 oltre 10 anni e 30 "
                  "oltre 18.",
        "cause": ["Maturazione del mese non registrata.",
                  "Ferie godute non scaricate dal residuo.",
                  "Giorno in più del Metalmeccanico oltre i 10 anni non attivato."],
        "limiti": ["Ferie in giorni, non in ore; ROL ed ex festività sono in C18.",
                   "Per chi è assunto nel mese il residuo di partenza è zero."],
    },
    "C06": {
        "regola": "Il lordo è la somma di tabellare, scatti, superminimo e straordinari, con le voci di chi lascia e, "
                  "nel mese di un'assenza, meno la retribuzione dei giorni assenti e più indennità INPS, carenza e "
                  "integrazione; il netto è il lordo meno "
                  "contributi, IRPEF e altre trattenute, più la somma del cuneo fiscale e il trattamento integrativo.",
        "cause": ["Una voce aggiunta a mano e non sommata.",
                  "Una trattenuta inserita due volte."],
        "limiti": ["Una sola segnalazione per cedolino: se il lordo non torna, il netto non si controlla (D5).",
                   "L'IRPEF la ricalcola C20 (C21 all'uscita): qui conta solo che il netto torni con le voci del cedolino."],
    },
    "C07": {
        "regola": "Il netto non deve cambiare di oltre il 20%, in su o in giù, rispetto al mese prima, a meno che il "
                  "cedolino indichi un evento che lo spieghi.",
        "cause": ["Straordinari o arretrati pagati senza un evento dichiarato.",
                  "Voci duplicate, che gonfiano il netto."],
        "limiti": ["La soglia del 20% va tarata sui primi mesi di uso reale (S02).",
                   "Un evento dichiarato spegne il controllo, anche se l'importo è sbagliato."],
    },
    "C08": {
        "regola": "Per ogni cliente, le ritenute versate con il codice tributo 1001 e i contributi a carico dei "
                  "dipendenti nell'F24 sono uguali alla somma dei cedolini del mese.",
        "cause": ["Un dipendente rimasto fuori dalla delega.",
                  "Delega preparata prima di una correzione ai cedolini."],
        "limiti": ["La sezione INPS è semplificata alla sola quota dei dipendenti (D12).",
                   "Le addizionali regionali e comunali (codici 3802 e 3848) non sono riconciliate."],
    },
    "C09": {
        "regola": "Il carattere di controllo del codice fiscale (il sedicesimo) è quello che il DM 23 dicembre 1976 "
                  "ricava dai primi quindici.",
        "cause": ["Codice trascritto a mano con un carattere sbagliato."],
        "limiti": ["Controlla solo il carattere di controllo, non che il codice corrisponda alla persona.",
                   "I codici con omocodia sono validi e passano, come devono."],
    },
    "C10": {
        "regola": "Livello, part-time, superminimo e data di assunzione sono uguali al mese prima, a meno che il "
                  "cedolino indichi un evento.",
        "cause": ["Anagrafica modificata per errore.",
                  "Un cambio vero non comunicato come evento."],
        "limiti": ["Un errore presente fin dall'assunzione non cambia da un mese all'altro e resta invisibile: è il "
                   "limite dichiarato e tenuto vero da un test.",
                   "Chi non ha un cedolino il mese prima non viene confrontato."],
    },
    "C11": {
        "regola": "I dodicesimi di tredicesima (da gennaio) e di quattordicesima (da luglio) sono i mesi di servizio "
                  "nel periodo, fino al mese del cedolino. Il mese di assunzione conta se ha almeno 15 giorni nel "
                  "Terziario e nel Turismo, più di 15 nel Metalmeccanico e nella Logistica; il Metalmeccanico non ha "
                  "la quattordicesima. Alla cessazione, nel Turismo, le frazioni del primo e dell'ultimo mese si "
                  "sommano: un dodicesimo ogni 30 giorni, più uno per il resto di almeno 15.",
        "cause": ["Mese di assunzione con meno giorni di quelli del CCNL contato intero.",
                  "Quattordicesima contata da gennaio invece che da luglio.",
                  "Un dodicesimo perso senza assenze che lo spieghino."],
        "limiti": ["Controlla il numero di dodicesimi, non l'importo (D14).",
                   "Non considera i periodi non retribuiti che riducono i ratei, come l'aspettativa.",
                   "Le colonne dei ratei sono facoltative: senza, C11 non si applica (D15)."],
    },
    "C12": {
        "regola": "Tredicesima e quattordicesima sono la retribuzione mensile (tabellare, scatti e superminimo) per i "
                  "dodicesimi maturati, diviso 12. A dicembre i dodicesimi sono quelli dei ratei; alla cessazione si "
                  "contano fino alla data di uscita, con la regola del CCNL per l'ultimo mese (C11). Nel Turismo la "
                  "quattordicesima si calcola senza gli scatti.",
        "cause": ["Quattordicesima liquidata con i dodicesimi da gennaio invece che da luglio.",
                  "Ultimo mese contato intero con meno di 15 giorni di servizio.",
                  "Mensilità calcolata sulla retribuzione senza scatti o superminimo; nel Turismo, quattordicesima con "
                  "gli scatti."],
        "limiti": ["Non considera i periodi non retribuiti che riducono i dodicesimi, come l'aspettativa.",
                   "Le colonne sono facoltative: se il cedolino non riporta l'importo, C12 non si applica (D16).",
                   "Una quattordicesima pagata a luglio a chi resta è quella del periodo chiuso il 30 giugno (D19). "
                   "Per chi lascia nei primi giorni di luglio, quella del periodo precedente, se non ancora pagata, "
                   "va controllata a mano."],
    },
    "C13": {
        "regola": "Alla cessazione le ferie maturate e non godute si pagano con la quota giornaliera del CCNL per ogni "
                  "giorno di residuo: 1/26 della retribuzione mensile, 1/22 nella Logistica con la settimana di 5 "
                  "giorni.",
        "cause": ["Quota giornaliera calcolata dividendo per 30 invece che per 26, o per 26 dove è 22.",
                  "Residuo ferie di fine rapporto non aggiornato con la maturazione dell'ultimo mese."],
        "limiti": ["Usa il residuo ferie del cedolino, che C05 controlla a parte. C05 conta la maturazione dell'intero "
                   "mese anche per chi lascia a metà: in quel caso il residuo va ricontrollato a mano.",
                   "Non considera i permessi (ROL ed ex festività), che hanno un loro divisore orario (D17)."],
    },
    "C14": {
        "regola": "Il preavviso, in giorni di calendario, è almeno quello del CCNL per livello, anni di servizio "
                  "(fino a 5, dal 6° al 10°, oltre il 10°) e per chi recede: dimissioni o licenziamento. Metalmeccanico "
                  "e Turismo hanno gli stessi termini per tutti e due; nella Logistica le dimissioni dell'impiegato "
                  "hanno metà dei termini del licenziamento. Un mese conta 30 giorni (D29).",
        "cause": ["Tabella delle dimissioni usata per un licenziamento.",
                  "Termini di un altro livello o di un altro CCNL.",
                  "Anni di servizio contati male, sulla soglia dei 5 o dei 10 anni."],
        "limiti": ["Controlla i giorni di preavviso, non l'importo dell'indennità sostitutiva (D18).",
                   "Non applica le anzianità convenzionali che il CCNL riconosce ad alcune categorie, né le regole "
                   "degli operatori di vendita.",
                   "Si applica solo a dimissioni e licenziamento: per giusta causa o altri tipi di cessazione il "
                   "preavviso non è dovuto e il controllo tace."],
    },
    "C15": {
        "regola": "L'indennità di malattia anticipata per conto dell'INPS è il 50% della retribuzione media globale "
                  "giornaliera per i giorni dal 4° al 20° dell'evento e il 66,66% dal 21° al 180°, domeniche comprese; "
                  "la retribuzione media è quella del mese prima per le mensilità diviso 12, divisa per 30 (nel Turismo "
                  "la quattordicesima senza scatti). Nei pubblici esercizi l'indennità è l'80% per tutto il periodo; "
                  "gli impiegati dell'industria (Metalmeccanico) non l'hanno: paga tutto il datore di lavoro.",
        "cause": ["Base giornaliera calcolata dividendo per 26 invece che per 30, o senza i ratei di tredicesima e "
                  "quattordicesima.",
                  "Giorni contati dall'inizio del mese invece che dall'inizio dell'evento.",
                  "Carenza indennizzata dall'INPS, o 66,66% applicato prima del 21° giorno.",
                  "Percentuali generali applicate a un pubblico esercizio, o indennità anticipata a un impiegato "
                  "dell'industria."],
        "limiti": ["Controlla l'indennità INPS; l'integrazione dell'azienda è in C22.",
                   "Gli eventi iniziati prima del mese non sono controllati: la base sarebbe un cedolino che il "
                   "controllo non ha.",
                   "Vale per gli impiegati (D30); operai e ricoveri hanno altre misure."],
    },
    "C16": {
        "regola": "Terziario: i primi 3 giorni si pagano per intero ai primi 2 eventi di malattia dell'anno, al 66% al "
                  "3°, al 50% al 4°, e non più dal 5°; senza limiti per ricovero, prognosi iniziale di almeno 12 "
                  "giorni, terapie salvavita e malattie in gravidanza. Metalmeccanico: per intero, ma dal 4° evento "
                  "dell'anno di non più di 5 giorni al 66% e dal 5° al 50%. Turismo: per intero solo se la malattia "
                  "supera i 5 giorni. Logistica: per intero.",
        "cause": ["Eventi dell'anno non contati: carenza pagata anche dal quinto.",
                  "Regola di un altro CCNL: nel Turismo, carenza non pagata a una malattia di più di 5 giorni.",
                  "Esenzione non registrata, e carenza negata a chi ne ha diritto."],
        "limiti": ["Controlla se la carenza è pagata quando serve, non l'importo: anche quello è sul netto.",
                   "Il numero dell'evento e l'esenzione vengono dal cedolino: una ricaduta conta come lo stesso evento, "
                   "e va registrata così."],
    },
    "C17": {
        "regola": "L'indennità di maternità anticipata per conto dell'INPS è l'80% della retribuzione media globale "
                  "giornaliera del mese prima dell'inizio del congedo, per ogni giorno del mese.",
        "cause": ["Base senza i ratei di tredicesima e quattordicesima.",
                  "Integrazione dell'azienda al 100% registrata come indennità INPS."],
        "limiti": ["Controlla la quota INPS: l'integrazione al 100% del netto per i primi cinque mesi (Terziario) è in "
                   "C22.",
                   "I congedi iniziati prima del mese non sono controllati, per la stessa ragione di C15."],
    },
    "C18": {
        "regola": "Il residuo dei permessi è il residuo del mese prima più un dodicesimo delle ore annue, meno le "
                  "ore godute, in proporzione al part-time. Terziario: 72 ore di riduzione d'orario (56 fino a 15 "
                  "dipendenti) e 32 di ex festività; per chi è entrato dopo il 1° marzo 2011 la riduzione d'orario "
                  "spetta al 50% dopo 2 anni e al 100% dopo 4. Metalmeccanico: 104 ore di PAR. Turismo: 104 ore, con "
                  "la stessa regola dei 2 e 4 anni per chi è entrato dal 2018. Logistica: 40 ore più 32 di "
                  "festività abolite.",
        "cause": ["Riduzione d'orario maturata per intero da un neoassunto.",
                  "Part-time che matura le ore di un tempo pieno.",
                  "Soglia dei 15 dipendenti sbagliata nella configurazione del cliente."],
        "limiti": ["Non riduce la maturazione per assenze non retribuite, né per le articolazioni d'orario che "
                   "assorbono i permessi (39 o 38 ore settimanali).",
                   "Gli anni di anzianità si contano all'ultimo giorno del mese (S07)."],
    },
    "C19": {
        "regola": "Il TFR liquidato è il fondo al 31 dicembre, più la rivalutazione (1,5% annuo fisso per i mesi "
                  "interi e il 75% dell'aumento dell'indice ISTAT FOI su dicembre; il mese conta se si esce dal 15) "
                  "meno l'imposta sostitutiva del 17% sulla rivalutazione, più le quote dell'anno meno lo 0,50% "
                  "dell'imponibile previdenziale.",
        "cause": ["Coefficiente del mese di uscita usato per chi esce prima del 15.",
                  "Imposta sostitutiva non tolta dalla rivalutazione.",
                  "Contributo dello 0,50% non tolto dalle quote dell'anno."],
        "limiti": ["Controlla il lordo: la tassazione separata e le quote versate a fondi pensione o al Fondo di "
                   "Tesoreria dell'INPS restano fuori.",
                   "Fondo al 31 dicembre, quote e imponibile dell'anno vengono dal cedolino, non sono ricalcolati.",
                   "Serve l'indice FOI del mese nei Parametri: per i mesi che mancano il controllo tace."],
    },
    "C20": {
        "regola": "La ritenuta del mese applica all'imponibile fiscale gli scaglioni del 2026 (23%, 33%, 43%) "
                  "ragguagliati al mese, e toglie un dodicesimo della detrazione per lavoro dipendente e "
                  "dell'ulteriore detrazione del cuneo fiscale, calcolate sul reddito presunto dell'anno (imponibile del "
                  "mese per 14 mensilità). Fino a 20.000 € di reddito spetta la somma del cuneo (7,1%, 5,3% o 4,8% "
                  "dell'imponibile del mese), fino a 15.000 € un dodicesimo del trattamento integrativo.",
        "cause": ["Tabella IRPEF del 2025 ancora nel software: 35% invece di 33% sul secondo scaglione.",
                  "Ulteriore detrazione del cuneo fiscale non applicata tra 20.000 e 40.000 € di reddito.",
                  "Somma del cuneo non erogata, o erogata a chi supera i 20.000 €."],
        "limiti": ["Il reddito dell'anno è presunto dall'imponibile del mese (S09): un software che lo stima "
                   "dall'anno progressivo dà ritenute diverse nei mesi, uguali al conguaglio.",
                   "Niente detrazioni per familiari a carico, oneri o altri redditi dichiarati dal dipendente (S11).",
                   "Le mensilità aggiuntive pagate in un mese ordinario si tassano senza detrazioni: il controllo "
                   "vale per i mesi senza tredicesima o quattordicesima.",
                   "Addizionali regionale e comunale fuori dal controllo: si trattengono a rate sull'anno prima."],
    },
    "C22": {
        "regola": "Nel mese di malattia la retribuzione dei giorni di assenza lascia il posto all'indennità INPS, alla "
                  "carenza e all'integrazione del datore di lavoro, che segue il CCNL. Terziario: il netto del mese, "
                  "prima delle altre trattenute, non sta sotto la quota garantita del netto di un mese normale: i "
                  "giorni lavorati per intero, la carenza alla quota dovuta, il 75% dal 4° al 20° giorno, il 100% dal "
                  "21°; nella maternità il 100%. Metalmeccanico e Logistica: indennità INPS più integrazione arrivano "
                  "alla retribuzione intera dei giorni dopo la carenza. Turismo: nessuna integrazione oltre la "
                  "carenza, e il controllo tace.",
        "cause": ["Integrazione non pagata: il software ha registrato solo l'indennità INPS.",
                  "Quote di un altro CCNL: il 75% del Terziario applicato nella Logistica, o l'80% che nel "
                  "Metalmeccanico vale solo dopo i 122 giorni.",
                  "Integrazione calcolata sul lordo dove il CCNL la vuole sul netto."],
        "limiti": ["Il netto normale si calcola con contributi e IRPEF di un mese senza assenze (C03, C20): altre "
                   "trattenute, addizionali e conguagli restano fuori (S12).",
                   "Sul netto il controllo segnala solo un'integrazione in meno: chi paga di più non è un errore.",
                   "Le quote valgono per i primi periodi: dopo 122-214 giorni (Metalmeccanico) o 3-5 mesi "
                   "(Logistica) cambiano, e gli eventi lunghi vanno controllati a mano.",
                   "La retribuzione tolta per l'assenza è in giorni di calendario (D31): un software a giorni "
                   "lavorativi dà un netto diverso, che il controllo sul netto assorbe e quello sul lordo no."],
    },
    "C21": {
        "regola": "Alla cessazione il sostituto fa il conguaglio: imposta dell'anno sull'imponibile fiscale da "
                  "gennaio, meno detrazione per lavoro dipendente e ulteriore detrazione rapportate ai giorni di lavoro "
                  "(con il minimo di 690 € fino a 15.000 €), meno quanto già trattenuto. La somma del cuneo e il "
                  "trattamento integrativo spettanti per il periodo si confrontano con quelli già erogati: la "
                  "differenza si paga o si recupera nel cedolino di uscita.",
        "cause": ["Detrazioni dell'anno intero invece che dei giorni di lavoro: conguaglio troppo leggero.",
                  "Conguaglio non fatto: ritenuta calcolata come in un mese qualsiasi.",
                  "Somma del cuneo non recuperata quando il reddito dell'anno supera i 20.000 €."],
        "limiti": ["Imponibile da gennaio, giorni e somme dei mesi prima vengono dal cedolino: non sono ricostruiti.",
                   "Nessun altro reddito comunicato dal dipendente (art. 23 c. 4): con un precedente datore di "
                   "lavoro il conguaglio cambia.",
                   "Alla cessazione si recupera tutto subito: le rate (oltre 60 €) valgono per il conguaglio di fine anno."],
    },
}


def _numero(v) -> str:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return str(v)
    return build_rapporto.euro(x)


def _giorni(v) -> str:
    return f"{float(v):.4f}".replace(".", ",")


def _esempio(codice: str, an: pd.DataFrame) -> str:
    righe = an[an["controllo"] == codice]
    if righe.empty:
        return "Nessuna segnalazione nel mese di esempio."
    r = righe.iloc[0]
    chi = f"Dipendente {r['matricola']}, cliente {r['cliente']}"
    if codice == "C05":
        return f"{chi}: residuo atteso {_giorni(r['atteso'])} giorni, sul cedolino {_giorni(r['trovato'])}."
    if codice == "C07":
        variazione = float(r["trovato"]) / float(r["atteso"]) - 1
        segno = "+" if variazione > 0 else ""
        return (f"{chi}: netto di agosto {_numero(r['atteso'])}, di settembre {_numero(r['trovato'])} "
                f"({segno}{build_rapporto.pct(variazione)}), nessun evento sul cedolino.")
    if codice == "C08":
        return (f"Cliente {r['cliente']}: somma dei cedolini {_numero(r['atteso'])}, nell'F24 {_numero(r['trovato'])}, "
                f"differenza {_numero(r['differenza'])}.")
    if codice == "C09":
        return f"{chi}: il codice «{r['trovato']}» ha un carattere di controllo non valido."
    if codice == "C14":
        return (f"{chi}: preavviso minimo {float(r['atteso']):.0f} giorni, sul cedolino {float(r['trovato']):.0f} "
                f"giorni.")
    if codice in ("C10", "C11"):
        return f"{chi}: atteso «{r['atteso']}», sul cedolino «{r['trovato']}»."
    return (f"{chi}: atteso {_numero(r['atteso'])}, sul cedolino {_numero(r['trovato'])}, "
            f"differenza {_numero(r['differenza'])}.")


def scheda(codice: str, wb, an: pd.DataFrame) -> list[str]:
    nome, descrizione, priorita = controlli.CONTROLLI[codice]
    s = SCHEDE[codice]
    foglio, attese, esito = FOGLIO_COLONNE[codice]
    ws = wb[foglio]
    righe = [f"## {codice} · {nome}", "",
             f"**Priorità {priorita}.** {descrizione}.", "",
             f"**La regola.** {s['regola']}", "",
             "**Fonti.** " + ", ".join(f"[{f}](fonti.md)" for f in FONTI[codice]) + ".", "",
             f"**Nel foglio** (foglio {foglio}, riga 5; le altre righe sono uguali):", "", "```"]
    for col in [*attese, esito]:
        righe.append(f"{col}  {ws[f'{col}4'].value}")
        righe.append(f"    {ws[f'{col}5'].value}")
    righe += ["```", "",
              f"**Un esempio dal mese di settembre 2026.** {_esempio(codice, an)}", "",
              "**Cause tipiche.**", "", *[f"- {c}" for c in s["cause"]], "",
              f"**Cosa fare.** {build_rapporto.COSA_FARE[codice]}.", "",
              "**Limiti.**", "", *[f"- {x}" for x in s["limiti"]], ""]
    return righe


def testo() -> str:
    wb = load_workbook(FOGLIO)
    an = pd.read_csv(C.REPORT / "anomalie.csv", dtype={"matricola": str}, keep_default_na=False)
    righe = ["# Catalogo dei controlli", "",
             "Una scheda per controllo: cosa controlla, da quale regola, dove sta nel foglio, un esempio vero e cosa "
             "fare. Generato da `src/build_catalogo.py`: nome, priorità, formule ed esempi vengono dal codice e dal "
             "foglio, quindi non restano indietro.", "",
             "| Controllo | Priorità | Cosa controlla |", "|---|---|---|"]
    for codice, (nome, descrizione, priorita) in controlli.CONTROLLI.items():
        righe.append(f"| [{codice} · {nome}](#{codice.lower()}--{nome.lower().replace(' ', '-')}) | {priorita} | "
                     f"{descrizione} |")
    righe.append("")
    for codice in controlli.CONTROLLI:
        righe += scheda(codice, wb, an)
    return "\n".join(righe).rstrip("\n") + "\n"


def write() -> None:
    OUT.write_text(testo(), encoding="utf-8")


if __name__ == "__main__":
    write()
    print(f"catalogo -> {OUT.relative_to(C.ROOT)}")
