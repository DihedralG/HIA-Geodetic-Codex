// glyphs.js
// Load and display ChiRIPP glyph records from Dropbox JSON logs

document.addEventListener("DOMContentLoaded", function () {
    const searchForm = document.querySelector("#searchForm");
    const contentTypeInput = document.querySelector("#contentType");
    const accessCodeInput = document.querySelector("#accessCode");
    const emailInput = document.querySelector("#email");
    const glyphList = document.querySelector("#glyphList");
  
    // URL of the Dropbox folder JSON index
    const dropboxFeed = "https://www.dropbox.com/scl/fo/YOUR_PUBLIC_FOLDER_ID/json?dl=1"; // Replace with your folder path
  
    async function fetchGlyphData() {
      try {
        const response = await fetch(dropboxFeed);
        const data = await response.json();
        return data;
      } catch (error) {
        console.error("Error fetching glyph data:", error);
        return [];
      }
    }
  
    function renderGlyphCards(dataArray, filters = {}) {
      glyphList.innerHTML = "";
      const template = document.querySelector("#glyphCard");
  
      dataArray.forEach((data) => {
        const matchContentType =
          !filters.contentType || filters.contentType === "All" || data.type === filters.contentType;
        const matchAccessCode =
          !filters.accessCode || data.code?.toLowerCase().includes(filters.accessCode.toLowerCase());
        const matchEmail =
          !filters.email || data.email?.toLowerCase().includes(filters.email.toLowerCase());
  
        if (matchContentType && matchAccessCode && matchEmail) {
          const card = template.content.cloneNode(true);
          card.querySelector("img").src = data.img || "placeholder.jpg";
          card.querySelector(".type").textContent = data.type;
          card.querySelector(".email").textContent = data.email;
          card.querySelector(".code").textContent = data.code || "--";
          card.querySelector(".summary").textContent = data.summary || "(No summary provided.)";
          glyphList.appendChild(card);
        }
      });
    }
  
    // Load all on page load
    fetchGlyphData().then((dataArray) => renderGlyphCards(dataArray));
  
    // Search form listener
    searchForm.addEventListener("submit", function (e) {
      e.preventDefault();
      const filters = {
        contentType: contentTypeInput.value,
        accessCode: accessCodeInput.value.trim(),
        email: emailInput.value.trim(),
      };
      fetchGlyphData().then((dataArray) => renderGlyphCards(dataArray, filters));
    });
  });
  