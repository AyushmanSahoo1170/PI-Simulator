const PI = "14159265358979323846264338327950288419716939937510582097494459230781640628620899862803482534211706";

const TIER_ORDER = { instant: 0, medium: 1, slow: 2, statistical: 3, reference: 4 };
const CATEGORY_ORDER = [
  "Geometric", "Infinite Series", "Infinite Products", "Probabilistic",
  "Iterative / AGM", "Definite Integrals", "Continued Fractions",
  "Modern Algorithms", "Special Functions",
];

const state = {
  methods: [],
  tier: "all",
  target: 32,
  samplesExp: 5.301,
  computing: false,
};

const $ = (id) => document.getElementById(id);

function safeStore(key, value) {
  try { localStorage.setItem(key, value); } catch (_) { /* private mode */ }
}

function safeRead(key) {
  try { return localStorage.getItem(key); } catch (_) { return null; }
}

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  $("themeToggle").textContent = theme === "light" ? "☾" : "☀";
}

function initTheme() {
  const saved = safeRead("pi-theme");
  const preferred = window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
  applyTheme(saved || preferred);
  $("themeToggle").onclick = () => {
    const next = document.documentElement.dataset.theme === "light" ? "dark" : "light";
    applyTheme(next);
    safeStore("pi-theme", next);
  };
}

function samplesFromExp(exp) {
  const raw = Math.pow(10, exp);
  const step = Math.pow(10, Math.max(Math.floor(Math.log10(raw)) - 2, 0));
  return Math.round(raw / step) * step;
}

function formatYear(year) {
  return year < 0 ? `${-year} BCE` : year;
}

function renderChips() {
  const box = $("tierChips");
  box.innerHTML = "";
  [["all", "All 50"], ["instant", "instant"], ["medium", "medium"],
   ["slow", "slow"], ["statistical", "statistical"], ["reference", "reference"]]
    .forEach(([tier, label]) => {
      const chip = document.createElement("button");
      chip.className = "chip" + (state.tier === tier ? " active" : "");
      chip.textContent = label;
      chip.onclick = () => {
        state.tier = tier;
        renderChips();
        renderGrid();
      };
      box.appendChild(chip);
    });
}

function sortedMethods() {
  return [...state.methods].sort(
    (a, b) => TIER_ORDER[a.tier] - TIER_ORDER[b.tier] || a.year - b.year
  );
}

function renderGrid() {
  const grid = $("methodGrid");
  grid.innerHTML = "";
  sortedMethods()
    .filter((m) => state.tier === "all" || m.tier === state.tier)
    .forEach((m) => {
      const card = document.createElement("article");
      card.className = "card";
      card.innerHTML = `
        <div class="card-top"><h3>${m.label}</h3>
          <span class="tier-dot tier-${m.tier}">${m.tier}</span></div>
        <p class="meta">${formatYear(m.year)} · ${m.category}</p>
        <p class="formula">${m.formula}</p>
        <p class="blurb">${m.blurb}</p>
        <div class="card-foot"></div>`;
      const foot = card.querySelector(".card-foot");
      if (m.runnable) {
        const btn = document.createElement("button");
        btn.className = "run-btn";
        btn.textContent = "Run";
        btn.onclick = () => runInCard(m, card, btn);
        foot.appendChild(btn);
      } else {
        foot.innerHTML = `<span class="ref-tag">reference only</span>`;
      }
      grid.appendChild(card);
    });
}

function span(ch, cls, index) {
  const s = document.createElement("span");
  s.className = "digit " + cls;
  s.textContent = ch;
  s.style.animationDelay = `${Math.min(index * 22, 2000)}ms`;
  return s;
}

function buildWall(d, wall) {
  wall.innerHTML = "";
  const ref = d.reference.slice(2);
  const val = d.value.startsWith("3.") ? d.value.slice(2) : "";
  wall.appendChild(span("3", "lead", 0));
  wall.appendChild(span(".", "lead", 1));
  let missAt = -1;
  for (let i = 0; i < val.length; i++) {
    let cls = "extra";
    if (missAt === -1 && i < ref.length) {
      if (val[i] === ref[i]) {
        cls = "ok";
      } else {
        cls = "miss";
        missAt = i;
      }
    }
    wall.appendChild(span(val[i], cls, i + 2));
  }
  return missAt;
}

function resultNote(d, missAt) {
  if (d.mode === "samples") {
    return `statistical estimate from ${d.work.toLocaleString()} ${d.work_label} — ` +
      `${Math.min(d.correct, d.shown)} of ${d.shown} shown decimals matched by luck, not convergence`;
  }
  if (d.passed) {
    return d.bonus > 0
      ? `all ${d.target} asked decimals verified — the computation is actually correct to ${d.correct}, the extra ${d.bonus} guard digits are simply not shown`
      : `all ${d.target} asked decimals verified — exact digits, no surplus`;
  }
  return `only ${d.correct} of ${d.target} asked decimals are correct — first miss at decimal ${missAt + 1}`;
}

function renderCardResult(m, card, d) {
  let box = card.querySelector(".card-result");
  if (!box) {
    box = document.createElement("div");
    box.className = "card-result";
    box.innerHTML = `
      <div class="cr-head"><span class="badge"></span><span class="muted mono-note"></span></div>
      <div class="digit-wall"></div>
      <p class="wall-note"></p>
      <div class="stats"></div>`;
    card.appendChild(box);
  }
  card.classList.add("expanded");
  const badge = box.querySelector(".badge");
  if (d.mode === "samples") {
    badge.className = "badge info";
    badge.textContent = `${Math.min(d.correct, d.shown)} DIGITS`;
  } else {
    badge.className = "badge " + (d.passed ? "pass" : "fail");
    badge.textContent = `${d.passed ? "PASS" : "FAIL"} · ${Math.min(d.correct, d.target)}/${d.target}`;
  }
  const missAt = buildWall(d, box.querySelector(".digit-wall"));
  box.querySelector(".wall-note").textContent = resultNote(d, missAt);
  box.querySelector(".stats").innerHTML = `
    <span class="stat">${d.work_label} <strong>${d.work.toLocaleString()}</strong></span>
    <span class="stat">time <strong>${d.ms.toLocaleString()} ms</strong></span>`;
}

