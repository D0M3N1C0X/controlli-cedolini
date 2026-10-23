// The browser tool's page: files in, columns matched, checks run, results shown and downloaded.
// The checks themselves are in controlli.js, verified against Python on every change; this file only moves data
// between the user and them. Nothing here talks to a server: inputs.json and testi.json come from this same page.
import { esegui, novembre, normalizza } from "./controlli.js";
import { createI18n } from "./design/i18n.js";
import { readTable, parseCsv, matchColumns, applyMapping, savedMapping, rememberMapping, download } from "./design/table.js";
import { writeXlsx } from "./design/xlsx.js";

const [{ cfg: CFG, ccnl: CCNL }, TESTI] = await Promise.all(
  ["./inputs.json", "./testi.json"].map((u) => fetch(u).then((r) => r.json())));

const UI = {
  it: {
    brand: "Controlli cedolini", eyebrow: "CCNL Terziario · prima dell'invio al cliente",
    title: "Controlla i cedolini del mese",
    lead: "Carica l'export del tuo software paghe: quattordici controlli ricalcolano ogni voce dalle regole del contratto e ti dicono cosa correggere, prima che il cliente se ne accorga.",
    privacy: "I tuoi file restano su questo computer: i controlli girano in questa pagina e niente viene inviato. Puoi verificarlo staccando la rete dopo che la pagina si è aperta.",
    step1: "I tuoi file", step1sub: "File Excel (.xlsx) o CSV, così come escono dal software paghe.",
    dropMese: "Cedolini del mese", dropMeseSub: "Obbligatorio · trascinalo qui o tocca per sceglierlo",
    dropPrima: "Cedolini del mese prima", dropPrimaSub: "Facoltativo · serve per ferie, variazioni del netto e anagrafica",
    dropF24: "Deleghe F24", dropF24Sub: "Facoltativo · per confrontare ritenute e contributi",
    esempio: "Prova con i dati di esempio", modelli: "Modelli delle colonne:", modelloCed: "cedolini",
    step2: "Le colonne", modifica: "Modifica",
    colonneOk: "Tutte le colonne necessarie sono state riconosciute",
    colonneSub: "Abbina ogni voce alla colonna del tuo file. La scelta resta su questo computer per la prossima volta.",
    colonneMancano: "Mancano {n} colonne: sceglile qui sotto per continuare.",
    nonPresente: "— non presente —", facoltativa: "facoltativa",
    step3: "Le impostazioni", mese: "Mese da controllare", meseSub: "Preso dal file, se c'è la colonna del mese.",
    aliquota: "Contributo INPS a carico del dipendente", aliquotaSub: "0,0919 è l'aliquota generale: usa quella della posizione del cliente.",
    soglia: "Variazione del netto da spiegare", sogliaSub: "0,20 vuol dire 20% in più o in meno del mese prima.",
    esegui: "Controlla i cedolini", step4: "Cosa correggere",
    filtroCliente: "Filtra per cliente", filtroControllo: "Filtra per controllo",
    tuttiClienti: "Tutti i clienti", tuttiControlli: "Tutti i controlli",
    scaricaXlsx: "Scarica in Excel", stampa: "Stampa per il cliente", stampaTitolo: "Controllo dei cedolini",
    stampaMeta: "Mese {mese} · controllato il {oggi} · {n} segnalazioni",
    kCedolini: "Cedolini controllati", kSegnalazioni: "Segnalazioni", kAlta: "Da correggere prima dell'invio",
    kGuardare: "Cedolini da guardare",
    hMatricola: "Matricola", hCliente: "Cliente", hControllo: "Controllo", hPriorita: "Priorità", hAtteso: "Atteso",
    hTrovato: "Trovato", hDifferenza: "Differenza", hCosa: "Cosa fare", hAssegnato: "Assegnato a",
    hCorretto: "Corretto il", hNote: "Note", hTotale: "Totale", hDipendenti: "Dipendenti", hAumento: "Aumento",
    hAssorbito: "Assorbito", hDaPagare: "Da pagare", hDescrizione: "Descrizione",
    nessuna: "Nessuna segnalazione: i cedolini tornano con le regole del contratto.",
    perCliente: "Per cliente", novembre: "La tranche del 1° novembre 2026, al mese",
    novembreSub: "Lordo dipendente. L'assorbimento del superminimo va verificato sulla lettera di assunzione.",
    clienteN: "Cliente {c}", giorni: "{n} gg", valido: "valido",
    footer: "Gli stessi calcoli dello script Python e del foglio di calcolo del progetto, verificati tra loro a ogni modifica. Non è consulenza del lavoro.",
    rapporto: "Rapporto", catalogo: "Catalogo dei controlli", codice: "Codice",
    eFile: "Non riesco a leggere {f}: {e}.", eVuoto: "Il file dei cedolini del mese è vuoto.",
    eSenzaMese: "Nessun cedolino del mese prima: il residuo ferie parte da zero e la variazione del netto non si controlla.",
    eNumero: "C'è un valore non numerico in una colonna di importi: {e}.",
    fileFoglio: "{n} righe · foglio «{s}»", fileRighe: "{n} righe",
    xSegnalazioni: "Segnalazioni", xPerCliente: "Per cliente", xNovembre: "Novembre 2026", xParametri: "Parametri",
    xMese: "Mese controllato", xAliquota: "Contributo INPS dipendente", xSoglia: "Soglia di variazione del netto",
    xData: "Controllato il", xFonte: "Generato da controlli-cedolini",
    f_mese: "Mese", f_matricola: "Matricola", f_cliente: "Cliente", f_codice_fiscale: "Codice fiscale", f_livello: "Livello",
    f_data_assunzione: "Data di assunzione", f_part_time: "Percentuale di part-time", f_evento: "Evento del mese",
    f_superminimo_assorbibile: "Superminimo assorbibile", f_tabellare: "Tabellare", f_scatti_n: "Numero di scatti",
    f_scatti: "Importo scatti", f_superminimo: "Superminimo", f_straordinari: "Straordinari", f_lordo: "Lordo",
    f_contributi_inps: "Contributi INPS dipendente", f_imponibile_irpef: "Imponibile IRPEF", f_irpef: "IRPEF",
    f_altre_trattenute: "Altre trattenute", f_netto: "Netto", f_quota_tfr: "Quota TFR del mese",
    f_ferie_maturate: "Ferie maturate", f_ferie_godute: "Ferie godute", f_ferie_residuo: "Residuo ferie",
    f_ratei_13: "Ratei di tredicesima", f_ratei_14: "Ratei di quattordicesima",
    f_data_cessazione: "Data di cessazione", f_tipo_cessazione: "Tipo di cessazione (dimissioni o licenziamento)",
    f_preavviso_giorni: "Giorni di preavviso", f_tredicesima: "Tredicesima pagata", f_quattordicesima: "Quattordicesima pagata",
    f_ferie_liquidate: "Ferie non godute pagate",
    f_ritenute_1001: "Ritenute IRPEF (codice 1001)", f_contributi_dipendente: "Contributi dei dipendenti",
  },
  en: {
    brand: "Payslip checks", eyebrow: "Italian CCNL Terziario · before payslips go to the client",
    title: "Check this month's payslips",
    lead: "Load the export from your payroll software: fourteen checks recompute every item from the collective agreement's rules and tell you what to fix, before the client notices.",
    privacy: "Your files stay on this computer: the checks run in this page and nothing is sent. You can confirm it by going offline once the page has opened.",
    step1: "Your files", step1sub: "Excel (.xlsx) or CSV files, as they come out of the payroll software.",
    dropMese: "This month's payslips", dropMeseSub: "Required · drop it here or tap to choose it",
    dropPrima: "Last month's payslips", dropPrimaSub: "Optional · used for holidays, changes in net pay and personnel records",
    dropF24: "F24 payments", dropF24Sub: "Optional · to reconcile taxes and contributions",
    esempio: "Try the example data", modelli: "Column templates:", modelloCed: "payslips",
    step2: "The columns", modifica: "Change",
    colonneOk: "Every column needed was recognised",
    colonneSub: "Match each item to a column of your file. Your choice stays on this computer for next time.",
    colonneMancano: "{n} columns are missing: choose them below to continue.",
    nonPresente: "— not in the file —", facoltativa: "optional",
    step3: "Settings", mese: "Month to check", meseSub: "Taken from the file when it has a month column.",
    aliquota: "Employee INPS contribution", aliquotaSub: "0.0919 is the general rate: use the one of the client's INPS position.",
    soglia: "Change in net pay to explain", sogliaSub: "0.20 means 20% above or below last month.",
    esegui: "Check the payslips", step4: "What to fix",
    filtroCliente: "Filter by client", filtroControllo: "Filter by check",
    tuttiClienti: "All clients", tuttiControlli: "All checks",
    scaricaXlsx: "Download in Excel", stampa: "Print for the client", stampaTitolo: "Payslip check",
    stampaMeta: "Month {mese} · checked on {oggi} · {n} flags",
    kCedolini: "Payslips checked", kSegnalazioni: "Flags", kAlta: "To fix before sending", kGuardare: "Payslips to look at",
    hMatricola: "Employee", hCliente: "Client", hControllo: "Check", hPriorita: "Priority", hAtteso: "Expected",
    hTrovato: "Found", hDifferenza: "Difference", hCosa: "What to do", hAssegnato: "Assigned to",
    hCorretto: "Fixed on", hNote: "Notes", hTotale: "Total", hDipendenti: "Employees", hAumento: "Increase",
    hAssorbito: "Absorbed", hDaPagare: "To pay", hDescrizione: "Description",
    nessuna: "No flags: the payslips agree with the collective agreement's rules.",
    perCliente: "By client", novembre: "The 1 November 2026 increase, per month",
    novembreSub: "Employee gross pay. Whether the individual supplement absorbs it depends on the hiring letter.",
    clienteN: "Client {c}", giorni: "{n} days", valido: "valid",
    footer: "The same calculations as the project's Python script and spreadsheet, checked against each other on every change. Not legal advice.",
    rapporto: "Report", catalogo: "Catalogue of checks", codice: "Code",
    eFile: "I cannot read {f}: {e}.", eVuoto: "This month's payslip file is empty.",
    eSenzaMese: "No payslips for last month: the holiday balance starts from zero and changes in net pay are not checked.",
    eNumero: "A column of amounts has a value that is not a number: {e}.",
    fileFoglio: "{n} rows · sheet “{s}”", fileRighe: "{n} rows",
    xSegnalazioni: "Flags", xPerCliente: "By client", xNovembre: "November 2026", xParametri: "Settings",
    xMese: "Month checked", xAliquota: "Employee INPS contribution", xSoglia: "Net pay change threshold",
    xData: "Checked on", xFonte: "Made with controlli-cedolini",
    f_mese: "Month", f_matricola: "Employee number", f_cliente: "Client", f_codice_fiscale: "Tax code", f_livello: "Grade",
    f_data_assunzione: "Hiring date", f_part_time: "Part-time share", f_evento: "Event this month",
    f_superminimo_assorbibile: "Supplement absorbable", f_tabellare: "Basic pay", f_scatti_n: "Number of increments",
    f_scatti: "Increments amount", f_superminimo: "Individual supplement", f_straordinari: "Overtime", f_lordo: "Gross pay",
    f_contributi_inps: "Employee INPS contribution", f_imponibile_irpef: "Taxable income", f_irpef: "Income tax (IRPEF)",
    f_altre_trattenute: "Other deductions", f_netto: "Net pay", f_quota_tfr: "Monthly TFR accrual",
    f_ferie_maturate: "Holidays accrued", f_ferie_godute: "Holidays taken", f_ferie_residuo: "Holiday balance",
    f_ratei_13: "13th month twelfths", f_ratei_14: "14th month twelfths",
    f_data_cessazione: "Leaving date", f_tipo_cessazione: "Type of leaving (dimissioni or licenziamento)",
    f_preavviso_giorni: "Notice days", f_tredicesima: "13th month paid", f_quattordicesima: "14th month paid",
    f_ferie_liquidate: "Untaken holiday paid",
    f_ritenute_1001: "Income tax withheld (code 1001)", f_contributi_dipendente: "Employee contributions",
  },
};

