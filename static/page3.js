document.addEventListener("DOMContentLoaded", function() {
    // Find the "Generate Speech Draft" button by its text content.
    const genButton = Array.from(document.querySelectorAll("button"))
      .find(btn => btn.textContent.trim() === "Generate Speech Draft");
      
    if (genButton) {
      genButton.addEventListener("click", function(e) {
        e.preventDefault();
        generateSpeechDraft();
      });
    }
  });
  
  function generateSpeechDraft() {
    // Retrieve saved data from page1, page2, and page3.
    const page1Data = JSON.parse(localStorage.getItem("page1Data") || "{}");
    const page2Data = JSON.parse(localStorage.getItem("page2Data") || "{}");
    const page3Data = JSON.parse(localStorage.getItem("page3Data") || "{}");
    
    // Combine all data into one object.
    const combinedData = Object.assign({}, page1Data, page2Data, page3Data, { page: "page3" });
    
    // Send the combined data to the Flask server's /process endpoint.
    fetch('/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(combinedData)
    })
    .then(response => response.json())
    .then(result => {
      // Print the response (final speech draft) in the textarea with id "speech-draft"
      document.getElementById("speech-draft").value = result.response;
    })
    .catch(error => {
      console.error("Error generating speech draft:", error);
      document.getElementById("speech-draft").value = "Error generating speech draft.";
    });
  }
  