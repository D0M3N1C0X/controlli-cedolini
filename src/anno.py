"""
Un anno intero di cedolini, gennaio-dicembre 2026, e gli errori di configurazione che restano coerenti.

I 69 errori inseriti e le 1.100 alterazioni casuali di robustezza.py toccano una voce di un cedolino di un mese. Un
software paghe configurato male sbaglia in un altro modo: sbaglia la regola, per tutti i dipendenti del cliente e
per tutti i mesi, e ricalcola a valle in modo coerente, così che lordo, contributi, imponibile, IRPEF e netto
tornano fra loro. Qui le due cose si misurano su un anno.

1. **L'anno pulito.** I dipendenti dell'anagrafica, ognuno dal mese di assunzione (o da dicembre 2025, il mese di
   partenza che non si controlla) a dicembre 2026, con le tranche dei minimi nel mese in cui entrano in vigore
   (Turismo e Metalmeccanico a giugno, Terziario a novembre), gli scatti che maturano, ferie, permessi e qualche
   straordinario; la quattordicesima a luglio e la tredicesima a dicembre in un cedolino a parte. Ogni mese passa i
   controlli col mese prima: quello che segnalano è un falso allarme, perché nessun errore è stato inserito.
2. **Nove errori di configurazione.** Ognuno su un cliente (o un dipendente), da un mese a dicembre, ricalcolato a
   cascata come farebbe il software. Per ognuno: i cedolini esposti (quelli che cambiano rispetto all'anno pulito),
   quelli segnalati, il mese della prima segnalazione, i controlli che scattano, e quanto vale l'errore nell'anno.

Il risultato conta più per quello che non trova: un errore nella regola si vede ogni mese, perché i controlli la
ricalcolano da capo; un errore nell'anagrafica fin dall'assunzione non si vede mai, e uno inserito a metà anno si
vede una volta sola, nel mese in cui cambia (C10), poi l'anagrafica sbagliata diventa la base dei mesi dopo.
"""
import random
from dataclasses import dataclass
from datetime import date

import pandas as pd

import config as C
import controlli
import genera
import regole as R

INIZIO = "2025-12"                                   # il mese di partenza: dà il mese prima a gennaio
MESI = [f"2026-{m:02d}" for m in range(1, 13)]
MESE_14, MESE_13 = "2026-07", "2026-12"
# le voci che, se cambiano rispetto all'anno pulito, rendono il cedolino esposto all'errore
VOCI = ["livello", "part_time", "superminimo", "tabellare", "scatti", "lordo", "contributi_inps", "quota_tfr",
        "irpef", "netto", "ferie_maturate", "ferie_residuo", "ratei_13", "ratei_14"]


def successivo(mese: str) -> str:
    a, m = map(int, mese.split("-"))
    return f"{a + m // 12}-{m % 12 + 1:02d}"


def precedente(mese: str) -> str:
    a, m = map(int, mese.split("-"))
    return f"{a - (m == 1)}-{(m - 2) % 12 + 1:02d}"


# ---- Gli errori di configurazione -----------------------------------------------------------------------------
# Ogni errore ha un cliente, un mese da cui vale, un filtro opzionale sul dipendente, e due ganci: `anagrafica`
# cambia la scheda del dipendente prima del cedolino, `cedolino` cambia la regola e ricalcola a valle.

def _ricalcola_fisco(r: dict, **kw) -> dict:
    r["imponibile_irpef"] = R.centesimi(r["lordo"] - r["contributi_inps"])
    return genera.fisco(r, **kw)


def tranche_non_caricata(r: dict, d, mese: str) -> dict:
    k = genera.ccnl(r)
    vecchia = R.colonna_in_vigore(k, "2026-05")            # K1: la tranche del 1° giugno 2026 non entra
    r["tabellare"] = R.tabellare(r["livello"], r["part_time"], vecchia, k)
    return genera.ricalcola(r)


