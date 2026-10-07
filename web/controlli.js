// I nove controlli nel browser: gemello riga per riga di src/controlli.py e src/regole.py.
// tests/js/check_controlli.mjs li fa girare sui dati di casi preparati in Python
// (tests/fixtures/js_vectors.json) e la CI fallisce alla prima differenza.

export const CONTROLLI = {
  C01: ["Minimo tabellare", "alta"], C02: ["Scatti di anzianità", "alta"], C03: ["Contributi INPS", "alta"],
  C04: ["Quota TFR", "media"], C05: ["Residuo ferie", "media"], C06: ["Quadratura", "alta"],
  C07: ["Variazione del netto", "media"], C08: ["Riconciliazione F24", "alta"], C09: ["Codice fiscale", "alta"],
  C10: ["Anagrafica", "alta"],
};

const ANAGRAFICA = ["livello", "part_time", "superminimo", "data_assunzione"];
// come _fmt in Python: i numeri nel formato più corto ("%g"), il resto come testo
const fmtValore = (v) => (typeof v === "number" ? String(Number(v.toPrecision(6))) : String(v));

// ---- Arrotondamenti -------------------------------------------------------------------------
// ROUND di Excel: 15 cifre significative, poi metà per eccesso (come regole.centesimi in Python).
export function centesimi(x) {
  const s = Number(x).toPrecision(15);
  const neg = s.startsWith("-");
  const [int, frac = ""] = (neg ? s.slice(1) : s).split("e")[0].split(".");
  if (s.includes("e")) return Math.round(Number(x) * 100) / 100;      // numeri enormi o minuscoli
  const f = (frac + "000").slice(0, 3);
  let cents = BigInt(int + f.slice(0, 2));
  if (Number(f[2]) >= 5) cents += 1n;
  const v = Number(cents) / 100;
  return neg ? -v : v;
}
// round di pandas/numpy: metà al pari, sul valore binario moltiplicato
function rint(v) {
  const r = Math.round(v);
  return Math.abs(v - Math.trunc(v)) === 0.5 ? 2 * Math.round(v / 2) : r;
}
export const round2 = (x) => rint(x * 100) / 100;
export const round4 = (x) => rint(x * 10000) / 10000;

// ---- Codice fiscale (DM 23 dicembre 1976) ------------------------------------------------------
const DISPARI = {};
const ODD = [1, 0, 5, 7, 9, 13, 15, 17, 19, 21, 2, 4, 18, 20, 11, 3, 6, 8, 12, 14, 16, 10, 22, 25, 24, 23];
"0123456789".split("").forEach((c, i) => { DISPARI[c] = ODD[i]; });
"ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("").forEach((c, i) => { DISPARI[c] = ODD[i]; });
const PARI = {};
"0123456789".split("").forEach((c, i) => { PARI[c] = i; });
"ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("").forEach((c, i) => { PARI[c] = i; });

export function cfValido(cf) {
  cf = String(cf).trim().toUpperCase();
  if (cf.length !== 16 || !/^[A-Z0-9]{15}[A-Z]$/.test(cf)) return false;
  let s = 0;
  for (let i = 0; i < 15; i++) s += i % 2 === 0 ? DISPARI[cf[i]] : PARI[cf[i]];
  return String.fromCharCode(65 + (s % 26)) === cf[15];
}

// ---- Regole ---------------------------------------------------------------------------------
export function scattiMaturati(assunzione, mese, cfg) {
  const [y0, m0] = assunzione.split("-").map(Number);
  const [y, m] = mese.split("-").map(Number);
  let n = 0;
  for (let k = 1; k <= cfg.scatti_max; k++) {
    const ty = y0 + cfg.scatti_anni * k;
    if (y > ty || (y === ty && m > m0)) n = k;
  }
  return n;
}

