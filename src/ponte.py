"""
Il ponte verso gli altri due strumenti del portfolio: dai cedolini dell'anno (anno.py) all'estratto che legge
pay-transparency-readiness-kit, e i conti italiani confrontati con quelli di workforce-cost-model.

1. **Trasparenza retributiva.** Ogni voce del cedolino ha una natura per la direttiva (UE) 2023/970 e per il
   recepimento italiano, che misura il livello retributivo sulle sole voci fisse e continuative: la tabella VOCI la
   scrive una volta. Con quella, i cedolini di gennaio-dicembre 2026 diventano un estratto nel formato "anno di
   riferimento" del kit (data/ponte/estratto_ptk.csv): retribuzione pagata nell'anno e ore contrattuali del periodo,
   un datore di lavoro per cliente. I divari dell'articolo 9 si calcolano qui, e il kit stesso li ricalcola sullo
   stesso file a un commit fissato (tools/ptk_indicatori.py, nella CI): i due risultati devono coincidere.
2. **Costo del lavoro.** workforce-cost-model calcola il costo italiano dal lato del datore: IVS al 23,81% e TFR =
   retribuzione annua / 13,5. Il suo config.py è copiato a un commit e checksum fissati; qui si controlla che la
   quota IVS del datore più quella del dipendente facciano il 33% del fondo pensioni, e che dodici quote mensili di
   TFR dei cedolini diano la sua quota annua.
"""
import hashlib
import json
import re

import pandas as pd

import anno
import config as C
import regole as R

PTK_REPO = "https://github.com/D0M3N1C0X/pay-transparency-readiness-kit"
PTK_COMMIT = "18be663"
WCM_REPO = "https://github.com/D0M3N1C0X/workforce-cost-model"
WCM_COMMIT = "bdcfa57"
WCM_CONFIG = C.DATA / "source" / "wcm_config.txt"
WCM_SHA256 = "7a70c7db813539b8cb5600ad6ea172945dde4c80407c73f995dc6fac84ff2fc9"
CARTELLA = C.DATA / "ponte"
ESTRATTO = CARTELLA / "estratto_ptk.csv"
GRIGLIA = CARTELLA / "griglia_ptk.csv"
INDICATORI_PTK = CARTELLA / "indicatori_ptk.json"
IVS_TOTALE = 0.33                    # aliquota IVS del Fondo pensioni lavoratori dipendenti (F05)
ORE = 40                             # ore settimanali di riferimento: vedi la nota su ore e divari in estratto()
SETTIMANE = 52                       # la convenzione del kit (WEEKS_PER_YEAR)
SOGLIA = 0.05                        # art. 10(1)(a) della direttiva: un divario di almeno il 5%

# (voce del cedolino, colonna dell'estratto del kit, natura, perché)
VOCI = [
    ("tabellare", "base_pay", "fissa e continuativa", "minimo del livello: retribuzione di base"),
    ("scatti", "base_pay", "fissa e continuativa", "scatti di anzianità: maturano per regola generale"),
    ("superminimo", "base_pay", "fissa e continuativa", "superminimo individuale: pagato ogni mese"),
    ("tredicesima", "base_pay", "fissa e continuativa", "mensilità aggiuntiva dovuta dal CCNL"),
    ("quattordicesima", "base_pay", "fissa e continuativa", "mensilità aggiuntiva dovuta dal CCNL"),
    ("straordinari", "bonus", "variabile", "dipende dalle ore del mese: componente variabile (il kit non ha una "
                                           "colonna per lo straordinario, la colonna bonus è variabile)"),
    ("quota_tfr", "", "esclusa", "accantonamento differito, non pagato nell'anno; liquidato alla cessazione"),
    ("malattia_inps", "", "esclusa", "anticipata per conto dell'INPS: non la paga il datore di lavoro"),
    ("maternita_inps", "", "esclusa", "anticipata per conto dell'INPS: non la paga il datore di lavoro"),
    ("integrazione_datore", "base_pay", "sostitutiva", "prende il posto della retribuzione dei giorni di assenza"),
    ("contributi_inps", "", "esclusa", "trattenuta, non retribuzione"),
    ("irpef", "", "esclusa", "trattenuta, non retribuzione"),
]
COLONNE = ["worker_id", "country", "role", "gender", "weekly_hours", "annual_hours", "base_pay", "payroll_total",
           "bonus", "commission", "shift_allowance", "car_allowance", "period_status"]


def dizionario() -> pd.DataFrame:
    return pd.DataFrame(VOCI, columns=["voce", "colonna_ptk", "natura", "motivo"])