def cigs_mancante(r: dict, d, mese: str) -> dict:
    r["contributi_inps"] = R.contributi(r["lordo"], C.CIGS_SOGLIA - 1, R.fis_cliente(r["cliente"]))
    return _ricalcola_fisco(r)


def tredici_mensilita(r: dict, d, mese: str) -> dict:
    ordinaria = R.centesimi(r["tabellare"] + r["scatti"] + r["superminimo"])
    r["quota_tfr"] = R.centesimi(ordinaria * 13 / C.DIVISORE_TFR / 12)
    r["ratei_14"] = 0
    r.update(R.irpef_mese(r["imponibile_irpef"], 13))
    return genera.netto(r)


def irpef_2025(r: dict, d, mese: str) -> dict:
    return genera.fisco(r, scaglioni=C.SCAGLIONI_IRPEF_2025)


def scatto_anticipato(r: dict, d, mese: str) -> dict:
    k = genera.ccnl(r)
    r["scatti_n"] = R.scatti_maturati(date.fromisoformat(r["data_assunzione"]), successivo(mese), k)
    r["scatti"] = R.scatti_importo(r["livello"], r["scatti_n"], r["part_time"], k)
    return genera.ricalcola(r)


def ferie_22(r: dict, d, mese: str) -> dict:
    sbagliate = R.ferie_mese("logistica")
    r["ferie_residuo"] = round(r["ferie_residuo"] - r["ferie_maturate"] + sbagliate, 4)
    r["ferie_maturate"] = sbagliate
    return r


def livello_sopra(d: pd.Series, mese: str) -> pd.Series:
    livelli = R.regola(genera.ccnl(d))["livelli"]
    d["livello"] = livelli[livelli.index(d["livello"]) - 1]
    return d


def part_time_75(d: pd.Series, mese: str) -> pd.Series:
    d["part_time"] = 0.75
    return d


def superminimo_assorbito(d: pd.Series, mese: str) -> pd.Series:
    k = genera.ccnl(d)
    aumento = (R.tabellare(d["livello"], d["part_time"], R.colonna_in_vigore(k, mese), k)
               - R.tabellare(d["livello"], d["part_time"], R.colonna_in_vigore(k, "2026-10"), k))   # K9: da novembre
    d["superminimo"] = R.centesimi(max(0.0, d["superminimo"] - aumento))
    return d


@dataclass
class Errore:
    codice: str
    titolo: str
    cliente: str
    dal: str
    tipo: str                       # "regola" o "anagrafica"
    cedolino: object = None         # gancio sul cedolino (regola)
    anagrafica: object = None       # gancio sulla scheda (anagrafica), dal mese `dal`
    chi: object = None              # filtro: il primo dipendente del cliente che lo soddisfa
    descrizione: str = ""


