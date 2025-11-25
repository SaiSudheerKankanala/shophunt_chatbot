from fastapi import FastAPI
from pydantic import BaseModel
import mysql.connector
import pandas as pd

app = FastAPI()

# --------------- DB CONNECTION -----------------

conn = mysql.connector.connect(
    host='ballast.proxy.rlwy.net',
    user='root',
    password='SjmGYKKMDAYKGzYQzlkISNiLSMeBvlfi',
    database='railway',
    port=19240
)

df = pd.read_sql("SELECT * FROM product_inventory;", conn)
product_list = df["product_name"].str.lower().tolist()

# --------------- MODELS -----------------

class Question(BaseModel):
    question: str

# --------------- LOGIC -----------------

def find_product(query):
    q = query.lower()

    # match product by substring
    for product in product_list:
        if product in q:
            row = df[df["product_name"].str.lower() == product].iloc[0]
            return {
                "product": product,
                "shop_name": row["shop_name"],
                "address": row["shop_address"],
                "stock_status": row["stock_status"]
            }

    return {"answer": "Product unavailable"}

# --------------- ROUTE -----------------

@app.post("/ask")
def ask_api(data: Question):
    return find_product(data.question)