// The columns the checks read, with the names payroll exports often use for them.
const CAMPI_CEDOLINI = [
  ["mese", false, ["periodo", "mese di riferimento", "competenza", "month"]],
  ["matricola", true, ["codice dipendente", "cod dipendente", "id dipendente", "matr", "employee id"]],
  ["cliente", true, ["azienda", "ditta", "codice azienda", "client", "company"]],
  ["codice_fiscale", true, ["cf", "cod fiscale", "codice fiscale dipendente", "tax code"]],
  ["livello", true, ["inquadramento", "livello inquadramento", "liv", "grade"]],
  ["data_assunzione", true, ["data di assunzione", "assunzione", "data assunz", "hiring date"]],
  ["part_time", true, ["percentuale part time", "perc part time", "pt", "part time"]],
  ["evento", false, ["eventi", "evento del mese", "event"]],
  ["superminimo_assorbibile", false, ["superminimo assorbibile", "assorbibile"]],
  ["tabellare", true, ["minimo tabellare", "retribuzione tabellare", "paga tabellare"]],
  ["scatti_n", false, ["numero scatti", "n scatti"]],
  ["scatti", true, ["scatti anzianita", "importo scatti"]],
  ["superminimo", true, ["superminimo individuale"]],
  ["straordinari", true, ["straordinario", "lavoro straordinario"]],
  ["lordo", true, ["totale competenze", "retribuzione lorda", "totale lordo", "gross"]],
  ["contributi_inps", true, ["contributi", "inps dipendente", "contributi c dipendente", "contributi a carico dipendente"]],
  ["imponibile_irpef", false, ["imponibile fiscale"]],
  ["irpef", true, ["ritenute irpef", "irpef netta"]],
  ["altre_trattenute", true, ["trattenute", "altre ritenute"]],
  ["netto", true, ["netto in busta", "netto a pagare", "net"]],
  ["quota_tfr", true, ["tfr", "rateo tfr", "quota tfr mese"]],
  ["ferie_maturate", false, ["ferie maturate nel mese"]],
  ["ferie_godute", true, ["ferie fruite", "ferie godute nel mese"]],
  ["ferie_residuo", true, ["residuo ferie", "ferie residue"]],
  ["ratei_13", false, ["ratei tredicesima", "ratei 13a", "dodicesimi tredicesima"]],
  ["ratei_14", false, ["ratei quattordicesima", "ratei 14a", "dodicesimi quattordicesima"]],
  ["data_cessazione", false, ["data di cessazione", "cessazione", "data licenziamento", "data dimissioni", "leaving date"]],
  ["tipo_cessazione", false, ["tipo di cessazione", "motivo cessazione", "causale cessazione"]],
  ["preavviso_giorni", false, ["preavviso", "giorni di preavviso", "giorni preavviso", "notice days"]],
  ["tredicesima", false, ["tredicesima mensilita", "13a mensilita", "mensilita 13"]],
  ["quattordicesima", false, ["quattordicesima mensilita", "14a mensilita", "mensilita 14"]],
  ["ferie_liquidate", false, ["indennita ferie non godute", "ferie liquidate", "ferie non godute liquidate"]],
].map(([key, required, aliases]) => ({ key, required, aliases }));
const CAMPI_F24 = [
  ["cliente", true, ["azienda", "ditta", "client"]],
  ["mese", false, ["periodo", "mese di riferimento"]],
  ["ritenute_1001", true, ["codice tributo 1001", "ritenute 1001", "irpef 1001"]],
  ["contributi_dipendente", true, ["contributi dipendenti", "inps dipendente", "contributi a carico dipendenti"]],
].map(([key, required, aliases]) => ({ key, required, aliases }));

