document.addEventListener("DOMContentLoaded", () => {
  const logContainer = document.getElementById("glyphLog");

  fetch("/data/glyph-log-data.json")
    .then((response) => response.json())
    .then((data) => {
      data.forEach((entry) => {
        const card = document.createElement("div");
        card.className = "glyph-card";
        card.innerHTML = `
          <h3>${entry.title}</h3>
          <p><strong>Location:</strong> ${entry.location}</p>
          <p><strong>Type:</strong> ${entry.type}</p>
          <p><strong>Timestamp:</strong> ${new Date(entry.timestamp).toLocaleString()}</p>
        `;
        logContainer.appendChild(card);
      });
    })
    .catch((error) => {
      logContainer.innerHTML = "<p>Error loading glyph data.</p>";
      console.error("Error fetching JSON:", error);
    });
});