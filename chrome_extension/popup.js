document.getElementById("runBtn").addEventListener("click", async () => {
  const resultDiv = document.getElementById("res");
  resultDiv.innerText = "Processing...";

  // Simulated data (Next step: scrape real data from Amazon)
  const price = 129.99;
  const sku = "PROD123";

  try {
    const response = await fetch(
      `http://127.0.0.1:8000/analyze?sku=${sku}&price=${price}`,
    );
    const data = await response.json();
    resultDiv.innerHTML = `Result: ${data.recommendation}<br>Avg Price: $${data.history_avg}`;
  } catch (err) {
    resultDiv.innerText = "Error: Is the Python server running?";
  }
});
