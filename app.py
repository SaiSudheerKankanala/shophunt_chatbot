# app.py
import mysql.connector
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

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
    df = fetch_data()   # Load DB ONLY when request comes

    q = query.question.lower()
    product_list = df["product_name"].str.lower().tolist()

    match = [p for p in product_list if p in q]
    if not match:
        return {"response": "Product unavailable"}

    product = match[0]
    row = df[df["product_name"].str.lower() == product]

    if row.empty:
        return {"response": "Product unavailable"}

    row = row.iloc[0]

    return {
        "shop_name": row["shop_name"],
        "address": row["shop_address"],
        "stock_status": row["stock_status"]
    }


@app.get("/")
def home():
    return {"status": "Backend running"}