def estratto(ced: pd.DataFrame | None = None, extra: pd.DataFrame | None = None) -> pd.DataFrame:
    """L'anno di riferimento 2026 nel formato del kit. Le ore: tutti i dipendenti di un cliente hanno lo stesso
    orario contrattuale, quindi il numero di ore settimanali scala la paga oraria di tutti allo stesso modo e i
    divari dentro un datore di lavoro non cambiano; conta solo il part-time, mese per mese."""
    if ced is None:
        ced, extra = anno.genera_anno()
    ced = ced[ced["mese"].isin(anno.MESI)]
    d = anno.dipendenti().set_index("matricola")
    rows = []
    for matricola, g in ced.groupby("matricola", sort=True):
        x = extra[extra["matricola"] == matricola]
        voci = {v: 0.0 for v, *_ in VOCI}
        for v in ("tabellare", "scatti", "superminimo", "straordinari"):
            voci[v] = float(g[v].sum())
        for v in ("tredicesima", "quattordicesima"):
            voci[v] = float(x.loc[x["voce"] == v, "importo"].sum())
        col = {c: 0.0 for c in ("base_pay", "bonus", "commission", "shift_allowance", "car_allowance")}
        for v, c, _, _ in VOCI:
            if c:
                col[c] += voci[v]
        ore = float((g["part_time"] * ORE * SETTIMANE / 12).sum())
        ultimo = g.iloc[-1]
        rows.append({"worker_id": matricola, "country": ultimo["cliente"],
                     "role": f"{R.ccnl_cliente(ultimo['cliente'])} {ultimo['livello']}",
                     "gender": d.loc[matricola, "sesso"], "weekly_hours": round(ore / SETTIMANE, 4),
                     "annual_hours": round(ore, 2), **{k: round(v, 2) for k, v in col.items()},
                     "payroll_total": round(sum(col.values()), 2),
                     "period_status": "whole period" if len(g) == len(anno.MESI) else "joined"})
    return pd.DataFrame(rows, columns=COLONNE)


def griglia(e: pd.DataFrame) -> pd.DataFrame:
    """La griglia che il kit chiede per ogni ruolo. Qui le categorie sono i livelli del CCNL, che il kit non conosce:
    gli si dà un punteggio uguale per tutti, che vale solo per far girare i suoi indicatori (a)-(f); i divari per
    categoria li calcola categorie()."""
    roles = sorted(e["role"].unique())
    return pd.DataFrame({"role": roles, "department": [r.split()[0] for r in roles],
                         "job_level": [r.split()[1] for r in roles], "skills": 1, "effort": 1, "responsibility": 1,
                         "working_conditions": 1,
                         "rationale": "categoria = livello del CCNL; punteggio neutro, non usato"})


def _gap(f: pd.Series, m: pd.Series, how: str = "mean") -> float:
    if f.empty or m.empty:
        return float("nan")
    a, b = (f.mean(), m.mean()) if how == "mean" else (f.median(), m.median())
    return float((b - a) / b) if b else float("nan")


