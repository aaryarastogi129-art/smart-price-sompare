import os
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# FIX: Forces Python to use the valid certificates you located
os.environ['REQUESTS_CA_BUNDLE'] = r"C:\Users\hp\smart-price-compare\venv\Lib\site-packages\certifi\cacert.pem"
os.environ['SSL_CERT_FILE'] = r"C:\Users\hp\smart-price-compare\venv\Lib\site-packages\certifi\cacert.pem"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_driver():
    chrome_options = Options()
    
    # ADD THE '#' TO DISABLE HEADLESS MODE
    # chrome_options.add_argument("--headless=new") 
    
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # This forces Chrome to ignore K7's network proxy/jail
    chrome_options.add_argument("--proxy-server='direct://'")
    chrome_options.add_argument("--proxy-bypass-list=*")
    chrome_options.add_argument("--ignore-certificate-errors")
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)
@app.get("/analyze")
async def analyze(url: str):
    driver = None
    try:
        driver = get_driver()
        driver.set_page_load_timeout(30)
        
        print(f"DEBUG: Attempting to reach {url}")
        
        try:
            driver.get(url)
        except Exception as e:
            # FORCE SCREENSHOT ON FAILURE
            driver.save_screenshot("failed_connection.png")
            print(f"DEBUG: Connection failed, saved failed_connection.png. Error: {e}")
            raise e

        time.sleep(5) 
        driver.save_screenshot("debug_amazon.png")
        print("DEBUG: Successfully reached page. Saved debug_amazon.png")
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        price_selectors = ["span.a-price-whole", "span#priceblock_ourprice", "span.a-offscreen"]
        
        price_el = None
        for selector in price_selectors:
            price_el = soup.select_one(selector)
            if price_el: break
        
        if price_el:
            raw_text = price_el.text.replace(",", "").replace("₹", "").strip()
            numeric_price = float(''.join(c for c in raw_text if c.isdigit() or c == '.'))
            return {
                "status": "Success",
                "price": numeric_price,
                "recommendation": "GOOD DEAL" if numeric_price < 500 else "WAIT",
                "history_avg": 500.0
            }
        else:
            return {"status": "Error", "message": "Price not found on page."}

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        return {"status": "Error", "message": str(e)}
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)