// scripts/peer-review.js
document.getElementById("peerReviewForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const accessCode = document.getElementById("accessCode").value.trim();
  const file = document.getElementById("fileUpload").files[0];
  const context = document.getElementById("contextInput").value.trim();
  const type = document.getElementById("contentType").value;

  const formData = new FormData();
  formData.append("access_code", accessCode);
  formData.append("file", file);
  formData.append("content_type", type);
  formData.append("context", context);

  const response = await fetch("https://hook.us2.make.com/7smugsxhu83tf4d6uy7eyu1mkmyc6x45", {
    method: "POST",
    body: formData
  });

  const result = await response.text();
  document.getElementById("submissionStatus").innerText = result;
});
