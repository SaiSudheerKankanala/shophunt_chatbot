from flask import Flask, request, jsonify
import mysql.connector
import pandas as pd

app = Flask(__name__)

# ------------------------------
# CONNECT TO RAILWAY MySQL
# ------------------------------
conn = mysql.connector.connect(
    host="ballast.proxy.rlwy.net",
    user="root",
    password="SjmGYKKMDAYKGzYQzlkISNiLSMeBvlfi",
    database="railway",
    port=22466     # <-- IMPORTANT (Railway MySQL uses a port)
)

df = pd.read_sql("SELECT * FROM product_inventory;", conn)

product_list = df['product_name'].str.lower().tolist()

# ------------------------------
# PRODUCT ANSWER FUNCTION
# ------------------------------
def answer_question(question):
    q = question.lower()

    # strict product validation
    matched = [p for p in product_list if p in q]

    if not matched:
        return {"answer": "Product unavailable"}

    product = matched[0]

    row = df[df['product_name'].str.lower() == product]

    if row.empty:
        return {"answer": "Product unavailable"}

    row = row.iloc[0]

    response = {
        "shop_name": row["shop_name"],
        "address": row["shop_address"],
        "stock_status": row["stock_status"]
    }

    return response


# ------------------------------
# API ROUTES
# ------------------------------

@app.route("/")
def home():
    return "Shop Hunt Assistant is running successfully!"

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question", "")

    answer = answer_question(question)
    return jsonify(answer)


# ------------------------------
# RUN SERVER
# ------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
