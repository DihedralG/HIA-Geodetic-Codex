// scripts/peer-review.js
document.getElementById("peerReviewForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const accessCode = document.getElementById("accessCode").value.trim();
  const file = document.getElementById("fileUpload").files[0];
  const context = document.getElementById("contextInput").value.trim();
  const type = document.getElementById("contentType").value;

  if (!file || !accessCode) {
    document.getElementById("submissionStatus").innerText = "❗ Please upload a file and enter an access code.";
    return;
  }

  const formData = new FormData();
  formData.append("access_code", accessCode);
  formData.append("file", file);
  formData.append("content_type", type);
  formData.append("context", context);

  try {
    const webhookUrl = "https://hook.us2.make.com/YOUR_PEER_REVIEW_WEBHOOK"; // 🔁 Replace with your actual Make.com URL
    const response = await fetch(webhookUrl, {
      method: "POST",
      body: formData
    });

    if (!response.ok) throw new Error("Submission failed.");

    const result = await response.text();
    document.getElementById("submissionStatus").innerText = "✅ Submitted! " + result;
  } catch (err) {
    document.getElementById("submissionStatus").innerText = "❌ Error: " + err.message;
  }
});
