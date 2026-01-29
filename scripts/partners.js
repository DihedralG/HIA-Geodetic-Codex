// Update these manually after your first run
const snapshot = {
  score: "—",            // e.g., "72.4"
  label: "Awaiting baseline run",
  models: 0,             // e.g., 5
  baseline: "Baseline v0.1",
  lockTimestamp: "2026-01-28T19:xx:xx-05:00"
};

document.getElementById("cdiScore").textContent = snapshot.score;
document.getElementById("cdiLabel").textContent = snapshot.label;
document.getElementById("cdiModels").textContent = `${snapshot.models} models`;
document.getElementById("cdiBaseline").textContent = snapshot.baseline;
document.getElementById("lockTimestamp").textContent = snapshot.lockTimestamp;