def indicatori(e: pd.DataFrame) -> pd.DataFrame:
    """Gli elementi (a)-(f) dell'articolo 9(1) per cliente, con le definizioni del kit (articolo 3(1)): paga oraria
    e annua, componenti variabili tra chi le riceve, bande di quartile per paga oraria dentro il datore di lavoro."""
    w = e.copy()
    w["components"] = w["bonus"] + w["commission"] + w["shift_allowance"] + w["car_allowance"]
    w["total_pay"] = w["base_pay"] + w["components"]
    w["hourly_total"] = w["total_pay"] / (w["weekly_hours"] * SETTIMANE)
    rank = w.groupby("country")["hourly_total"].rank(method="first").astype(int)
    n = w.groupby("country")["worker_id"].transform("size")
    w["quartile"] = ((rank - 1) * 4 // n + 1).clip(upper=4)
    rows = []
    for c, g in w.groupby("country"):
        f, m = g[g["gender"] == "F"], g[g["gender"] == "M"]
        fr, mr = f[f["components"] > 0], m[m["components"] > 0]
        r = {"country": c, "workers": len(g), "women": len(f), "men": len(m),
             "a_mean_gap_hourly": _gap(f["hourly_total"], m["hourly_total"]),
             "a_mean_gap_annual": _gap(f["total_pay"], m["total_pay"]),
             "b_mean_gap_components": _gap(fr["components"], mr["components"]),
             "c_median_gap_hourly": _gap(f["hourly_total"], m["hourly_total"], "median"),
             "c_median_gap_annual": _gap(f["total_pay"], m["total_pay"], "median"),
             "d_median_gap_components": _gap(fr["components"], mr["components"], "median"),
             "e_share_women_receiving": len(fr) / len(f) if len(f) else float("nan"),
             "e_share_men_receiving": len(mr) / len(m) if len(m) else float("nan")}
        for q in (1, 2, 3, 4):
            band = g[w.loc[g.index, "quartile"] == q]
            r[f"f_q{q}_share_women"] = float((band["gender"] == "F").mean()) if len(band) else float("nan")
        rows.append(r)
    return pd.DataFrame(rows)


def categorie(e: pd.DataFrame) -> pd.DataFrame:
    """Il divario di paga oraria per categoria, con la categoria = livello del CCNL dentro il cliente: lo stesso
    lavoro o un lavoro di pari valore secondo la classificazione del contratto. Segnalato al 5% (art. 10)."""
    w = e.assign(hourly=e["payroll_total"] / (e["weekly_hours"] * SETTIMANE))
    rows = []
    for (c, role), g in w.groupby(["country", "role"]):
        f, m = g[g["gender"] == "F"], g[g["gender"] == "M"]
        gap = _gap(f["hourly"], m["hourly"])
        rows.append({"cliente": c, "categoria": role, "donne": len(f), "uomini": len(m), "divario_orario": gap,
                     "stato": "un solo sesso" if f.empty or m.empty
                     else ("da giustificare" if abs(gap) >= SOGLIA else "sotto il 5%")})
    return pd.DataFrame(rows)


# ---- workforce-cost-model ---------------------------------------------------------------------------------------

def wcm() -> dict:
    """I parametri italiani di workforce-cost-model, letti dal suo config.py copiato a un commit fissato."""
    testo = WCM_CONFIG.read_text(encoding="utf-8")
    if hashlib.sha256(WCM_CONFIG.read_bytes()).hexdigest() != WCM_SHA256:
        raise SystemExit(f"{WCM_CONFIG} non corrisponde al checksum fissato: copialo di nuovo da {WCM_REPO} "
                         f"al commit {WCM_COMMIT}")

    def val(nome: str) -> float:
        return float(re.search(rf"^{nome}\s*=\s*([0-9.]+)", testo, flags=re.M).group(1))
    return {"IT_IVS": val("IT_IVS"), "IT_OTHER": val("IT_OTHER"), "TFR_DIVISOR": val("TFR_DIVISOR")}


def tfr_confronto(ced: pd.DataFrame, extra: pd.DataFrame) -> pd.DataFrame:
    """Per chi ha lavorato tutto l'anno: le dodici quote di TFR dei cedolini contro la quota annua del modello di
    costo (retribuzione annua / 13,5, sulle voci di base), e la quota netta dello 0,50% (L. 297/1982, art. 3) che il
    modello non toglie."""
    p = wcm()
    ced = ced[ced["mese"].isin(anno.MESI)]
    rows = []
    for matricola, g in ced.groupby("matricola", sort=True):
        if len(g) < len(anno.MESI) or g["part_time"].nunique() > 1 or g["livello"].nunique() > 1:
            continue                 # un anno intero e lo stesso contratto: altrimenti la base cambia nell'anno
        x = extra[extra["matricola"] == matricola]
        base = float((g["tabellare"] + g["scatti"] + g["superminimo"]).sum() + x["importo"].sum())
        imponibile = float(g["lordo"].sum() + x["importo"].sum())
        rows.append({"matricola": matricola, "cliente": g["cliente"].iloc[0], "retribuzione_annua": base,
                     "tfr_cedolini": float(g["quota_tfr"].sum()), "tfr_modello": base / p["TFR_DIVISOR"],
                     "contributo_050": imponibile * C.CONTRIBUTO_TFR})
    t = pd.DataFrame(rows)
    t["differenza"] = t["tfr_cedolini"] - t["tfr_modello"]
    return t


def costo(e: pd.DataFrame, t: pd.DataFrame) -> pd.DataFrame:
    """Il costo del lavoro dell'anno per cliente con le regole di workforce-cost-model, accanto ai contributi
    a carico dei dipendenti che i cedolini trattengono davvero."""
    p = wcm()
    rows = []
    for c, g in e.groupby("country"):
        lordo = float(g["payroll_total"].sum())
        rows.append({"cliente": c, "dipendenti": len(g), "lordo_anno": lordo,
                     "ivs_datore": lordo * p["IT_IVS"], "altri_datore": lordo * p["IT_OTHER"],
                     "tfr": float(g["base_pay"].sum()) / p["TFR_DIVISOR"],
                     "aliquota_dipendente": R.aliquota_cliente(c)})
    out = pd.DataFrame(rows)
    out["costo_totale"] = out["lordo_anno"] + out["ivs_datore"] + out["altri_datore"] + out["tfr"]
    return out


def run() -> dict:
    ced, extra = anno.genera_anno()
    e = estratto(ced, extra)
    t = tfr_confronto(ced, extra)
    p = wcm()
    return {"dizionario": dizionario(), "estratto": e, "indicatori": indicatori(e), "categorie": categorie(e),
            "wcm": p, "ivs": {"datore": p["IT_IVS"], "dipendente": C.ALIQUOTA_DIPENDENTE,
                              "somma": round(p["IT_IVS"] + C.ALIQUOTA_DIPENDENTE, 6)},
            "tfr": t, "costo": costo(e, t),
            "ptk": json.loads(INDICATORI_PTK.read_text(encoding="utf-8")) if INDICATORI_PTK.exists() else None}


def scrivi() -> dict:
    o = run()
    CARTELLA.mkdir(exist_ok=True)
    o["estratto"].to_csv(ESTRATTO, index=False)
    griglia(o["estratto"]).to_csv(GRIGLIA, index=False)
    o["dizionario"].to_csv(CARTELLA / "dizionario_voci.csv", index=False)
    return o


if __name__ == "__main__":
    o = scrivi()
    pd.set_option("display.width", 220)
    print(o["indicatori"].round(4).to_string(index=False))
    c = o["categorie"]
    print(c["stato"].value_counts().to_dict())
    print(o["ivs"], o["tfr"]["differenza"].abs().max(), len(o["tfr"]))
    print(o["costo"].round(0).to_string(index=False))