ERRORI = [
    Errore("K1", "Tranche di giugno non caricata", "E", "2026-06", "regola", cedolino=tranche_non_caricata,
           descrizione="Il software resta sui minimi del Turismo di giugno 2025 dopo il 1° giugno 2026."),
    Errore("K2", "CIGS non applicata", "F", "2026-01", "regola", cedolino=cigs_mancante,
           descrizione="Media del semestre caricata sotto 15 dipendenti: manca lo 0,30% di CIGS."),
    Errore("K3", "CCNL a 13 mensilità invece di 14", "A", "2026-01", "regola", cedolino=tredici_mensilita,
           descrizione="Nessun rateo di quattordicesima, TFR su 13 mensilità, reddito presunto su 13."),
    Errore("K4", "Scaglioni IRPEF del 2025", "B", "2026-01", "regola", cedolino=irpef_2025,
           descrizione="Il secondo scaglione resta al 35% invece del 33% del 2026."),
    Errore("K5", "Scatto pagato un mese prima", "C", "2026-01", "regola", cedolino=scatto_anticipato,
           descrizione="Lo scatto entra nel mese in cui si compie il triennio, non dal mese dopo."),
    Errore("K6", "Ferie a 22 giorni invece di 26", "B", "2026-01", "regola", cedolino=ferie_22,
           descrizione="Il cliente del Terziario configurato con le ferie annue della Logistica."),
    Errore("K7", "Livello sbagliato dall'assunzione", "B", "2025-12", "anagrafica", anagrafica=livello_sopra,
           chi=lambda d: d["livello"] == "4" and d["data_assunzione"] < "2025-12-01",
           descrizione="Assunto al 4° livello, inserito al 3° fin dal primo cedolino."),
    Errore("K8", "Part-time inserito a giugno senza lettera", "C", "2026-06", "anagrafica", anagrafica=part_time_75,
           chi=lambda d: d["part_time"] == 1.0 and d["data_assunzione"] < "2025-12-01",
           descrizione="Un tempo pieno portato al 75% in anagrafica da giugno, senza un evento che lo spieghi."),
    Errore("K9", "Superminimo assorbito ma non assorbibile", "A", "2026-11", "anagrafica",
           anagrafica=superminimo_assorbito,
           chi=lambda d: d["superminimo"] > 0 and not d["superminimo_assorbibile"]
           and d["data_assunzione"] < "2025-12-01",
           descrizione="Alla tranche di novembre il superminimo cala dell'aumento, ma la lettera non lo consente."),
]


# ---- La generazione ---------------------------------------------------------------------------------------------
# Eventi legittimi dell'anno, registrati sul cedolino col loro evento: un passaggio di livello a marzo nei clienti D,
# E e F (il primo tempo pieno assunto prima del 2024) e una trasformazione in part-time al 50% a settembre nel
# cliente B. Senza l'evento, C10 li segnalerebbe: è quello che deve fare.
PROMOZIONI = {"D": "2026-03", "E": "2026-03", "F": "2026-03"}
PART_TIME = {"B": "2026-09"}


def eventi(a: pd.DataFrame) -> dict:
    """matricola -> (mese, campo, valore, evento)."""
    out = {}
    for cliente, mese in PROMOZIONI.items():
        d = next(d for _, d in a[a["cliente"] == cliente].iterrows()
                 if d["part_time"] == 1.0 and d["data_assunzione"] < "2024-01-01")
        livelli = R.regola(genera.ccnl(d))["livelli"]
        out[d["matricola"]] = (mese, "livello", livelli[livelli.index(d["livello"]) - 1], "passaggio di livello")
    for cliente, mese in PART_TIME.items():
        d = next(d for _, d in a[a["cliente"] == cliente].iloc[::-1].iterrows()
                 if d["part_time"] == 1.0 and d["data_assunzione"] < "2024-01-01")
        out[d["matricola"]] = (mese, "part_time", 0.5, "trasformazione in part-time")
    return out


def dipendenti() -> pd.DataFrame:
    return pd.read_csv(C.DIPENDENTI, dtype={"livello": str})


def _scelto(a: pd.DataFrame, e: Errore) -> str | None:
    if e.chi is None:
        return None
    return next(d["matricola"] for _, d in a[a["cliente"] == e.cliente].iterrows() if e.chi(d))


