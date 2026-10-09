"""Le cifre citate nel README sono quelle che il modello produce."""

import pandas as pd

import build_rapporto as B
import config as C
import robustezza


def test_readme_aggiornato(out):
    f = B.fatti(out, pd.read_csv(C.REPORT / "robustezza.csv"), robustezza.errore_coerente())
    readme = (C.ROOT / "README.md").read_text(encoding="utf-8")
    attese = [
        f"**{f['segnalazioni']} segnalazioni su {f['cedolini']} cedolini e {len(C.CLIENTI)} F24**",
        f"{f['alta']} ad alta priorità", f"**{f['sotto_minimo']} dipendenti sotto il minimo:**",
        B.euro(f["arretrati_minimo"]), B.euro(-f["f24_c"]), B.euro(f["nov_aumento"]), B.euro(f["nov_assorbito"]),
        f"**{B.euro(f['nov_da_pagare'])} al mese**", f"{f['trovati']} trovati su {f['inseriti']}",
        B.euro(f["coerente"]["netto_giusto"] - f["coerente"]["netto_pagato"]),
        f"Su {B.num(f['prove'], 0)} alterazioni casuali",
    ]
    import statistica
    v = statistica.valutazione().set_index("metodo")
    s35, rg = v.loc["Statistico, z oltre 3,5"], v.loc["Regole (C01-C10)"]
    n = lambda r, k: int(r[k])          # una riga di DataFrame misto torna in float: 9.0
    attese.append(f"trova {n(s35, 'trovati')} cedolini sbagliati\n  su {n(s35, 'errori')}, "
                  f"con {n(s35, 'falsi_allarmi')} "
                  f"falsi allarmi; le regole {n(rg, 'trovati')} su {n(rg, 'errori')}")
    assert not [a for a in attese if a not in readme]
