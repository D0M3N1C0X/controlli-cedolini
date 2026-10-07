// Rifà con web/controlli.js ogni caso calcolato in Python. Esce con 1 alla prima differenza.
import { readFileSync } from "node:fs";
import { esegui, novembre, leggiCsv, normalizza } from "../../web/controlli.js";

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
// Lo stesso file esportato da un Excel in italiano: punto e virgola, virgola decimale, date gg/mm/aaaa.
const csv = readFileSync(new URL("../../data/cedolini.csv", import.meta.url), "utf8").trim().split("\n");
const head = csv[0].split(",");
const ita = [head.join(";"), ...csv.slice(1).map((l) => l.split(",").map((v, i) => {
  if (head[i] === "data_assunzione") { const [y, m, d] = v.split("-"); return `${d}/${m}/${y}`; }
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
