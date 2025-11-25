from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
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
    try:
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
    except Exception as e:
        print(f"Database error: {e}")
        return None

@app.post("/ask")
def ask(query: Query):
    try:
        df = fetch_data()
        if df is None:
            return {"response": "Database connection error"}
        
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
    except Exception as e:
        print(f"Error in /ask: {e}")
        return {"response": f"Error processing request: {str(e)}"}

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ShopHunt Assist Bot</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            input[type="text"] {
                width: 70%;
                padding: 10px;
                margin-right: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            button {
                padding: 10px 20px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
            button:hover {
                background-color: #0056b3;
            }
            #response {
                margin-top: 20px;
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 5px;
                white-space: pre-wrap;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>ShopHunt Assist Bot</h2>
            <p>Ask about product availability:</p>
            
            <input type="text" id="question" placeholder="Enter product name...">
            <button onclick="askBot()">Ask</button>

            <div id="response"></div>
        </div>

        <script>
        async function askBot() {
            const question = document.getElementById('question').value;
            const responseElement = document.getElementById('response');
            
            if (!question.trim()) {
                responseElement.innerText = 'Please enter a product name';
                return;
            }

            responseElement.innerText = 'Searching...';

            try {
                const res = await fetch("/ask", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ question })
                });

                const data = await res.json();
                
                if (data.response === "Product unavailable") {
                    responseElement.innerText = "Sorry, this product is currently unavailable.";
                } else if (data.response && data.response.includes("Error")) {
                    responseElement.innerText = data.response;
                } else {
                    responseElement.innerHTML = `
                        <strong>Shop Name:</strong> ${data.shop_name}<br>
                        <strong>Address:</strong> ${data.address}<br>
                        <strong>Stock Status:</strong> ${data.stock_status}
                    `;
                }
            } catch (error) {
                responseElement.innerText = 'Error connecting to server. Please try again.';
                console.error('Error:', error);
            }
        }

        // Allow pressing Enter to submit
        document.getElementById('question').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                askBot();
            }
        });
        </script>
    </body>
    </html>
    """

@app.get("/health")
def health_check():
    return {"status": "Backend running"}