def _anno_dipendente(d: pd.Series, errore: Errore | None = None, evento: tuple | None = None,
                     registra: bool = True) -> tuple[list[dict], list[dict]]:
    """I cedolini del dipendente, da INIZIO (o dal mese di assunzione) a dicembre, e quelli delle mensilità
    aggiuntive. Un generatore per dipendente: l'errore su un cliente non cambia gli altri."""
    rng = random.Random(f"{C.SEED}-anno-{d['matricola']}")
    residuo, permessi = round(rng.uniform(8, 26), 4), round(rng.uniform(8, 60), 4)
    mesi, extra = [], []
    assunto = d["data_assunzione"][:7]
    for mese in [INIZIO, *MESI]:
        straordinari = R.centesimi(rng.uniform(60, 260)) if rng.random() < 0.12 else 0.0
        godute = 10 if mese == "2026-08" else rng.choice([0, 0, 0, 0, 1, 2, 3])
        p_god = rng.choice([0, 0, 0, 4, 8])
        if mese < assunto:
            continue
        if mese == assunto:
            residuo, permessi = 0.0, 0.0
        x = d.copy()
        if evento and mese >= evento[0]:
            x[evento[1]] = evento[2]
        if errore and errore.anagrafica and mese >= errore.dal:
            x = errore.anagrafica(x, mese)
        r = genera.cedolino(x, mese, rng, residuo, straordinari=straordinari, ferie_godute=min(godute, residuo + 2),
                            permessi_prec=permessi, permessi_goduti=min(p_god, permessi))
        if errore and errore.cedolino and mese >= errore.dal:
            r = errore.cedolino(r, x, mese)
        if evento and mese == evento[0] and registra:
            r["evento"] = evento[3]
        residuo, permessi = r["ferie_residuo"], r["permessi_residuo"]
        mesi.append(r)
        extra += _mensilita_aggiuntive(r, mese, errore)
    return mesi, extra


def _mensilita_aggiuntive(r: dict, mese: str, errore: Errore | None) -> list[dict]:
    """Il cedolino a parte della quattordicesima (luglio) e della tredicesima (dicembre), con le voci che C12 legge.
    Con un CCNL configurato a 13 mensilità (K3) la quattordicesima non c'è: non c'è niente da controllare."""
    k = genera.ccnl(r)
    ass = date.fromisoformat(r["data_assunzione"])
    mensile = R.centesimi(r["tabellare"] + r["scatti"] + r["superminimo"])
    base = {c: r[c] for c in ("mese", "matricola", "cliente", "livello", "data_assunzione", "tabellare", "scatti",
                              "superminimo")}
    if mese == MESE_14 and R.ha_quattordicesima(k) and not (errore and errore.cedolino is tredici_mensilita):
        n = R.dodicesimi_14_pagata(ass, mese, k)
        v = R.mensilita_aggiuntiva(R.base_quattordicesima(mensile, r["scatti"], k), n)
        return [{**base, "voce": "quattordicesima", "quattordicesima": v, "importo": v}]
    if mese == MESE_13:
        v = R.mensilita_aggiuntiva(mensile, R.ratei_13(ass, mese, k))
        return [{**base, "voce": "tredicesima", "tredicesima": v, "importo": v}]
    return []


def genera_anno(errore: Errore | None = None, a: pd.DataFrame | None = None,
                registra: bool = True) -> tuple[pd.DataFrame, pd.DataFrame]:
    """I cedolini dell'anno (tutti i dipendenti, o solo quelli toccati dall'errore) e le mensilità aggiuntive.
    `registra=False`: gli eventi legittimi avvengono, ma il cedolino non li registra."""
    a = dipendenti() if a is None else a
    ev = eventi(a)
    if errore is not None:
        scelto = _scelto(a, errore)
        a = a[a["matricola"] == scelto] if scelto else a[a["cliente"] == errore.cliente]
    mesi, extra = [], []
    for _, d in a.iterrows():
        m, x = _anno_dipendente(d, errore, ev.get(d["matricola"]), registra)
        mesi += m
        extra += x
    return pd.DataFrame(mesi), pd.DataFrame(extra)


# ---- I controlli, mese per mese ---------------------------------------------------------------------------------

def _f24(m: pd.DataFrame) -> pd.DataFrame:
    """L'F24 del mese versato come dicono i cedolini: un errore coerente arriva coerente anche in F24."""
    s = m.groupby("cliente")[["irpef", "contributi_inps"]].sum().map(R.centesimi).reset_index()
    return s.rename(columns={"irpef": "ritenute_1001", "contributi_inps": "contributi_dipendente"})


