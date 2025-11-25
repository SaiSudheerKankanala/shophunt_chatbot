from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
import pandas as pd

app = FastAPI()

# CORS FIX
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    question: str

def fetch_data():
    conn = mysql.connector.connect(
        host="ballast.proxy.rlwy.net",
        user="root",
        password="SjmGYKKMDAYKGzYQzlkISNiLSMeBvlfi",
        database="railway",
        port=19240
    )
    df = pd.read_sql("SELECT * FROM product_inventory;", conn)
    conn.close()

    df.columns = [
        "record_id","shop_name","shop_owner","shop_address","product_name",
        "product_brand","product_mrp","product_size","quantity","selling_price",
        "manufacture_date","expiry_date","is_available","stock_status",
        "created_at","last_updated"
    ]

    return df

@app.post("/ask")
def ask(query: Query):
    df = fetch_data()
    q = query.question.lower()

    products = df["product_name"].str.lower().tolist()
    matches = [p for p in products if p in q]

    if not matches:
        return {"response": "Product unavailable"}

    p_name = matches[0]
    row = df[df["product_name"].str.lower() == p_name].iloc[0]

    return {
        "shop_name": row["shop_name"],
        "address": row["shop_address"],
        "stock_status": row["stock_status"]
    }

@app.get("/")
def home():
    return {"status": "Backend running"}
