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
