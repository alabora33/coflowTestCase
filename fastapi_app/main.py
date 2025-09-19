from fastapi import FastAPI, Header, HTTPException
from typing import List, Optional
from dotenv import load_dotenv
import os
load_dotenv()

app = FastAPI(title="Stock API")

API_KEY = os.getenv("API_KEY")

def check_key(x_api_key: Optional[str]):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

# Basit örnek envanter
INVENTORY = {
    "SKU001": 12,
    "SKU002": 0,
    "SKU003": 42,
    "SKU004": 7,
    "SKU005": 19,
    "SKU006": 3,
    "SKU007": 8,
    "SKU008": 15,
    "SKU009": 27,
    "SKU010": 1,
}

@app.get("/api/v1/stock")
def stock(sku: str, x_api_key: Optional[str] = Header(None)):
    check_key(x_api_key)
    if sku not in INVENTORY:
        raise HTTPException(status_code=404, detail="SKU not found")
    return {"sku": sku, "qty": INVENTORY[sku]}

@app.get("/api/v1/stock/bulk")
def stock_bulk(x_api_key: Optional[str] = Header(None)):
    check_key(x_api_key)
    return [{"sku": k, "qty": v} for k, v in list(INVENTORY.items())]
