let liveData = null;
let kv2021 = null;
let dataLoaded = false;

async function loadData() {
  if (dataLoaded) return;
  const [liveRes, kvRes] = await Promise.all([
    fetch("data/live_turnout.json", { cache: "no-store" }),
    fetch("data/kv2021_turnout.json", { cache: "no-store" }),
  ]);

  if (!liveRes.ok) {
    throw new Error("Kan ikke hente live-data");
  }
  if (!kvRes.ok) {
    throw new Error("Kan ikke hente data fra 2021");
  }

  liveData = await liveRes.json();
  kv2021 = await kvRes.json();
  dataLoaded = true;
}

function normalizeName(str) {
  return str
    .toLowerCase()
    .replace("kommune", "")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/æ/g, "ae")
    .replace(/ø/g, "oe")
    .replace(/å/g, "aa");
}

function findKommune(input) {
  if (!input || !liveData) return null;
  const norm = normalizeName(input);
  const kommuner = liveData.kommuner;

  let exact = null;
  let partial = null;

  for (const [kode, info] of Object.entries(kommuner)) {
    const n = normalizeName(info.navn);

    if (n === norm) {
      exact = { kode, ...info };
      break;
    }
    if (!partial && n.includes(norm)) {
      partial = { kode, ...info };
    }
  }

  return exact || partial;
}

async function lookup() {
  const btn = document.getElementById("lookup-btn");
  const box = document.getElementById("result");
  const q = document.getElementById("kommune-input").value.trim();

  box.style.display = "block";
  box.innerHTML = "Henter data ...";
  btn.disabled = true;

  try {
    await loadData();
    const match = findKommune(q);

    if (!match) {
      box.innerHTML = '<span class="error">Jeg kunne ikke finde den kommune. Prøv at skrive kun kommunenavnet.</span>';
      return;
    }

    const kv = kv2021[match.kode] || {};
    const before = kv.stemmeprocent;
    const now = match.stemmeprocent;
    const diff = (typeof before === "number" && typeof now === "number")
      ? (now - before).toFixed(1)
      : null;

    box.innerHTML = `
      <strong>${match.navn} Kommune</strong><br>
      Aktuel stemmeprocent i dag: ${now ?? "ukendt"} %<br>
      Ved kommunalvalget i 2021: ${before ?? "ukendt"} %<br>
      ${diff !== null ? "Forskel i procentpoint: " + diff : ""}
      <br><span class="small">Senest opdateret: ${liveData.timestamp}</span>
    `;
  } catch (err) {
    console.error(err);
    box.innerHTML = '<span class="error">Der skete en fejl, da jeg hentede data. Prøv igen senere.</span>';
  } finally {
    btn.disabled = false;
  }
}
