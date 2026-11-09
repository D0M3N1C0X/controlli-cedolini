// Rifà con web/controlli.js ogni caso calcolato in Python. Esce con 1 alla prima differenza.
import { readFileSync } from "node:fs";
import { esegui, novembre, leggiCsv, normalizza, ratei, dodicesimiAllaCessazione, inizio13, inizio14, preavvisoMinimo,
  dodicesimi14Pagata, data, scattiMaturati, carenzaPercentuale, ferieAnnue, integrazioneLorda, quotaNettoGarantita,
  indennitaMalattia }
  from "../../web/controlli.js";

const V = JSON.parse(readFileSync(new URL("../fixtures/js_vectors.json", import.meta.url)));
const close = (a, b) => (typeof a === "number" && typeof b === "number" ? Math.abs(a - b) <= 1e-9 * Math.max(1, Math.abs(b)) : a === b);
let checks = 0, failures = 0;
const expect = (ok, what) => { checks++; if (!ok) { failures++; if (failures <= 20) console.error("differenza:", what); } };

V.cases.forEach((c, k) => {
  const mese = V.mese.map((r) => ({ ...r }));
  for (const [i, voce, v] of c.patch) mese[i][voce] = v;
  const f24 = V.f24.map((r) => ({ ...r }));
  for (const [j, voce, v] of c.f24_patch) f24[j][voce] = v;
  const { anomalie, riconciliazione } = esegui(mese, V.prec, f24, V.ccnl, V.cfg);
  expect(anomalie.length === c.anomalie.length, `caso ${k}: ${anomalie.length} segnalazioni contro ${c.anomalie.length}`);
  c.anomalie.forEach((e, i) => {
    const a = anomalie[i] || {};
    for (const f of ["controllo", "cliente", "matricola", "atteso", "trovato"])
      expect(close(a[f], e[f]), `caso ${k} riga ${i} ${f}: ${a[f]} contro ${e[f]}`);
  });
  c.riconciliazione.forEach((e) => {
    const a = riconciliazione.find((r) => r.cliente === e.cliente);
    expect(a && close(a.diff_ritenute, e.diff_ritenute) && close(a.diff_contributi, e.diff_contributi), `caso ${k} F24 ${e.cliente}`);
  });
  const nov = novembre(mese, V.ccnl, V.cfg);
  c.novembre.forEach((e) => {
    const s = nov.filter((r) => r.cliente === e.cliente);
    for (const f of ["aumento", "assorbito", "da_pagare"]) {
      const tot = Math.round(s.reduce((t, r) => t + r[f], 0) * 100) / 100;
      expect(close(tot, e[f]), `caso ${k} novembre ${e.cliente} ${f}: ${tot} contro ${e[f]}`);
    }
  });
});
// I ratei sui casi limite, gli stessi di tests/test_controlli.py
for (const [assunzione, mese, r13, r14] of [["2015-05-04", "2026-09", 9, 3], ["2026-02-18", "2026-09", 7, 3],
  ["2026-03-17", "2026-09", 7, 3], ["2026-09-01", "2026-09", 1, 1], ["2026-07-20", "2026-09", 2, 2],
  ["2015-05-04", "2026-06", 6, 12], ["2025-12-10", "2026-02", 2, 3]]) {
  const [a13, a14] = ratei(assunzione, mese, V.cfg);
  expect(a13 === r13 && a14 === r14, `ratei ${assunzione} a ${mese}: ${a13}/${a14} contro ${r13}/${r14}`);
}
// Le cessazioni sui casi limite, gli stessi di tests/test_cessazioni.py
for (const [assunzione, cessazione, n13, n14] of [["2015-05-04", "2026-09-30", 9, 3], ["2015-05-04", "2026-09-14", 8, 2],
  ["2015-05-04", "2026-09-15", 9, 3], ["2026-03-18", "2026-09-30", 6, 3], ["2026-03-17", "2026-09-30", 7, 3],
  ["2026-09-10", "2026-09-24", 1, 1], ["2026-09-10", "2026-09-23", 0, 0], ["2020-01-01", "2026-03-31", 3, 9],
  ["2026-10-01", "2026-09-30", 0, 0]]) {
  const a13 = dodicesimiAllaCessazione(assunzione, cessazione, inizio13(cessazione), V.cfg);
  const a14 = dodicesimiAllaCessazione(assunzione, cessazione, inizio14(cessazione), V.cfg);
  expect(a13 === n13 && a14 === n14, `cessazione ${assunzione} al ${cessazione}: ${a13}/${a14} contro ${n13}/${n14}`);
}
for (const [tipo, livello, assunzione, cessazione, giorni] of [["dimissioni", "4", "2021-10-01", "2026-09-30", 15],
  ["dimissioni", "4", "2021-09-30", "2026-09-30", 20], ["licenziamento", "Quadri", "2016-09-30", "2026-09-30", 120],
  ["licenziamento", "Quadri", "2016-10-01", "2026-09-30", 90], ["licenziamento", "7", "2000-01-01", "2026-09-30", 20]]) {
  const g = preavvisoMinimo(tipo, livello, assunzione, cessazione, V.cfg);
  expect(g === giorni, `preavviso ${tipo} ${livello} ${assunzione}-${cessazione}: ${g} contro ${giorni}`);
}
// Quattordicesima pagata a chi resta: da luglio è quella del periodo chiuso il 30 giugno
for (const [ass, mese, n] of [["2015-05-04", "2026-06", 12], ["2015-05-04", "2026-07", 12], ["2015-05-04", "2026-08", 12],
  ["2015-05-04", "2026-05", 11], ["2026-02-01", "2026-07", 5]]) {
  const a = dodicesimi14Pagata(ass, mese, V.cfg);
  expect(a === n, `quattordicesima pagata ${ass} a ${mese}: ${a} contro ${n}`);
}
// I file come escono dagli export: matricole numero o testo, part-time in percentuale, date impossibili
{
  const r = normalizza([{ matricola: 1001, cliente: " A ", part_time: "50%", data_assunzione: "01/09/2020" },
    { matricola: "1002", part_time: "100", data_assunzione: "2020-09-01" }], true);
  expect(r[0].matricola === "1001" && r[0].cliente === "A" && r[0].part_time === 0.5 && r[1].part_time === 1, "normalizza: matricola, part-time");
  for (const d of ["31/02/2026", "2026-13-45", "00/01/2026"]) {
    let rotto = false;
    try { data(d); } catch { rotto = true; }
    expect(rotto, `data impossibile accettata: ${d}`);
  }
  expect(data("1.9.2020") === "2020-09-01", "data con i punti");
}
// Le regole dei quattro CCNL sui casi limite, gli stessi di tests/test_ccnl.py
{
  const K = (k) => ({ ...V.cfg, ...V.cfg.regole[k] });
  const [TZ, M, T, L] = ["terziario", "metalmeccanico", "turismo", "logistica"].map(K);
  for (const [c, n] of [[TZ, 1], [M, 2], [L, 2], [T, 1]])
    expect(scattiMaturati("2022-05-10", "2026-09", c) === n, `scatti ${c.colonna_minimo}: ${scattiMaturati("2022-05-10", "2026-09", c)} contro ${n}`);
  for (const [c, n] of [[TZ, 6], [T, 6], [M, 5], [L, 5]])
    expect(ratei("2026-04-16", "2026-09", c)[0] === n, `ratei 15 giorni ${c.colonna_minimo}`);
  expect(ratei("2015-05-04", "2026-09", M)[1] === 0, "Metalmeccanico senza quattordicesima");
  expect(dodicesimiAllaCessazione("2026-07-20", "2026-09-10", "2026-01-01", TZ) === 1
    && dodicesimiAllaCessazione("2026-07-20", "2026-09-10", "2026-01-01", T) === 2
    && dodicesimiAllaCessazione("2026-07-10", "2026-09-11", "2026-01-01", T) === 2, "Turismo: frazioni sommate");
  for (const [anni, g] of [[9, 24], [10, 25], [17, 25], [18, 30]]) expect(ferieAnnue(M, anni) === g, `ferie Metalmeccanico ${anni} anni`);
  expect(preavvisoMinimo("dimissioni", "Quadri", "2023-01-01", "2026-09-30", L) === 37.5
    && preavvisoMinimo("licenziamento", "Quadri", "2023-01-01", "2026-09-30", L) === 75, "preavviso Logistica");
  for (const [c, ev, dur, q] of [[T, 1, 5, 0], [T, 1, 6, 1], [M, 3, 3, 1], [M, 4, 3, 0.66], [M, 6, 5, 0.5], [M, 6, 6, 1],
    [L, 9, 2, 1], [TZ, 5, 3, 0]]) expect(carenzaPercentuale(ev, false, c, dur) === q, `carenza ${c.regola_carenza} evento ${ev} di ${dur} giorni`);
  expect(indennitaMalattia(2000, "2026-09-01", "2026-09-14", "2026-09", M) === 0, "INPS all'impiegato dell'industria");
  expect(close(quotaNettoGarantita("2026-09", TZ, ["2026-09-07", "2026-09-20"], 1), (30 - 14 + 3 + 11 * 0.75) / 30)
    && quotaNettoGarantita("2026-09", M, ["2026-09-07", "2026-09-20"], 1) === null && quotaNettoGarantita("2026-09", T) === 1
    && quotaNettoGarantita("2026-09", L) === null, "quota del netto garantita");
  expect(integrazioneLorda(3000, 0, "2026-09-03", "2026-09-17", "2026-09", M) === 1200
    && integrazioneLorda(3000, 500, "2026-09-03", "2026-09-17", "2026-09", L) === 700
    && integrazioneLorda(3000, 0, "2026-09-03", "2026-09-17", "2026-09", TZ) === null, "integrazione lorda");
}
// Lo stesso file esportato da un Excel in italiano: punto e virgola, virgola decimale, date gg/mm/aaaa.
const csv = readFileSync(new URL("../../data/cedolini.csv", import.meta.url), "utf8").trim().split("\n");
const head = csv[0].split(",");
const ita = [head.join(";"), ...csv.slice(1).map((l) => l.split(",").map((v, i) => {
  if ((head[i] === "data_assunzione" || head[i] === "data_cessazione") && v) { const [y, m, d] = v.split("-"); return `${d}/${m}/${y}`; }
  return /^-?\d+\.\d+$/.test(v) ? v.replace(".", ",") : v;
}).join(";"))].join("\n");
const righe = normalizza(leggiCsv(ita), true);
const mese = righe.filter((r) => r.mese === V.cfg.mese), prec = righe.filter((r) => r.mese === V.cfg.mese_precedente);
const ris = esegui(mese, prec, V.f24, V.ccnl, V.cfg).anomalie;
expect(ris.length === V.cases[0].anomalie.length, `formato italiano: ${ris.length} segnalazioni contro ${V.cases[0].anomalie.length}`);
V.cases[0].anomalie.forEach((e, i) => expect(ris[i] && ris[i].matricola === e.matricola && ris[i].controllo === e.controllo && close(ris[i].atteso, e.atteso),
  `formato italiano riga ${i}`));
console.log(`${checks - failures} controlli su ${checks} tornano in ${V.cases.length} casi e nel formato di Excel italiano`);
process.exit(failures ? 1 : 0);
