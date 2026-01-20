(async function () {
  const grid = document.getElementById("grid");
  const qEl = document.getElementById("q");
  const tierEl = document.getElementById("tier");
  const groupEl = document.getElementById("group");
  const countEl = document.getElementById("count");

  function esc(s) {
    return (s ?? "").toString()
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  async function loadIndex() {
    const res = await fetch("/sop/sopa/data/members.sopa.json");
    if (!res.ok) throw new Error(`Failed to load members.sopa.json (${res.status})`);
    return await res.json();
  }

  function populateGroups(items) {
    const groups = Array.from(new Set(items.map(x => x.group).filter(Boolean))).sort();
    for (const g of groups) {
      const opt = document.createElement("option");
      opt.value = g;
      opt.textContent = g;
      groupEl.appendChild(opt);
    }
  }

  function matches(item, q, tier, group) {
    const hay = [
      item.name, item.code, item.group, item.primary_sop,
      ...(item.tags || [])
    ].join(" ").toLowerCase();

    if (q && !hay.includes(q)) return false;
    if (tier && item.tier !== tier) return false;
    if (group && item.group !== group) return false;
    return true;
  }

  function render(items) {
    const q = (qEl.value || "").trim().toLowerCase();
    const tier = tierEl.value;
    const group = groupEl.value;

    const filtered = items.filter(it => matches(it, q, tier, group));
    countEl.textContent = `${filtered.length} shown / ${items.length} total`;

    grid.innerHTML = filtered.map(it => {
      const href = `/member.html?id=${encodeURIComponent(it.code)}`;
      const conf = it.confidence ? `${it.confidence.low}-${it.confidence.high}` : "—";
      return `
        <div class="card">
          <h3>${esc(it.name)} <span class="muted">(${esc(it.code)})</span></h3>
          <div>
            <span class="pill">Tier ${esc(it.tier)}</span>
            <span class="pill">${esc(it.group || "Unassigned")}</span>
            <span class="pill">Conf ${esc(conf)}</span>
          </div>
          <div class="kv">
            <div><span class="muted">Primary SOP:</span> ${esc(it.primary_sop || "SOPA")}</div>
            <div><span class="muted">Role:</span> ${esc(it.role || "Baseline")}</div>
          </div>
          <div class="linkrow">
            <a href="${href}">Open data card →</a>
          </div>
        </div>
      `;
    }).join("");
  }

  try {
    const index = await loadIndex();
    const items = index.items || [];
    populateGroups(items);

    render(items);

    [qEl, tierEl, groupEl].forEach(el => {
      el.addEventListener("input", () => render(items));
      el.addEventListener("change", () => render(items));
    });
  } catch (err) {
    console.error(err);
    grid.innerHTML = `<div class="card">Error loading members. Check console.</div>`;
  }
})();