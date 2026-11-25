"""
Gli indicatori dell'articolo 9(1) calcolati dal codice di pay-transparency-readiness-kit sull'estratto italiano.

    python tools/ptk_indicatori.py PERCORSO_DEL_KIT

Gira con la sola cartella src del kit sul percorso (i due progetti hanno moduli con lo stesso nome, come config):
legge data/ponte/estratto_ptk.csv e data/ponte/griglia_ptk.csv, chiama workers.derive e article9.indicators del
kit, cliente per cliente, e scrive data/ponte/indicatori_ptk.json. La CI lo fa girare sul kit al commit fissato in
src/ponte.py e controlla che il file non cambi; tests/test_ponte.py controlla che dica le stesse cose di ponte.py.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PONTE = ROOT / "data" / "ponte"
CHIAVI = ["workers", "women", "men", "a_mean_gap_hourly", "a_mean_gap_annual", "b_mean_gap_components",
          "c_median_gap_hourly", "c_median_gap_annual", "d_median_gap_components", "e_share_women_receiving",
          "e_share_men_receiving", "f_q1_share_women", "f_q2_share_women", "f_q3_share_women", "f_q4_share_women"]


def main(kit: Path) -> None:
    sys.path.insert(0, str(kit / "src"))
    import article9
    import pandas as pd
    import workers
    workers.JOB_EVALUATION = PONTE / "griglia_ptk.csv"
    p = pd.read_csv(PONTE / "estratto_ptk.csv")
    w = workers.derive(p)
    commit = subprocess.run(["git", "-C", str(kit), "rev-parse", "--short", "HEAD"], capture_output=True,
                            text=True).stdout.strip()
    out = {"kit_commit": commit, "clienti": {}}
    for c in sorted(w["country"].unique()):
        ind = article9.indicators(w[w["country"] == c])
        out["clienti"][c] = {k: (None if ind[k] != ind[k] else round(float(ind[k]), 10)) for k in CHIAVI}
    (PONTE / "indicatori_ptk.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"indicatori del kit ({commit}) -> data/ponte/indicatori_ptk.json")


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
