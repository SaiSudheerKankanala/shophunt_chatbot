from fastapi import FastAPI
from pydantic import BaseModel
import mysql.connector

app = FastAPI()

# --- DATABASE CONNECTION ---
conn = mysql.connector.connect(
    host="ballast.proxy.rlwy.net",
    user="root",
    password="SjmGYKKMDAYKGzYQzlkISNiLSMeBvlfi",
    database="railway",
    port=19240
)

cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT * FROM product_inventory;")
rows = cursor.fetchall()

product_list = [row["product_name"].lower() for row in rows]


# --- REQUEST MODEL ---
class Question(BaseModel):
    question: str


# --- FIND PRODUCT FUNCTION ---
def find_product(query):
    q = query.lower()

    for row in rows:
        product = row["product_name"].lower()
        if product in q:
            return {
                "product": product,
                "shop_name": row["shop_name"],
                "address": row["shop_address"],
                "stock_status": row["stock_status"]
            }

    return {"answer": "Product unavailable"}


# --- API ROUTE ---
@app.post("/ask")
def ask_api(data: Question):
    return find_product(data.question)


# --- ROOT ROUTE ---
@app.get("/")
def root():
    return {"message": "ShopHunt AssistBot Backend Running"}
