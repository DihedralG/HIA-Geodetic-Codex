(async function () {
  const params = new URLSearchParams(window.location.search);
  const id = (params.get("id") || "").toUpperCase().trim();

  const title = document.getElementById("title");
  const subtitle = document.getElementById("subtitle");
  const pills = document.getElementById("pills");
  const summary = document.getElementById("summary");
  const kpi = document.getElementById("kpi");
  const assets = document.getElementById("assets");
  const pains = document.getElementById("pains");
  const notes = document.getElementById("notes");
  const idEl = document.getElementById("id");

  function esc(s) {
    return (s ?? "").toString()
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  async function loadMember(code) {
    const res = await fetch("./data/members.sopa.json");
    if (!res.ok) throw new Error(`Missing member file for ${code} (${res.status})`);
    return await res.json();
  }

  function pill(text) {
    const span = document.createElement("span");
    span.className = "pill";
    span.textContent = text;
    return span;
  }

  function render(m) {
    title.textContent = `${m.name} (${m.code})`;
    subtitle.textContent = `${m.primary_sop || "SOPA"} • ${m.group || "Unassigned"} • Tier ${m.tier}`;

    pills.innerHTML = "";
    pills.appendChild(pill(`Tier ${m.tier}`));
    if (m.confidence) pills.appendChild(pill(`Confidence ${m.confidence.low}-${m.confidence.high}`));
    if (m.role) pills.appendChild(pill(m.role));
    if (m.tags?.length) pills.appendChild(pill(m.tags.slice(0, 2).join(" • ")));

    summary.textContent = m.summary || "";

    const scores = m.kpi_scores || {};
    const labels = [
      ["Security & Stability", "security_stability"],
      ["Economic Throughput", "economic_throughput"],
      ["Infrastructure Resilience", "infrastructure_resilience"],
      ["Governance & Compliance", "governance_compliance"],
      ["Environmental & Climate", "environment_climate"],
      ["Data Participation", "data_participation"],
      ["Social Impact", "social_impact"]
    ];

    kpi.innerHTML = labels.map(([label, key]) => {
      const v = (scores[key] ?? "—");
      return `<div class="panel" style="margin:0;">
        <div class="k">${esc(label)}</div>
        <div class="v">${esc(v)}</div>
      </div>`;
    }).join("");

    assets.innerHTML = (m.assets || []).map(x => `<li>${esc(x)}</li>`).join("");
    pains.innerHTML  = (m.pain_points || []).map(x => `<li>${esc(x)}</li>`).join("");

    notes.textContent = m.notes || "";
    idEl.textContent = m.code;
  }

  try {
    if (!id) {
      title.textContent = "Member not specified";
      subtitle.textContent = "Add ?id=USA (example) to the URL.";
      return;
    }
    const m = await loadMember(id);
    render(m);
  } catch (err) {
    console.error(err);
    title.textContent = `Member not found (${id || "—"})`;
    subtitle.textContent = "Check the ID code or ensure the JSON file exists in /sop/sopa/data/cards/";
  }
})();