"""
Tutto in un comando:

    python src/run_all.py

dati sintetici -> controlli -> foglio di calcolo con le formule -> prova di robustezza -> anno intero -> rapporto.
Deterministico: stessi dati, stessi risultati.
"""
import time

import anno
import build_catalogo
import build_foglio
import build_rapporto
import build_web
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
    an = anno.run()
    an["mesi"].to_csv(controlli.C.REPORT / "anno_mesi.csv", index=False)
    an["errori"].to_csv(controlli.C.REPORT / "anno_errori.csv", index=False, float_format="%.2f")
    print(f"anno -> report/anno_errori.csv ({int(an['mesi']['cedolini'].sum())} cedolini, "
          f"{len(an['errori'])} errori di configurazione)")
    build_rapporto.write(o, rob, robustezza.errore_coerente(), an)
    report_html.build()
    print("rapporto -> report/rapporto.md, report/index.html")
    build_catalogo.write()
    print("catalogo -> docs/catalogo-controlli.md")
    build_web.write_inputs()
    print(f"strumento -> web/inputs.json; {build_web.write_vectors()} casi di prova per il JavaScript")
    print(f"fatto in {time.perf_counter() - start:.1f}s")


if __name__ == "__main__":
    main()
