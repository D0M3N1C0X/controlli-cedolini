"""Le cifre citate nel README sono quelle che il modello produce."""

import pandas as pd

import build_rapporto as B
import config as C
import robustezza


def test_readme_aggiornato(out):
    f = B.fatti(out, pd.read_csv(C.REPORT / "robustezza.csv"), robustezza.errore_coerente())
    readme = (C.ROOT / "README.md").read_text(encoding="utf-8")
    eur = lambda x: f"€{x:,.2f}"
    attese = [
        f"**{f['segnalazioni']} flags on {f['cedolini']} payslips and {len(C.CLIENTI)} F24 payments**",
        f"{f['alta']} high priority", f"**{f['sotto_minimo']} employees below the minimum:**",
        eur(f["arretrati_minimo"]), eur(-f["f24_c"]), eur(f["nov_aumento"]), eur(f["nov_assorbito"]),
        f"**{eur(f['nov_da_pagare'])} a month**", f"{f['trovati']} found out of {f['inseriti']}",
        eur(f["coerente"]["netto_giusto"] - f["coerente"]["netto_pagato"]),
        f"On {f['prove']:,} random alterations",
    ]
    import statistica
    v = statistica.valutazione().set_index("metodo")
    s35, rg = v.loc["Statistico, z oltre 3,5"], v.loc["Regole (C01-C14)"]
    n = lambda r, k: int(r[k])          # una riga di DataFrame misto torna in float: 9.0
    attese.append(f"finds {n(s35, 'trovati')} wrong payslips out of {n(s35, 'errori')}, "
                  f"with {n(s35, 'falsi_allarmi')} false alarms; "
                  f"the rules find {n(rg, 'trovati')} of {n(rg, 'errori')}")
    assert not [a for a in attese if a not in readme]
