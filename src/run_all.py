"""
Tutto in un comando:

    python src/run_all.py

dati sintetici -> controlli -> foglio di calcolo con le formule -> prova di robustezza -> rapporto.
Deterministico: stessi dati, stessi risultati.
"""
import time

import build_foglio
import build_rapporto
import controlli
import genera
import report_html
import robustezza


def main() -> None:
    start = time.perf_counter()
    genera.main()
    o = controlli.run()
    o["anomalie"].to_csv(controlli.C.REPORT / "anomalie.csv", index=False, float_format="%.2f")
    f = build_foglio.build(o)
    print(f"foglio -> deliverables/foglio_controllo_cedolini.xlsx ({len(f.checks)} confronti con Python)")
    rob = robustezza.run()
    rob.to_csv(controlli.C.REPORT / "robustezza.csv", index=False)
    build_rapporto.write(o, rob, robustezza.errore_coerente())
    report_html.build()
    print("rapporto -> report/rapporto.md, report/index.html")
    print(f"fatto in {time.perf_counter() - start:.1f}s")


if __name__ == "__main__":
    main()