const i18n = createI18n(UI, "it");
const t = i18n.t;
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const testo = (codice) => TESTI[i18n.lang][codice];

// state: one entry per file the user gave, plus the result of the last run
const files = { mese: null, prima: null, f24: null };
let risultato = null;

$("aliquota").value = CFG.aliquota;
$("soglia").value = CFG.soglia;
$("mese").value = CFG.mese;

function messaggio(text, kind = "error") {
  const m = $("errore");
  m.textContent = text || "";
  m.className = `s-msg is-${kind}${text ? " is-shown" : ""}`;
}

// ---- files -------------------------------------------------------------------------------------------
async function prendiFile(slot, file) {
  try {
    const table = await readTable(file);
    files[slot] = { name: file.name, ...table };
    risultato = null;                                   // a new file: old results no longer apply
    $("risultati").style.display = "none";
    $(`nome-${slot}`).textContent = `${file.name} · ` + (table.sheet
      ? t("fileFoglio", { n: table.rows.length, s: table.sheet }) : t("fileRighe", { n: table.rows.length }));
    $(`drop-${slot}`).classList.add("is-done");
    messaggio("");
    colonne();
  } catch (e) {
    messaggio(t("eFile", { f: file.name, e: e.message }));
  }
}

for (const slot of Object.keys(files)) {
  const drop = $(`drop-${slot}`), input = $(`file-${slot}`);
  input.addEventListener("change", () => input.files[0] && prendiFile(slot, input.files[0]));
  drop.addEventListener("dragover", (e) => { e.preventDefault(); drop.classList.add("is-over"); });
  drop.addEventListener("dragleave", () => drop.classList.remove("is-over"));
  drop.addEventListener("drop", (e) => {
    e.preventDefault(); drop.classList.remove("is-over");
    if (e.dataTransfer.files[0]) prendiFile(slot, e.dataTransfer.files[0]);
  });
}

