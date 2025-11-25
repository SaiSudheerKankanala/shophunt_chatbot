# main.py
import os
import mysql.connector
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# ------------------------------------------
# CONNECT TO MYSQL (Railway)
# ------------------------------------------
conn = mysql.connector.connect(
    host="ballast.proxy.rlwy.net",
    user="root",
    password="SjmGYKKMDAYKGzYQzlkISNiLSMeBvlfi",
    database="railway",
    port=19240
)

df = pd.read_sql("SELECT * FROM product_inventory;", conn)

df.columns = [
    "record_id","shop_name","shop_owner","shop_address","product_name",
    "product_brand","product_mrp","product_size","quantity","selling_price",
    "manufacture_date","expiry_date","is_available","stock_status",
    "created_at","last_updated"
]

product_list = df["product_name"].str.lower().tolist()

# ------------------------------------------
# ANSWER FUNCTION
# ------------------------------------------
def answer_question(question):
    question_lower = question.lower()

    matched = [p for p in product_list if p in question_lower]
    if not matched:
        return {"response": "Product unavailable"}

    product = matched[0]
    row = df[df["product_name"].str.lower() == product]

    if row.empty:
        return {"response": "Product unavailable"}

    row = row.iloc(0)

    return {
        "shop_name": row["shop_name"],
        "address": row["shop_address"],
        "stock_status": row["stock_status"]
    }

# ------------------------------------------
# FastAPI Model
# ------------------------------------------
class Query(BaseModel):
    question: str

# ------------------------------------------
# API ROUTES
# ------------------------------------------
@app.post("/ask")
def ask_bot(query: Query):
    return answer_question(query.question)

@app.get("/")
def home():
    return {"status": "Backend running"}
