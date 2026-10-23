// I quattordici controlli nel browser: gemello riga per riga di src/controlli.py e src/regole.py.
// tests/js/check_controlli.mjs li fa girare sui dati di casi preparati in Python
// (tests/fixtures/js_vectors.json) e la CI fallisce alla prima differenza.

export const CONTROLLI = {
  C01: ["Minimo tabellare", "alta"], C02: ["Scatti di anzianità", "alta"], C03: ["Contributi INPS", "alta"],
  C04: ["Quota TFR", "media"], C05: ["Residuo ferie", "media"], C06: ["Quadratura", "alta"],
  C07: ["Variazione del netto", "media"], C08: ["Riconciliazione F24", "alta"], C09: ["Codice fiscale", "alta"],
  C10: ["Anagrafica", "alta"], C11: ["Ratei 13ª e 14ª", "media"],
  C12: ["Tredicesima e quattordicesima pagate", "alta"], C13: ["Ferie non godute", "alta"], C14: ["Preavviso", "alta"],
};

const ANAGRAFICA = ["livello", "part_time", "superminimo", "data_assunzione"];
// come _fmt in Python: i numeri nel formato più corto ("%g"), il resto come testo
const fmtValore = (v) => (typeof v === "number" ? String(Number(v.toPrecision(6))) : String(v));

// ---- Arrotondamenti -------------------------------------------------------------------------
// ROUND di Excel: 15 cifre significative, poi metà per eccesso (come regole.centesimi in Python).
// Imponibile contributivo all'unità di euro, metà per eccesso (come regole.euro in Python).
export function euro(x) {
  const v = Number(Number(x).toPrecision(15));
  return Math.sign(v) * Math.floor(Math.abs(v) + 0.5);
}

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

// Dodicesimi di tredicesima (da gennaio) e quattordicesima (da luglio) fino al mese del cedolino compreso: il mese
// di assunzione conta se ha almeno cfg.giorni_mese_intero giorni di servizio (come regole.dodicesimi in Python).
export function dodicesimi(assunzione, mese, inizioAnno, inizioMese, cfg) {
  const [ya, ma, da] = assunzione.split("-").map(Number);
  const [y, m] = mese.split("-").map(Number);
  const daInizio = ya < inizioAnno || (ya === inizioAnno && (ma < inizioMese || (ma === inizioMese && da === 1)));
  if (daInizio) return (y - inizioAnno) * 12 + m - inizioMese + 1;
  const giorni = new Date(Date.UTC(ya, ma, 0)).getUTCDate() - da + 1;
  return (y - ya) * 12 + m - ma + (giorni >= cfg.giorni_mese_intero ? 1 : 0);
}

export function ratei(assunzione, mese, cfg) {
  const [y, m] = mese.split("-").map(Number);
  return [dodicesimi(assunzione, mese, y, 1, cfg), dodicesimi(assunzione, mese, m >= 7 ? y : y - 1, 7, cfg)];
}

// Mesi di servizio da `inizio` alla data di cessazione: il primo e l'ultimo mese contano se hanno almeno
// cfg.giorni_mese_intero giorni (come regole.dodicesimi_alla_cessazione in Python). Date ISO.
const giorno = (iso) => { const [y, m, d] = iso.split("-").map(Number); return Date.UTC(y, m - 1, d); };
export function dodicesimiAllaCessazione(assunzione, cessazione, inizio, cfg) {
  const da = assunzione > inizio ? assunzione : inizio;
  if (cessazione < da) return 0;
  const [y0, m0, d0] = da.split("-").map(Number);
  const [y1, m1, d1] = cessazione.split("-").map(Number);
  if (y0 === y1 && m0 === m1) return (giorno(cessazione) - giorno(da)) / 86400000 + 1 >= cfg.giorni_mese_intero ? 1 : 0;
  const primo = new Date(Date.UTC(y0, m0, 0)).getUTCDate() - d0 + 1 >= cfg.giorni_mese_intero;
  const ultimo = d1 >= cfg.giorni_mese_intero;
  return (y1 - y0) * 12 + m1 - m0 - 1 + (primo ? 1 : 0) + (ultimo ? 1 : 0);
}
// I dodicesimi di una quattordicesima pagata a chi resta: da luglio in poi, quelli del periodo chiuso il 30 giugno
// (come regole.dodicesimi_14_pagata in Python).
export function dodicesimi14Pagata(assunzione, mese, cfg) {
  const [y, m] = mese.split("-").map(Number);
  if (m < 7) return ratei(assunzione, mese, cfg)[1];
  return dodicesimiAllaCessazione(assunzione, `${y}-06-30`, `${y - 1}-07-01`, cfg);
}
export const inizio13 = (iso) => `${iso.slice(0, 4)}-01-01`;
export const inizio14 = (iso) => { const y = Number(iso.slice(0, 4)); return `${Number(iso.slice(5, 7)) >= 7 ? y : y - 1}-07-01`; };

