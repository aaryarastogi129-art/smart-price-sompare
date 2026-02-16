from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allows the extension to talk to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/analyze")
async def analyze(sku: str, price: float):
    # Simulated logic: If price < 150, it's a good deal
    avg_price = 150.0
    is_good = price < avg_price
    return {
        "status": "Success",
        "recommendation": "BUY NOW" if is_good else "WAIT",
        "savings": round(avg_price - price, 2) if is_good else 0,
        "history_avg": avg_price
    }