// ---- Controlli --------------------------------------------------------------------------------
// righe: oggetti con i campi di data/cedolini.csv, già convertiti in numeri e date ISO.
export function esegui(mese, prec, f24, ccnl, cfg) {
  const prevBy = new Map(prec.map((r) => [r.matricola, r]));
  const out = [];
  const segnala = (r, codice, atteso, trovato) => out.push({
    matricola: r.matricola, cliente: r.cliente, controllo: codice, voce: CONTROLLI[codice][0],
    atteso, trovato, differenza: typeof atteso === "number" && typeof trovato === "number" ? trovato - atteso : null,
    priorita: CONTROLLI[codice][1] });
  const ferieMese = Math.round((cfg.ferie_annue / 12) * 10000) / 10000;
  for (const r of mese) {
    const t = ccnl[r.livello];
    if (!t) { segnala(r, "C01", "livello CCNL valido", r.livello); continue; }
    const a = {};
    a.tabellare = centesimi(t[cfg.colonna_minimo] * r.part_time);
    a.scatti_n = scattiMaturati(r.data_assunzione, cfg.mese, cfg);
    a.scatti = centesimi(t.scatto * a.scatti_n * r.part_time);
    a.contributi_inps = centesimi(r.lordo * cfg.aliquota);
    const ordinaria = r.tabellare + r.scatti + r.superminimo;
    a.quota_tfr = centesimi(ordinaria * cfg.mensilita / cfg.divisore_tfr / 12);
    const p = prevBy.get(r.matricola);
    a.ferie_residuo = round4((p ? p.ferie_residuo : 0) + ferieMese - r.ferie_godute);
    a.lordo = round2(ordinaria + r.straordinari);
    a.netto = round2(r.lordo - r.contributi_inps - r.irpef - r.altre_trattenute);
    for (const [codice, voce, tol] of [["C01", "tabellare", cfg.tolleranza], ["C02", "scatti", cfg.tolleranza],
      ["C03", "contributi_inps", cfg.tolleranza], ["C04", "quota_tfr", cfg.tolleranza],
      ["C05", "ferie_residuo", cfg.tolleranza_ferie]]) {
      if (Math.abs(r[voce] - a[voce]) > tol) segnala(r, codice, a[voce], r[voce]);
    }
    if (Math.abs(r.lordo - a.lordo) > cfg.tolleranza) segnala(r, "C06", a.lordo, r.lordo);
    else if (Math.abs(r.netto - a.netto) > cfg.tolleranza) segnala(r, "C06", a.netto, r.netto);
    if (p) {
      const v = r.netto / p.netto - 1;
      if (Math.abs(v) > cfg.soglia && !r.evento) segnala(r, "C07", p.netto, r.netto);
    }
    if (!cfValido(r.codice_fiscale)) segnala(r, "C09", "valido", r.codice_fiscale);
    if (p && !r.evento) {
      const cambi = ANAGRAFICA.filter((c) => (typeof p[c] === "number" && typeof r[c] === "number"
        ? Math.abs(p[c] - r[c]) > cfg.tolleranza : String(p[c]) !== String(r[c])));
      if (cambi.length) segnala(r, "C10", cambi.map((c) => `${c} ${fmtValore(p[c])}`).join("; "),
        cambi.map((c) => `${c} ${fmtValore(r[c])}`).join("; "));
    }
  }
  const somme = {};
  for (const r of mese) {
    const s = (somme[r.cliente] ||= { irpef: 0, contributi_inps: 0 });
    s.irpef += r.irpef; s.contributi_inps += r.contributi_inps;
  }
  const riconciliazione = [];
  for (const f of f24) {
    const s = somme[f.cliente] || { irpef: 0, contributi_inps: 0 };
    const irpef = round2(s.irpef), inps = round2(s.contributi_inps);
    const dr = round2(f.ritenute_1001 - irpef), dc = round2(f.contributi_dipendente - inps);
    riconciliazione.push({ cliente: f.cliente, ritenute_1001: f.ritenute_1001, irpef, diff_ritenute: dr,
      contributi_dipendente: f.contributi_dipendente, contributi_inps: inps, diff_contributi: dc });
    if (Math.abs(dr) > cfg.tolleranza || Math.abs(dc) > cfg.tolleranza) {
      const voceR = Math.abs(dr) > cfg.tolleranza;
      const atteso = voceR ? irpef : inps, trovato = voceR ? f.ritenute_1001 : f.contributi_dipendente;
      out.push({ matricola: "", cliente: f.cliente, controllo: "C08", voce: CONTROLLI.C08[0], atteso, trovato,
        differenza: trovato - atteso, priorita: "alta" });
    }
  }
  const cmp = (x, y) => (x < y ? -1 : x > y ? 1 : 0);
  out.sort((x, y) => cmp(x.controllo, y.controllo) || cmp(x.cliente, y.cliente) || cmp(x.matricola, y.matricola));
  return { anomalie: out, riconciliazione };
}