export function anniDiServizio(assunzione, al) {
  const [ya, ma, da] = assunzione.split("-").map(Number);
  const [y, m, d] = al.split("-").map(Number);
  return y - ya - (m < ma || (m === ma && d < da) ? 1 : 0);
}

// Giorni di preavviso del CCNL: fino a 5 anni di servizio, dal 6° al 10°, oltre il 10° (F13).
export function preavvisoMinimo(tipo, livello, assunzione, cessazione, cfg) {
  const anni = anniDiServizio(assunzione, cessazione);
  return cfg.preavviso[tipo][livello][anni < 5 ? 0 : anni < 10 ? 1 : 2];
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
  // C12-C14: le voci pagate a dicembre o alla cessazione, quando il cedolino le riporta (come _cessazione in Python)
  function cessazione(r) {
    const mensile = centesimi(r.tabellare + r.scatti + r.superminimo);
    const ces = vuoto(r.data_cessazione) ? null : String(r.data_cessazione);
    for (const [voce, inizio, k] of [["tredicesima", inizio13, 0], ["quattordicesima", inizio14, 1]]) {
      if (vuoto(r[voce])) continue;
      const n = ces ? dodicesimiAllaCessazione(r.data_assunzione, ces, inizio(ces), cfg)
        : k === 0 ? ratei(r.data_assunzione, cfg.mese, cfg)[0] : dodicesimi14Pagata(r.data_assunzione, cfg.mese, cfg);
      const atteso = centesimi(mensile * n / 12), trovato = Number(r[voce]);
      if (Math.abs(trovato - atteso) > cfg.tolleranza) { segnala(r, "C12", atteso, trovato); break; }
    }
    if (!ces) return;
    if (!vuoto(r.ferie_liquidate)) {
      const atteso = centesimi(mensile / cfg.divisore_giornaliero * r.ferie_residuo), trovato = Number(r.ferie_liquidate);
      if (Math.abs(trovato - atteso) > cfg.tolleranza) segnala(r, "C13", atteso, trovato);
    }
    const tipo = String(r.tipo_cessazione ?? "").trim().toLowerCase();
    if (Object.hasOwn(cfg.preavviso, tipo) && !vuoto(r.preavviso_giorni)) {
      const minimo = preavvisoMinimo(tipo, String(r.livello), r.data_assunzione, ces, cfg);
      if (Math.trunc(Number(r.preavviso_giorni)) < minimo) segnala(r, "C14", minimo, Number(r.preavviso_giorni));
    }
  }
  for (const r of mese) {
    const t = ccnl[r.livello];
    if (!t) { segnala(r, "C01", "livello CCNL valido", r.livello); continue; }
    const a = {};
    a.tabellare = centesimi(t[cfg.colonna_minimo] * r.part_time);
    a.scatti_n = scattiMaturati(r.data_assunzione, cfg.mese, cfg);
    a.scatti = centesimi(t.scatto * a.scatti_n * r.part_time);
    a.contributi_inps = centesimi(euro(r.lordo) * cfg.aliquota);
    const ordinaria = r.tabellare + r.scatti + r.superminimo;
    a.quota_tfr = centesimi(ordinaria * cfg.mensilita / cfg.divisore_tfr / 12);
    const p = prevBy.get(r.matricola);
    a.ferie_residuo = round4((p ? p.ferie_residuo : 0) + ferieMese - r.ferie_godute);
    const extra = ["tredicesima", "quattordicesima", "ferie_liquidate"].reduce((s, k) => s + (vuoto(r[k]) ? 0 : Number(r[k])), 0);
    a.lordo = centesimi(ordinaria + r.straordinari + extra);
    a.netto = centesimi(r.lordo - r.contributi_inps - r.irpef - r.altre_trattenute);
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
    if (r.ratei_13 != null && r.ratei_14 != null) {        // colonne facoltative: senza, C11 non si applica
      // per chi lascia nel mese, i dodicesimi si contano fino alla data di uscita
      const [e13, e14] = vuoto(r.data_cessazione) ? ratei(r.data_assunzione, cfg.mese, cfg)
        : [dodicesimiAllaCessazione(r.data_assunzione, r.data_cessazione, inizio13(r.data_cessazione), cfg),
          dodicesimiAllaCessazione(r.data_assunzione, r.data_cessazione, inizio14(r.data_cessazione), cfg)];
      if (r.ratei_13 !== e13 || r.ratei_14 !== e14) segnala(r, "C11", `13ª ${e13}; 14ª ${e14}`, `13ª ${r.ratei_13}; 14ª ${r.ratei_14}`);
    }
    cessazione(r);
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
    const irpef = centesimi(s.irpef), inps = centesimi(s.contributi_inps);
    const dr = centesimi(f.ritenute_1001 - irpef), dc = centesimi(f.contributi_dipendente - inps);
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
  // chi lascia prima della tranche non la riceve
  return mese.filter((r) => ccnl[r.livello] && (vuoto(r.data_cessazione) || r.data_cessazione >= cfg.prossima_tranche)).map((r) => {
    const t = ccnl[r.livello];
    const aumento = centesimi((t[cfg.colonna_minimo_prossimo] - t[cfg.colonna_minimo]) * r.part_time);
    const assorbito = r.superminimo_assorbibile ? Math.min(r.superminimo, aumento) : 0;
    return { matricola: r.matricola, cliente: r.cliente, aumento, assorbito, da_pagare: centesimi(aumento - assorbito) };
  });
}

const vuoto = (v) => v == null || (typeof v === "number" && Number.isNaN(v)) || String(v).trim() === "";

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

const FACOLTATIVI = ["ratei_13", "ratei_14", "preavviso_giorni", "tredicesima", "quattordicesima", "ferie_liquidate"];

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
  let iso = null;
  let m = t.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (m) iso = `${m[1]}-${m[2]}-${m[3]}`;
  m = t.match(/^(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})$/);
  if (m) iso = `${m[3]}-${m[2].padStart(2, "0")}-${m[1].padStart(2, "0")}`;
  // una data che esiste davvero: niente 31 febbraio o mese 13
  const [y, mo, d] = (iso || "").split("-").map(Number);
  const dt = iso && new Date(Date.UTC(y, mo - 1, d));
  if (!dt || dt.getUTCFullYear() !== y || dt.getUTCMonth() !== mo - 1 || dt.getUTCDate() !== d) throw new Error(`data non valida: "${s}"`);
  return iso;
}

