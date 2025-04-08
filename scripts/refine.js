// scripts/refine.js
document.getElementById("refineForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const chirippId = document.getElementById("chirippId").value.trim();
  const updatedContext = document.getElementById("updatedContext").value.trim();
  const email = document.getElementById("email").value.trim();

  if (!chirippId || !updatedContext) {
    document.getElementById("refineStatus").innerText = "Please fill out required fields.";
    return;
  }

  const payload = {
    chiripp_id: chirippId,
    new_context: updatedContext,
    email: email || null
  };

  try {
    const webhookUrl = "https://hook.us2.make.com/your-refine-hook-url-here"; // 🔁 Replace this
    const response = await fetch(webhookUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!response.ok) throw new Error("Failed to submit refinement.");

    const result = await response.text();
    document.getElementById("refineStatus").innerText = "✅ Success: " + result;
  } catch (error) {
    document.getElementById("refineStatus").innerText = "❌ Error: " + error.message;
  }
});
