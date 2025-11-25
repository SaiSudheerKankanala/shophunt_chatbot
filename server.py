from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from sqlalchemy import create_engine
import os

app = FastAPI()

# --------------- DB CONNECTION (SQLAlchemy) -----------------

# Railway MySQL connection
DB_HOST = "ballast.proxy.rlwy.net"
DB_USER = "root"
DB_PASS = "SjmGYKKMDAYKGzYQzlkISNiLSMeBvlfi"
DB_NAME = "railway"
DB_PORT = 19240

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)

# Load data safely
df = pd.read_sql("SELECT * FROM product_inventory;", engine)
product_list = df["product_name"].str.lower().tolist()

# --------------- MODELS -----------------

class Question(BaseModel):
    question: str

# --------------- LOGIC -----------------

def find_product(query):
    q = query.lower()

    for product in product_list:
        if product in q:
            row = df[df["product_name"].str.lower() == product].iloc[0]
            return {
                "product": product,
                "shop_name": row["shop_name"],
                "address": row["shop_address"],
                "stock_status": row["stock_status"],
            }

    return {"answer": "Product unavailable"}

# --------------- ROUTE -----------------

@app.post("/ask")
def ask_api(data: Question):
    return find_product(data.question)
