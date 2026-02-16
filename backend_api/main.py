import os
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

app = FastAPI()

# Enable CORS so your extension can talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_driver():
    chrome_options = Options()
    # On a new PC, keep headless OFF first to see it working
    # chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

@app.get("/analyze")
async def analyze(url: str):
    driver = None
    try:
        driver = get_driver()
        print(f"Scraping: {url}")
        
        driver.get(url)
        time.sleep(5)  # Let dynamic content load
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Amazon Price Selectors
        price_selectors = ["span.a-price-whole", "span#priceblock_ourprice", "span.a-offscreen"]
        price_el = None
        for s in price_selectors:
            price_el = soup.select_one(s)
            if price_el: break
            
        if price_el:
            raw_text = price_el.text.replace(",", "").replace("₹", "").strip()
            # Extract just the numbers
            numeric_price = float(''.join(c for c in raw_text if c.isdigit() or c == '.'))
            
            return {
                "status": "Success",
                "price": numeric_price,
                "recommendation": "GOOD DEAL" if numeric_price < 500 else "WAIT",
                "history_avg": 500.0
            }
        return {"status": "Error", "message": "Price element not found"}

    except Exception as e:
        return {"status": "Error", "message": str(e)}
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)