$("esempio").addEventListener("click", async () => {
  let c, f;
  try {
    [c, f] = await Promise.all(["cedolini.csv", "f24.csv"].map(async (u) => {
      const r = await fetch(u);
      if (!r.ok) throw new Error(`${u}: ${r.status}`);
      return r.text();
    }));
  } catch (e) { messaggio(t("eFile", { f: "dati di esempio", e: e.message })); return; }
  const ced = parseCsv(c);
  files.mese = { name: "cedolini.csv", ...ced };
  files.prima = null;
  files.f24 = { name: "f24.csv", ...parseCsv(f) };
  $("nome-mese").textContent = `cedolini.csv · ${t("fileRighe", { n: ced.rows.length })}`;
  $("nome-f24").textContent = "f24.csv";
  ["mese", "f24"].forEach((s) => $(`drop-${s}`).classList.add("is-done"));
  colonne();
  controlla();
});

// ---- columns -----------------------------------------------------------------------------------------
const mapping = { mese: {}, prima: {}, f24: {} };
const campi = (slot) => (slot === "f24" ? CAMPI_F24 : CAMPI_CEDOLINI);
const chiave = (slot) => (slot === "f24" ? "f24" : "cedolini");

function colonne() {
  const slots = Object.keys(files).filter((s) => files[s]);
  const mancanti = [];
  for (const s of slots) {
    const m = matchColumns(files[s].headers, campi(s), savedMapping(chiave(s), files[s].headers));
    mapping[s] = m.mapping;
    mancanti.push(...m.missing.map((k) => [s, k]));
  }
  // the month: from the file when it has a month column
  const mesi = files.mese && mapping.mese.mese
    ? [...new Set(files.mese.rows.map((r) => normalizzaMese(r[mapping.mese.mese])).filter(Boolean))].sort() : [];
  if (mesi.length) $("mese").value = mesi[mesi.length - 1];
  $("passo-colonne").style.display = files.mese ? "block" : "none";
  disegnaMappa(mancanti.length > 0);
  $("esegui").disabled = !files.mese || mancanti.length > 0;
}

