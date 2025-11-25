from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
import os

app = FastAPI()

# ---------- CORS FIX ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
# ------------------------------

# ---------- DATABASE ----------
db = mysql.connector.connect(
    host="junction.proxy.rlwy.net",
    user="root",
    password="6JpJaivpLbMojKEYIcdfCQVCkEpSmYVS",
    port=19240,
    database="railway"
)
cursor = db.cursor(dictionary=True)
# ------------------------------

@app.get("/")
def home():
    return {"status": "Backend running"}

@app.post("/ask")
def ask(question: dict):
    user_input = question["question"]

    query = """
    SELECT shop_name, address, stock_status
    FROM products
    WHERE product_name LIKE %s
    LIMIT 1
    """

    cursor.execute(query, (f"%{user_input}%",))
    result = cursor.fetchone()

    if result:
        return result

    return {"message": "Product not found"}

# ---------- RUN ON RAILWAY ----------
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))   # FIXED
    uvicorn.run(app, host="0.0.0.0", port=port)
