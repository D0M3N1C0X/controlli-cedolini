"""Il foglio di calcolo dà gli stessi risultati di Python, formula per formula."""
import pytest

formulas = pytest.importorskip("formulas")

import build_foglio  # noqa: E402
import check_workbook  # noqa: E402
from deterministic import same_content  # noqa: E402


@pytest.fixture(scope="module")
def foglio(out, tmp_path_factory):
    path = tmp_path_factory.mktemp("f") / "foglio.xlsx"
    return build_foglio.build(out, path), path


def test_ogni_formula_torna_con_python(foglio, capsys):
    f, path = foglio
    values = check_workbook.values_from_formulas(path)
    assert check_workbook.check(values, f.wb.sheetnames, len(f.checks)) == 0, capsys.readouterr().out


def test_un_valore_sbagliato_viene_visto(foglio, tmp_path):
    from openpyxl import load_workbook
    f, path = foglio
    wb = load_workbook(path)
    ws = wb["Riconciliazione"]
    row = next(r for r in range(7, 7 + len(f.checks)) if isinstance(ws[f"D{r}"].value, float))
    ws[f"D{row}"].value += 0.01
    broken = tmp_path / "rotto.xlsx"
    wb.save(broken)
    assert check_workbook.check(check_workbook.values_from_formulas(broken), wb.sheetnames, len(f.checks)) == 1


def test_il_foglio_e_riproducibile(out, tmp_path):
    a, b = tmp_path / "a.xlsx", tmp_path / "b.xlsx"
    build_foglio.build(out, a)
    build_foglio.build(out, b)
    assert same_content(a.read_bytes(), b.read_bytes())
