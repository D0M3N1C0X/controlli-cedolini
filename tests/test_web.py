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
