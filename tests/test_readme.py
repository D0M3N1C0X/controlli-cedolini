"""Le cifre citate nel README sono quelle che il modello produce."""
from pathlib import Path

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
    assert not [a for a in attese if a not in readme]