export function novembre(mese, ccnl, cfg) {
  return mese.filter((r) => ccnl[r.livello]).map((r) => {
    const t = ccnl[r.livello];
    const aumento = centesimi((t[cfg.colonna_minimo_prossimo] - t[cfg.colonna_minimo]) * r.part_time);
    const assorbito = r.superminimo_assorbibile ? Math.min(r.superminimo, aumento) : 0;
    return { matricola: r.matricola, cliente: r.cliente, aumento, assorbito, da_pagare: round2(aumento - assorbito) };
  });
}

// ---- Lettura dei CSV -----------------------------------------------------------------------------
// Accetta virgola o punto e virgola come separatore, e la virgola decimale delle esportazioni italiane.
export function leggiCsv(testo) {
  const righe = testo.replace(/^﻿/, "").split(/\r?\n/).filter((l) => l.trim() !== "");
  if (!righe.length) return [];
  const sep = righe[0].split(";").length > righe[0].split(",").length ? ";" : ",";
  const head = righe[0].split(sep).map((h) => h.trim().toLowerCase());
  return righe.slice(1).map((l) => {
    const v = l.split(sep);
    const o = {};
    head.forEach((h, i) => { o[h] = (v[i] ?? "").trim(); });
    return o;
  });
}

const NUMERI = ["part_time", "tabellare", "scatti_n", "scatti", "superminimo", "straordinari", "lordo", "contributi_inps",
  "imponibile_irpef", "irpef", "altre_trattenute", "netto", "quota_tfr", "ferie_maturate", "ferie_godute", "ferie_residuo",
  "ritenute_1001", "contributi_dipendente"];

export function numero(s, decimaleVirgola) {
  if (s === "" || s == null) return 0;
  let t = String(s).replace(/\s|€/g, "");
  if (decimaleVirgola) t = t.replace(/\./g, "").replace(",", ".");
  const n = Number(t);
  if (Number.isNaN(n)) throw new Error(`numero non valido: "${s}"`);
  return n;
}

export function data(s) {
  const t = String(s).trim();
  let m = t.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (m) return `${m[1]}-${m[2]}-${m[3]}`;
  m = t.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
  if (m) return `${m[3]}-${m[2].padStart(2, "0")}-${m[1].padStart(2, "0")}`;
  throw new Error(`data non valida: "${s}"`);
}

export function normalizza(righe, decimaleVirgola) {
  return righe.map((r) => {
    const o = { ...r };
    for (const k of NUMERI) if (k in o) o[k] = numero(o[k], decimaleVirgola);
    if ("data_assunzione" in o) o.data_assunzione = data(o.data_assunzione);
    if ("superminimo_assorbibile" in o) o.superminimo_assorbibile = /^(true|1|s[iì]|vero|x)$/i.test(String(o.superminimo_assorbibile));
    if ("livello" in o) o.livello = String(o.livello).replace(/[°º]/g, "").trim();
    if ("evento" in o) o.evento = String(o.evento || "").trim();
    return o;
  });
}