async function callEstimate(m) {
  const body = { method: m.id, decimals: state.target };
  if (m.mode === "samples") body.samples = samplesFromExp(state.samplesExp);
  const res = await fetch("/api/estimate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Request failed");
  return data;
}

async function runInCard(m, card, btn) {
  btn.classList.add("busy");
  btn.textContent = "Computing…";
  try {
    const data = await callEstimate(m);
    renderCardResult(m, card, data);
    pushHistory(data);
  } catch (err) {
    card.classList.add("expanded");
    let box = card.querySelector(".card-result");
    if (!box) {
      box = document.createElement("div");
      box.className = "card-result";
      card.appendChild(box);
    }
    box.innerHTML = `<p class="wall-note">${err.message}</p>`;
  } finally {
    btn.classList.remove("busy");
    btn.textContent = "Run again";
  }
}

function resultCell(d) {
  if (d.mode === "samples") {
    return `<span class="badge info">${Math.min(d.correct, d.shown)} digits</span>`;
  }
  const cls = d.passed ? "pass" : "fail";
  const word = d.passed ? "PASS" : "FAIL";
  return `<span class="badge ${cls}">${word} ${Math.min(d.correct, d.target)}/${d.target}</span>`;
}

function pushHistory(d) {
  $("historyPanel").classList.remove("hidden");
  const tr = document.createElement("tr");
  const asked = d.mode === "samples" ? `${d.work.toLocaleString()} samples` : `${d.target} dp`;
  tr.innerHTML = `
    <td>${d.label}</td>
    <td class="num">${asked}</td>
    <td>${resultCell(d)}</td>
    <td class="num">${d.work.toLocaleString()} ${d.work_label}</td>
    <td class="num">${d.ms} ms</td>`;
  $("historyBody").prepend(tr);
}

async function computeAll() {
  if (state.computing) return;
  state.computing = true;
  const btn = $("computeAllBtn");
  btn.classList.add("busy");
  btn.textContent = "Computing…";
  const board = $("boardCard");
  board.classList.remove("hidden");
  $("boardTarget").textContent = state.target;
  const body = $("boardBody");
  body.innerHTML = "";
  const runnable = sortedMethods().filter((m) => m.runnable);
  const started = performance.now();
  let done = 0;
  for (const m of runnable) {
    const tr = document.createElement("tr");
    tr.className = "reveal";
    tr.innerHTML = `
      <td>${m.label}</td>
      <td><span class="tier-dot tier-${m.tier}">${m.tier}</span></td>
      <td class="num">computing…</td><td class="num">—</td><td class="num">—</td>`;
    body.appendChild(tr);
    $("boardStatus").textContent = `${done}/${runnable.length} · ${m.label}` +
      (m.id === "nilakantha" && state.target >= 16 ? " (this one suffers on purpose — wait)" : "");
    try {
      const d = await callEstimate(m);
      tr.children[2].innerHTML = resultCell(d);
      tr.children[3].textContent = `${d.work.toLocaleString()} ${d.work_label}`;
      tr.children[4].textContent = `${d.ms.toLocaleString()} ms`;
    } catch (err) {
      tr.children[2].innerHTML = `<span class="badge fail">ERROR</span>`;
      tr.children[3].textContent = err.message;
    }
    done += 1;
  }
  const seconds = ((performance.now() - started) / 1000).toFixed(1);
  $("boardStatus").textContent = `${runnable.length} engines · finished in ${seconds} s`;
  btn.classList.remove("busy");
  btn.textContent = "Compute all 29 engines";
  state.computing = false;
}

function renderCatalogue() {
  const box = $("catalogue");
  box.innerHTML = "";
  CATEGORY_ORDER.forEach((category) => {
    const items = sortedMethods().filter((m) => m.category === category);
    if (!items.length) return;
    const group = document.createElement("div");
    group.className = "cat-group";
    group.innerHTML = `<h3>${category}</h3>`;
    items.forEach((m) => {
      const row = document.createElement("div");
      row.className = "cat-item";
      row.innerHTML = `
        <strong>${m.label}</strong>
        <span class="yr">${formatYear(m.year)}</span>
        <span class="desc">${m.blurb}</span>
        <span class="tier-dot tier-${m.tier}">${m.tier}</span>`;
      group.appendChild(row);
    });
    box.appendChild(group);
  });
}

function wireControls() {
  document.querySelectorAll("#targetSeg button").forEach((b) => {
    b.onclick = () => {
      state.target = Number(b.dataset.target);
      document
        .querySelectorAll("#targetSeg button")
        .forEach((x) => x.classList.toggle("active", x === b));
    };
  });
  $("samplesRange").oninput = (e) => {
    state.samplesExp = Number(e.target.value);
    $("samplesValue").textContent = samplesFromExp(state.samplesExp).toLocaleString();
  };
  $("computeAllBtn").onclick = computeAll;
}

async function init() {
  $("heroDigits").textContent = ("3" + PI).repeat(4);
  initTheme();
  renderChips();
  wireControls();
  try {
    const res = await fetch("/api/methods");
    state.methods = await res.json();
    renderGrid();
    renderCatalogue();
  } catch {
    $("methodGrid").innerHTML =
      "<p class='muted'>Could not load the engines — is the server running?</p>";
  }
}

init();