function normalizzaMese(v) {
  const s = String(v ?? "").trim();
  let m = s.match(/^(\d{4})-(\d{1,2})/);
  if (m) return `${m[1]}-${m[2].padStart(2, "0")}`;
  m = s.match(/^(\d{1,2})[/.-](\d{4})$/);
  return m ? `${m[2]}-${m[1].padStart(2, "0")}` : "";
}

function disegnaMappa(apri) {
  const slots = Object.keys(files).filter((s) => files[s]);
  const richiesti = slots.reduce((n, s) => n + campi(s).filter((f) => f.required).length, 0);
  const mancano = slots.reduce((n, s) => n + campi(s).filter((f) => f.required && !mapping[s][f.key]).length, 0);
  $("colonne-ok").textContent = t("colonneOk", { n: richiesti });
  $("colonne-sub").textContent = mancano ? t("colonneMancano", { n: mancano }) : t("colonneSub");
  $("riepilogo-colonne").style.display = mancano || apri === "forza" ? "none" : "block";
  const mappa = $("mappa");
  mappa.style.display = mancano || apri === "forza" ? "grid" : "none";
  mappa.innerHTML = slots.map((s) => `<p class="s-why"><b>${esc(files[s].name)}</b></p>` + campi(s).map((f) => {
    const scelta = mapping[s][f.key] || "";
    const missing = f.required && !scelta;
    return `<div class="s-map-row${missing ? " is-missing" : ""}"><div class="need">${esc(t(`f_${f.key}`))}
      ${f.required ? "" : `<small>${esc(t("facoltativa"))}</small>`}</div>
      <select class="s-select" data-slot="${s}" data-key="${f.key}" aria-label="${esc(t(`f_${f.key}`))}">
        <option value="">${esc(t("nonPresente"))}</option>
        ${files[s].headers.map((h) => `<option ${h === scelta ? "selected" : ""}>${esc(h)}</option>`).join("")}
      </select></div>`;
  }).join("")).join("");
  mappa.querySelectorAll("select").forEach((sel) => sel.addEventListener("change", () => {
    const s = sel.dataset.slot;
    mapping[s] = { ...mapping[s], [sel.dataset.key]: sel.value };
    rememberMapping(chiave(s), files[s].headers, mapping[s]);
    const restano = campi(s).some((f) => f.required && !mapping[s][f.key]);
    $("esegui").disabled = !files.mese || Object.keys(files).some((x) => files[x] && campi(x).some((f) => f.required && !mapping[x][f.key]));
    sel.closest(".s-map-row").classList.toggle("is-missing", !sel.value && campi(s).find((f) => f.key === sel.dataset.key).required);
    if (!restano) $("colonne-sub").textContent = t("colonneSub");
  }));
}
$("mostra-colonne").addEventListener("click", () => disegnaMappa("forza"));

