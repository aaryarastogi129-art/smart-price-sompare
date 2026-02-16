document.getElementById("runBtn").addEventListener("click", async () => {
    const resultDiv = document.getElementById("res");
    resultDiv.innerText = "🔍 Scrapping live price...";

    // Get current tab URL
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    try {
        const response = await fetch(`http://127.0.0.1:8000/analyze?url=${encodeURIComponent(tab.url)}`);
        const data = await response.json();

        if (data.status === "Success") {
            resultDiv.innerHTML = `
                <div style="font-size: 18px; color: #10b981; font-weight: bold;">₹${data.price}</div>
                <div style="margin: 10px 0;">Advice: <strong>${data.recommendation}</strong></div>
                <div style="font-size: 11px; color: #64748b;">Avg: ₹${data.history_avg}</div>
            `;
        } else {
            resultDiv.innerText = "Error: " + data.message;
        }
    } catch (err) {
        resultDiv.innerText = "Check if Python server is running!";
    }
});