def controlla(ced: pd.DataFrame, extra: pd.DataFrame) -> pd.DataFrame:
    """Le segnalazioni di ogni mese, col mese prima; e C12 sui cedolini della tredicesima e della quattordicesima."""
    out = []
    for mese in MESI:
        m = ced[ced["mese"] == mese].reset_index(drop=True)
        prec = ced[ced["mese"] == precedente(mese)]
        an, _ = controlli.esegui(m, prec, _f24(m), mese)
        out.append(an.assign(mese=mese))
    for r in ([] if extra.empty else extra.to_dict("records")):
        trovate: list = []

        def segnala(i, codice, atteso, trovato, trovate=trovate) -> None:
            trovate.append((codice, atteso, trovato))
        controlli._cessazione(pd.Series({**r, "data_cessazione": ""}), segnala, 0, r["mese"])
        out += [pd.DataFrame([{"matricola": r["matricola"], "cliente": r["cliente"], "controllo": c,
                               "voce": controlli.CONTROLLI[c][0], "atteso": at, "trovato": tr,
                               "mese": r["mese"] + " " + r["voce"]}]) for c, at, tr in trovate]
    out = [o for o in out if not o.empty]
    cols = ["mese", "matricola", "cliente", "controllo", "voce", "atteso", "trovato"]
    return pd.concat(out)[cols].reset_index(drop=True) if out else pd.DataFrame(columns=cols)


def falsi_allarmi(ced: pd.DataFrame, segn: pd.DataFrame) -> pd.DataFrame:
    """Per mese: cedolini controllati e segnalazioni sull'anno pulito, per controllo."""
    rows = []
    for mese in MESI:
        s = segn[segn["mese"] == mese]
        rows.append({"mese": mese, "cedolini": int((ced["mese"] == mese).sum()), "segnalazioni": len(s),
                     "cedolini_segnalati": s["matricola"].nunique(),
                     "controlli": ", ".join(f"{c} {n}" for c, n in s["controllo"].value_counts().sort_index().items())})
    return pd.DataFrame(rows)


def _esposti(pulito: pd.DataFrame, errato: pd.DataFrame) -> pd.DataFrame:
    """I cedolini dell'errore che cambiano rispetto all'anno pulito, con le differenze di netto e contributi."""
    k = ["mese", "matricola"]
    x = errato.merge(pulito, on=k, suffixes=("", "_pulito"), validate="one_to_one")
    diverso = pd.Series(False, index=x.index)
    for v in VOCI:
        a, b = x[v], x[f"{v}_pulito"]
        if pd.api.types.is_numeric_dtype(a) and pd.api.types.is_numeric_dtype(b):
            diverso |= (a - b).abs() > C.TOLLERANZA / 2
        else:
            diverso |= a.astype(str) != b.astype(str)
    x["esposto"] = diverso
    x["d_netto"] = x["netto"] - x["netto_pulito"]
    x["d_contributi"] = x["contributi_inps"] - x["contributi_inps_pulito"]
    x["d_irpef"] = x["irpef"] - x["irpef_pulito"]
    x["d_tfr"] = x["quota_tfr"] - x["quota_tfr_pulito"]
    x["d_ferie"] = x["ferie_residuo"] - x["ferie_residuo_pulito"]
    return x