// ---- checks -----------------------------------------------------------------------------------------
function precedente(m) {
  const [y, mo] = m.split("-").map(Number);
  return mo === 1 ? `${y - 1}-12` : `${y}-${String(mo - 1).padStart(2, "0")}`;
}

function righe(slot, meseFisso) {
  const f = files[slot];
  const rows = applyMapping(f.rows, mapping[slot]).map((r) => {
    if (slot !== "f24") r.mese = normalizzaMese(r.mese) || meseFisso;
    for (const k of ["evento", "superminimo_assorbibile"]) if (!(k in r) && slot !== "f24") r[k] = "";
    return r;
  });
  return normalizza(rows, f.decimalComma);
}

function controlla() {
  try {
    messaggio("");
    const mese = $("mese").value;
    const cfg = { ...CFG, mese, aliquota: +$("aliquota").value, soglia: +$("soglia").value };
    const tutti = [...righe("mese", mese), ...(files.prima ? righe("prima", precedente(mese)) : [])];
    if (!tutti.length) throw new Error(t("eVuoto"));
    const corr = tutti.filter((r) => r.mese === mese);
    const prec = tutti.filter((r) => r.mese === precedente(mese));
    const f24 = files.f24 ? righe("f24").filter((r) => !r.mese || normalizzaMese(r.mese) === mese) : [];
    const { anomalie, riconciliazione } = esegui(corr, prec, f24, CCNL, cfg);
    risultato = { anomalie, riconciliazione, nov: novembre(corr, CCNL, cfg), corr, prec, cfg };
    mostra();
    if (!prec.length) messaggio(t("eSenzaMese"), "info");
    $("risultati").scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
  } catch (e) {
    messaggio(/numero non valido/.test(e.message) ? t("eNumero", { e: e.message.split(": ").pop() }) : e.message);
  }
}
$("esegui").addEventListener("click", controlla);

