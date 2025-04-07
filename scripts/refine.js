// scripts/refine.js
document.getElementById("refineForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const chirippId = document.getElementById("chirippId").value.trim();
  const updatedContext = document.getElementById("updatedContext").value.trim();

  const payload = {
    chiripp_id: chirippId,
    new_context: updatedContext
  };

  const response = await fetch("https://hook.us2.make.com/your-refine-hook-url-here", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  const result = await response.text();
  document.getElementById("refineStatus").innerText = result;
});