def misura(e: Errore, pulito: pd.DataFrame, extra_pulito: pd.DataFrame, segn_pulito: pd.DataFrame) -> dict:
    ced, extra = genera_anno(e)
    segn = controlla(ced, extra)
    chi = set(ced["matricola"])
    x = _esposti(pulito[pulito["matricola"].isin(chi)], ced)
    x = x[x["mese"].isin(MESI)]
    esposti = x[x["esposto"]]
    segn_m = segn[segn["mese"].isin(MESI)]
    chiave = set(zip(segn_m["mese"], segn_m["matricola"], strict=True))
    trovati = [(m, mt) for m, mt in zip(esposti["mese"], esposti["matricola"], strict=True) if (m, mt) in chiave]
    # le mensilità aggiuntive: un importo diverso o un cedolino che manca è esposto
    ep = extra_pulito[extra_pulito["matricola"].isin(chi)]
    k_ex = ["mese", "matricola", "voce"]
    pagate = extra[k_ex + ["importo"]] if not extra.empty else pd.DataFrame(columns=k_ex + ["importo"])
    ex = ep[k_ex + ["importo"]].merge(pagate, on=k_ex, how="left", suffixes=("_pulito", ""))
    ex["importo"] = ex["importo"].astype(float).fillna(0.0)             # un cedolino che manca paga zero
    diff = ex["importo"] - ex["importo_pulito"]
    esposti_extra = int((diff.abs() > C.TOLLERANZA / 2).sum())
    d_extra = float(diff.sum())
    trovati_extra = int(segn["mese"].str.contains(" ").sum())
    # falsi allarmi: segnalazioni su cedolini non esposti che l'anno pulito non aveva
    base = set(zip(segn_pulito["mese"], segn_pulito["matricola"], segn_pulito["controllo"], strict=True))
    nuove = segn_m[pd.Series([(m, mt, c) not in base for m, mt, c in
                              zip(segn_m["mese"], segn_m["matricola"], segn_m["controllo"], strict=True)],
                             index=segn_m.index, dtype=bool)]
    esposti_set = set(zip(esposti["mese"], esposti["matricola"], strict=True))
    fuori = nuove[pd.Series([(m, mt) not in esposti_set for m, mt in zip(nuove["mese"], nuove["matricola"],
                                                                         strict=True)], index=nuove.index, dtype=bool)]
    primo_esp = esposti["mese"].min() if len(esposti) else ""
    mesi_trovati = sorted({m for m, _ in trovati})
    return {"codice": e.codice, "titolo": e.titolo, "tipo": e.tipo, "cliente": e.cliente, "dal": e.dal,
            "descrizione": e.descrizione, "dipendenti": len(chi),
            "esposti": len(esposti) + esposti_extra, "segnalati": len(trovati) + trovati_extra,
            "primo_esposto": primo_esp, "primo_segnalato": mesi_trovati[0] if mesi_trovati else "",
            "mesi_segnalati": len(mesi_trovati),
            "controlli": ", ".join(sorted(set(nuove["controllo"]) | set(segn[segn["mese"].str.contains(" ")]
                                                                       ["controllo"]))),
            "falsi_allarmi": len(fuori),
            "netto_anno": R.centesimi(float(esposti["d_netto"].sum()) + d_extra),
            "contributi_anno": R.centesimi(float(esposti["d_contributi"].sum())),
            "irpef_anno": R.centesimi(float(esposti["d_irpef"].sum())),
            "tfr_anno": R.centesimi(float(esposti["d_tfr"].sum())),
            "mensilita_aggiuntive": R.centesimi(d_extra),
            "ferie_dicembre": round(float(x.loc[x["mese"] == MESI[-1], "d_ferie"].sum()), 2)}


def run() -> dict:
    pulito, extra = genera_anno()
    segn = controlla(pulito, extra)
    errori = pd.DataFrame([misura(e, pulito, extra, segn) for e in ERRORI])
    senza = controlla(*genera_anno(registra=False))
    return {"cedolini": pulito, "extra": extra, "segnalazioni": segn, "mesi": falsi_allarmi(pulito, segn),
            "errori": errori, "eventi": eventi(dipendenti()), "senza_evento": senza}


def main() -> None:
    o = run()
    pd.set_option("display.width", 220)
    print(o["mesi"].to_string(index=False))
    print(o["errori"].drop(columns=["descrizione"]).to_string(index=False))
    print(o["senza_evento"].to_string(index=False))


if __name__ == "__main__":
    main()
