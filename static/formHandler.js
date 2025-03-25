

/**
 * Returns an object with values from all input, textarea, and select fields (using element IDs as keys)
 * Skips elements that you don't want to persist (e.g. the "speech-draft" textarea).
 */
function getAllFieldData() {
  const fields = document.querySelectorAll("input, textarea, select");
  let data = {};

  fields.forEach(el => {
      if (el.id && el.id !== "speech-draft") {
          if (el.type === "checkbox" || el.type === "radio") {
              data[el.id] = el.checked;
          } else if (el.multiple) {
              // Capture all selected values for multi-select fields
              let selectedValues = Array.from(el.selectedOptions).map(option => option.value);
              data[el.id] = selectedValues.join(", "); // Convert to comma-separated string
          } else {
              data[el.id] = el.value;
          }
      }
  });
  console.log("Collected Data:", data); // Debugging
  return data;
}
  
  /**
   * Saves current page data in localStorage under a page-specific key.
   */
  function saveCurrentPageData(pageKey) {
    const data = getAllFieldData();
    localStorage.setItem(pageKey, JSON.stringify(data));
  }
  
  /**
   * Loads saved data from localStorage for the given pageKey and populates matching fields.
   */
  function loadFormData(pageKey) {
    const dataStr = localStorage.getItem(pageKey);
    if (!dataStr) return;
    try {
        const data = JSON.parse(dataStr);
        for (const key in data) {
            if (key === "speech-draft") continue;
            const field = document.getElementById(key);
            if (field) {
                if (field.type === "checkbox" || field.type === "radio") {
                    field.checked = data[key];
                } else if (field.multiple) {
                    let values = data[key].split(", "); // Convert CSV back to array
                    for (let option of field.options) {
                        option.selected = values.includes(option.value);
                    }
                } else {
                    field.value = data[key];
                }
            }
        }
    } catch (err) {
        console.error("Error loading form data:", err);
    }
}

  
  /**
   * Determines the current page key based on the URL pathname.
   */
  function getCurrentPageKey() {
    let path = window.location.pathname;
    if (path === "/" || path.includes("page1")) return "page1Data";
    if (path.includes("page2")) return "page2Data";
    if (path.includes("page3")) return "page3Data";
    return "defaultData";
  }
  
  /**
   * Saves the current page data and redirects to a new destination.
   */
  function saveAndRedirect(destination, pageKey) {
    saveCurrentPageData(pageKey);
    window.location.href = destination;
  }

  function downloadAsText(text) {
    const blob = new Blob([text], { type: "text/plain" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "Final_Speech.txt";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

  function generatePDF(text) {
    const { jsPDF } = window.jspdf;
    if (!jsPDF) {
        console.error("jsPDF is not available!");
        alert("Error: jsPDF is not loaded properly.");
        return;
    }

    const doc = new jsPDF();
    const margin = 10;
    const pageWidth = doc.internal.pageSize.getWidth() - 2 * margin;
    const pageHeight = doc.internal.pageSize.getHeight() - 2 * margin;
    
    // Split text into multiple lines that fit within the page width
    const lines = doc.splitTextToSize(text, pageWidth);
    
    let y = margin + 10; // Initial Y position for text

    for (let i = 0; i < lines.length; i++) {
        if (y + 10 > pageHeight) {  // Check if we're running out of space on the page
            doc.addPage();  // Add a new page
            y = margin;  // Reset Y position for the new page
        }
        doc.text(lines[i], margin, y);
        y += 10;  // Move down for the next line
    }

    doc.save("Final_Speech.pdf"); // Download PDF
}

  
  /**
   * On the final page, save page3 data, combine with data from page1 and page2,
   * then send the combined data to the backend and update the generated speech textarea.
   */
  function saveFinalAndDownload() {
    saveCurrentPageData("page3Data");
  
    const page1Data = JSON.parse(localStorage.getItem("page1Data") || "{}");
    const page2Data = JSON.parse(localStorage.getItem("page2Data") || "{}");
    const page3Data = JSON.parse(localStorage.getItem("page3Data") || "{}");
  
    // Combine all data (later values overwrite earlier ones if keys match)
    const combinedData = Object.assign({}, page1Data, page2Data, page3Data, { page: "page3" });
  
    fetch('/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(combinedData)
    })
    .then(response => response.json())
    .then(result => {
      // Print the response in the textarea with id "speech-draft"
    //   document.getElementById("speech-draft").value = result.response;
      // Optionally, clear localStorage here if you want to reset the form completely:
      // localStorage.clear();
      const speechText = result.response; // Get text from backend
      // Extract speech (until "key_themes")
        const speechMatch = speechText.match(/"speech":\s*"([\s\S]*?)"\s*,\s*"key_themes"/);
        const speech = speechMatch ? speechMatch[1].trim() : "";

        // Extract key themes
        const keyThemesMatch = speechText.match(/"key_themes":\s*\[\s*([\s\S]*?)\s*\]/);
        const keyThemes = keyThemesMatch 
            ? keyThemesMatch[1].match(/"([^"]+)"/g).map(s => s.replace(/"/g, '')).join(', ') 
            : "";

        // Extract category
        const categoryMatch = speechText.match(/"category":\s*"([^"]+)"/);
        const category = categoryMatch ? categoryMatch[1] : "";

        // Extract explanation (until end)
        const explanationMatch = speechText.match(/"explanation":\s*"([\s\S]*?)"\s*\}/);
        const explanation = explanationMatch ? explanationMatch[1].trim() : "";

        console.log("Speech:", speech);
        console.log("Key Themes:", keyThemes);
        console.log("Category:", category);
        console.log("Explanation:", explanation);
        document.getElementById("speech-draft").value = speech; // Display in textarea
        const selectedFormat = document.getElementById("export-options").value;
        switch (selectedFormat) {
            case "text":
                downloadAsText(speech);
                break;
            case "pdf":
                generatePDF(speech);
                break;
            case "json":
                downloadAsText(speechText)
                break;
            case "audio":
                alert("Audio export is not implemented yet.");
                break;
            default:
                alert("Please select a valid format!");
        }
    })
    .catch(error => {
      console.error('Error:', error);
      alert("Error communicating with server.");
    });
  }
  
  // On DOMContentLoaded, load any saved data and override button actions.
  document.addEventListener("DOMContentLoaded", function() {
    const currentKey = getCurrentPageKey();
    loadFormData(currentKey);
    // localStorage.clear();
    // Override Next buttons on page1 and page2 (assumed to have class "next-button")
    const nextButtons = document.querySelectorAll('.next-button');
    nextButtons.forEach(btn => {
      btn.removeAttribute("onclick"); // Remove inline onclick attributes
      btn.addEventListener("click", function(e) {
        e.preventDefault();
        let destination = "";
        if (currentKey === "page1Data") {
          destination = "/page2"; // Use your Flask route for page2
        } else if (currentKey === "page2Data") {
          destination = "/page3"; // Use your Flask route for page3
        }
        saveAndRedirect(destination, currentKey);
      });
    });
  
    // Override the Download Final Speech button on page3.
    const downloadButton = Array.from(document.querySelectorAll("button"))
      .find(btn => btn.textContent.trim() === "Download Final Speech");
    if (downloadButton) {
      downloadButton.removeAttribute("onclick");
      downloadButton.addEventListener("click", function(e) {
        e.preventDefault();
        saveFinalAndDownload();
      });
    }
  });
  