export function normalizza(righe, decimaleVirgola) {
  return righe.map((r) => {
    const o = { ...r };
    // la quota di part-time si scrive spesso in percentuale: "100", "50%"
    if ("part_time" in o) {
      const s = String(o.part_time ?? "").trim();
      o.part_time = s.endsWith("%") ? numero(s.slice(0, -1), decimaleVirgola) / 100 : numero(s, decimaleVirgola);
      if (o.part_time > 1.5) o.part_time /= 100;
    }
    for (const k of NUMERI) if (k in o && k !== "part_time") o[k] = numero(o[k], decimaleVirgola);
    for (const k of ["matricola", "cliente"]) if (k in o) o[k] = String(o[k] ?? "").trim();   // 1001 e "1001" sono lo stesso
    for (const k of FACOLTATIVI) {                        // facoltative: vuote vuol dire "non indicate", non zero
      o[k] = k in o && String(o[k]).trim() !== "" ? numero(o[k], decimaleVirgola) : null;
    }
    if ("data_assunzione" in o) o.data_assunzione = data(o.data_assunzione);
    o.data_cessazione = vuoto(o.data_cessazione) ? null : data(o.data_cessazione);
    o.tipo_cessazione = String(o.tipo_cessazione ?? "").trim().toLowerCase();
    if ("superminimo_assorbibile" in o) o.superminimo_assorbibile = /^(true|1|s[iì]|vero|x)$/i.test(String(o.superminimo_assorbibile));
    if ("livello" in o) o.livello = String(o.livello).replace(/[°º]/g, "").trim();
    if ("evento" in o) o.evento = String(o.evento || "").trim();
    return o;
  });
}
