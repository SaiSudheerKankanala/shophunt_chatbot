from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
import pandas as pd

app = FastAPI()

# CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ----------------------------------------------------
# Connect to Railway MySQL
# ----------------------------------------------------
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

# ----------------------------------------------------
# Simple answer function (no ML)
# ----------------------------------------------------
def answer_question(question: str):
    q = question.lower()

    matches = [p for p in product_list if p in q]
    if not matches:
        return {"answer": "Product unavailable"}

    product = matches[0]

    row = df[df["product_name"].str.lower() == product]

    if row.empty:
        return {"answer": "Product unavailable"}

    row = row.iloc[0]

    return {
        "shop_name": row["shop_name"],
        "address": row["shop_address"],
        "stock_status": row["stock_status"]
    }

# ----------------------------------------------------
# API input model
# ----------------------------------------------------
class Query(BaseModel):
    question: str

# ----------------------------------------------------
# API endpoint
# ----------------------------------------------------
@app.post("/ask")
def ask_bot(data: Query):
    return answer_question(data.question)

@app.get("/")
def home():
    return {"status": "Backend running"}