// ---- results ----------------------------------------------------------------------------------------
const formato = (a, v) => {
  if (v == null || v === "") return "–";
  if (typeof v !== "number") return v === "valido" ? t("valido") : esc(v);
  const giorni = (d) => t("giorni", { n: i18n.number(v, d).replace(/^-/, "−") });
  if (a.controllo === "C05") return giorni(2);
  return a.controllo === "C14" ? giorni(0) : i18n.money(v);
};
const priorita = (p) => (i18n.lang === "en" ? { alta: "high", media: "medium" }[p] : p);
const pill = (p) => `<span class="s-pill ${p === "alta" ? "is-high" : "is-medium"}">${esc(priorita(p))}</span>`;

function mostra() {
  if (!risultato) return;
  const { anomalie, corr, nov } = risultato;
  $("risultati").style.display = "block";
  const daGuardare = new Set(anomalie.filter((a) => a.matricola).map((a) => a.matricola)).size;
  const alta = anomalie.filter((a) => a.priorita === "alta").length;
  $("kpis").innerHTML = [[t("kCedolini"), i18n.number(corr.length), ""], [t("kSegnalazioni"), anomalie.length, anomalie.length ? "" : "is-good"],
    [t("kAlta"), alta, alta ? "is-bad" : "is-good"], [t("kGuardare"), daGuardare, ""]]
    .map(([k, v, c]) => `<div class="s-kpi ${c}"><div class="k">${esc(k)}</div><div class="v">${v}</div></div>`).join("");
  $("stampa-meta").textContent = t("stampaMeta", { mese: risultato.cfg.mese, oggi: new Date().toLocaleDateString(i18n.lang === "it" ? "it-IT" : "en-GB"), n: anomalie.length });
  const clienti = [...new Set(corr.map((r) => r.cliente))].sort();
  const fc = $("f-cliente").value, fk = $("f-controllo").value;
  $("f-cliente").innerHTML = `<option value="">${esc(t("tuttiClienti"))}</option>` + clienti.map((c) => `<option value="${esc(c)}" ${c === fc ? "selected" : ""}>${esc(t("clienteN", { c }))}</option>`).join("");
  $("f-controllo").innerHTML = `<option value="">${esc(t("tuttiControlli"))}</option>` +
    Object.keys(TESTI.it).map((k) => `<option value="${k}" ${k === fk ? "selected" : ""}>${k} · ${esc(testo(k).nome)}</option>`).join("");
  tabella();
  const codici = Object.keys(TESTI.it);
  $("riepilogo").innerHTML = `<tr><th class="l">${esc(t("hControllo"))}</th>${clienti.map((c) => `<th>${esc(t("clienteN", { c }))}</th>`).join("")}<th>${esc(t("hTotale"))}</th></tr>` +
    codici.map((k) => {
      const n = clienti.map((c) => anomalie.filter((a) => a.controllo === k && a.cliente === c).length);
      return `<tr><td class="l">${k} · ${esc(testo(k).nome)}</td>${n.map((x) => `<td>${x || "–"}</td>`).join("")}<td><b>${n.reduce((s, x) => s + x, 0)}</b></td></tr>`;
    }).join("");
  $("novembre").innerHTML = `<tr><th class="l">${esc(t("hCliente"))}</th><th>${esc(t("hDipendenti"))}</th><th>${esc(t("hAumento"))}</th><th>${esc(t("hAssorbito"))}</th><th>${esc(t("hDaPagare"))}</th></tr>` +
    clienti.map((c) => {
      const s = nov.filter((r) => r.cliente === c);
      const tot = (f) => s.reduce((x, r) => x + r[f], 0);
      return `<tr><td class="l">${esc(t("clienteN", { c }))}</td><td>${s.length}</td><td>${i18n.money(tot("aumento"))}</td><td>${i18n.money(tot("assorbito"))}</td><td><b>${i18n.money(tot("da_pagare"))}</b></td></tr>`;
    }).join("");
}

function filtrate() {
  const fc = $("f-cliente").value, fk = $("f-controllo").value;
  return risultato.anomalie.filter((a) => (!fc || a.cliente === fc) && (!fk || a.controllo === fk));
}

