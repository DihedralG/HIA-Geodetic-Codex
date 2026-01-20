(async function () {
  const grid = document.getElementById("grid");

  function esc(s) {
    return (s ?? "").toString()
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  async function loadPilots() {
    const res = await fetch("https://dihedralg.github.io/HIA-Geodetic-Codex/data/members.sopa.json");
    if (!res.ok) throw new Error(`Failed to load pilots.index.schema.json (${res.status})`);
    return await res.json();
  }

  try {
    const data = await loadPilots();
    const items = data.items || [];
    grid.innerHTML = items.map(p => {
      return `
        <div class="card">
          <h3>${esc(p.name)}</h3>
          <div>
            <span class="pill">Pilot</span>
            <span class="pill">Tier target: ${esc(p.target_tier || "—")}</span>
            <span class="pill">Focus: ${esc((p.focus || []).slice(0,2).join(" • ") || "—")}</span>
          </div>
          <p class="muted">${esc(p.summary || "")}</p>
          ${(p.next_actions?.length)
            ? `<strong>Next actions</strong><ul class="list">${p.next_actions.map(a => `<li>${esc(a)}</li>`).join("")}</ul>`
            : ``}
        </div>
      `;
    }).join("");
  } catch (err) {
    console.error(err);
    grid.innerHTML = `<div class="card">Error loading pilots. Check console.</div>`;
  }
})();