"""Il dizionario dei dati descrive ogni colonna, livello, evento e tipo di errore presente nei dati."""
import csv

import config as C

DIZIONARIO = (C.ROOT / "docs" / "dizionario-dati.md").read_text(encoding="utf-8")


def descritto(nome: str) -> bool:
    return f"| `{nome}` |" in DIZIONARIO


def righe(path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_ogni_colonna_ha_una_voce() -> None:
    for path in (C.CCNL, C.DIPENDENTI, C.CEDOLINI, C.F24, C.ERRORI):
        with path.open(encoding="utf-8") as f:
            colonne = next(csv.reader(f))
        assert [c for c in colonne if not descritto(c)] == [], path.name


def test_ogni_livello_evento_e_tipo_ha_una_voce() -> None:
    nomi = ({r["livello"] for r in righe(C.CCNL)} | {r["evento"] for r in righe(C.CEDOLINI) if r["evento"]}
            | {r["tipo"] for r in righe(C.ERRORI)})
    assert sorted(n for n in nomi if not descritto(n)) == []