function tabella() {
  const rows = filtrate();
  $("anomalie").innerHTML = rows.length
    ? `<tr><th class="l">${esc(t("hMatricola"))}</th><th class="l">${esc(t("hControllo"))}</th><th class="l">${esc(t("hPriorita"))}</th><th>${esc(t("hAtteso"))}</th><th>${esc(t("hTrovato"))}</th><th>${esc(t("hDifferenza"))}</th></tr>` +
      rows.map((a) => `<tr><td class="l">${esc(a.matricola || "F24")}<div class="s-why">${esc(t("clienteN", { c: a.cliente }))}</div></td>
        <td class="l">${a.controllo} · ${esc(testo(a.controllo).nome)}<div class="cosa">${esc(testo(a.controllo).cosa_fare)}</div></td>
        <td class="l">${pill(a.priorita)}</td><td>${formato(a, a.atteso)}</td><td>${formato(a, a.trovato)}</td>
        <td>${a.differenza == null ? "–" : formato(a, a.differenza)}</td></tr>`).join("")
    : `<tr><td class="l"><span class="s-pill is-ok">${esc(t("nessuna"))}</span></td></tr>`;
}
$("f-cliente").addEventListener("change", tabella);
$("f-controllo").addEventListener("change", tabella);
$("stampa").addEventListener("click", () => print());

$("scarica-xlsx").addEventListener("click", () => {
  const { anomalie, corr, nov, cfg } = risultato;
  const valore = (v) => (v === "valido" ? t("valido") : v ?? "");
  const segnalazioni = [[t("hMatricola"), t("hCliente"), t("hControllo"), t("hDescrizione"), t("hPriorita"), t("hAtteso"),
    t("hTrovato"), t("hDifferenza"), t("hCosa"), t("hAssegnato"), t("hCorretto"), t("hNote")],
    ...anomalie.map((a) => [a.matricola || "F24", a.cliente, `${a.controllo} · ${testo(a.controllo).nome}`,
      testo(a.controllo).descrizione, priorita(a.priorita), valore(a.atteso), valore(a.trovato), a.differenza ?? "",
      testo(a.controllo).cosa_fare, "", "", ""])];
  const clienti = [...new Set(corr.map((r) => r.cliente))].sort();
  const perCliente = [[t("hControllo"), ...clienti.map((c) => t("clienteN", { c })), t("hTotale")],
    ...Object.keys(TESTI.it).map((k) => {
      const n = clienti.map((c) => anomalie.filter((a) => a.controllo === k && a.cliente === c).length);
      return [`${k} · ${testo(k).nome}`, ...n, n.reduce((s, x) => s + x, 0)];
    })];
  const novembreRows = [[t("hCliente"), t("hDipendenti"), t("hAumento"), t("hAssorbito"), t("hDaPagare")],
    ...clienti.map((c) => {
      const s = nov.filter((r) => r.cliente === c);
      const tot = (f) => Math.round(s.reduce((x, r) => x + r[f], 0) * 100) / 100;
      return [t("clienteN", { c }), s.length, tot("aumento"), tot("assorbito"), tot("da_pagare")];
    })];
  const oggi = new Date().toISOString().slice(0, 10);
  const parametri = [[t("xParametri"), ""], [t("xMese"), cfg.mese], [t("xAliquota"), cfg.aliquota], [t("xSoglia"), cfg.soglia],
    [t("xData"), oggi], [t("xFonte"), "https://github.com/D0M3N1C0X/controlli-cedolini"]];
  const bytes = writeXlsx([
    { name: t("xSegnalazioni"), rows: segnalazioni, widths: [12, 10, 28, 48, 10, 14, 14, 12, 48, 16, 12, 30] },
    { name: t("xPerCliente"), rows: perCliente, widths: [34, ...clienti.map(() => 12), 10] },
    { name: t("xNovembre"), rows: novembreRows, widths: [16, 12, 14, 14, 14] },
    { name: t("xParametri"), rows: parametri, widths: [34, 48] },
  ]);
  download(bytes, `${i18n.lang === "it" ? "segnalazioni" : "flags"}_${cfg.mese}.xlsx`,
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
});

i18n.apply();
i18n.onChange(() => { mostra(); if (files.mese) disegnaMappa(false); });
