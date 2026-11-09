"""Lo strumento nel browser dà gli stessi risultati di Python."""
import shutil
import subprocess

import pytest

import build_web
import config as C


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js non installato")
def test_il_javascript_riproduce_python():
    build_web.write_vectors()
    r = subprocess.run(["node", str(C.ROOT / "tests" / "js" / "check_controlli.mjs")], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "formato di Excel italiano" in r.stdout


def test_testi_in_due_lingue_completi_e_aggiornati():
    """Ogni controllo ha nome, descrizione e cosa fare in italiano e in inglese, e web/testi.json è aggiornato."""
    import json

    import controlli
    testi = build_web.texts()
    for lingua in ("it", "en"):
        assert set(testi[lingua]) == set(controlli.CONTROLLI)
        assert all(v["nome"] and v["descrizione"] and v["cosa_fare"] for v in testi[lingua].values())
    assert json.loads((C.ROOT / "web" / "testi.json").read_text(encoding="utf-8")) == testi


def test_la_pagina_legge_ogni_colonna_dei_cedolini():
    """Ogni colonna di data/cedolini.csv che i controlli leggono ha il suo campo nella pagina, con l'etichetta nelle
    due lingue: una colonna senza campo resta fuori dal file letto, e il controllo che la usa tace senza dirlo."""
    import csv
    import re
    app = (C.ROOT / "web" / "app.js").read_text(encoding="utf-8")
    blocco = app[app.index("const CAMPI_CEDOLINI = ["):app.index("const CAMPI_F24 = [")]
    campi = set(re.findall(r'^\s*\["(\w+)", (?:true|false),', blocco, re.M))
    with C.CEDOLINI.open(encoding="utf-8") as f:
        colonne = next(csv.reader(f))
    assert [c for c in colonne if c not in campi] == []
    for c in campi - {"mese", "matricola", "cliente"}:
        assert app.count(f"f_{c}:") >= 2, c          # etichetta italiana e inglese
