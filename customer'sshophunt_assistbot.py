# main.py
import os
import mysql.connector
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from fpdf import FPDF

app = FastAPI()

# ------------------------------------------
# 1. CONNECT TO MYSQL (Railway)
# ------------------------------------------
conn = mysql.connector.connect(
    host="ballast.proxy.rlwy.net",
    user="root",
    password="SjmGYKKMDAYKGzYQzlkISNiLSMeBvlfi",
    database="railway",
    port=YOUR_PORT
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
# CREATE PDF
# ------------------------------------------
def create_pdf_from_df(df, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(0, 10, "Product Inventory Report", ln=True, align='C')
    pdf.ln(5)

    for index, row in df.iterrows():
        text = (
            f"Record ID: {row['record_id']}\n"
            f"Shop Name: {row['shop_name']}\n"
            f"Owner: {row['shop_owner']}\n"
            f"Address: {row['shop_address']}\n"
            f"Product Name: {row['product_name']}\n"
            f"Brand: {row['product_brand']}\n"
            f"MRP: {row['product_mrp']}\n"
            f"Size: {row['product_size']}\n"
            f"Quantity: {row['quantity']}\n"
            f"Selling Price: {row['selling_price']}\n"
            f"Manufacture Date: {row['manufacture_date']}\n"
            f"Expiry Date: {row['expiry_date']}\n"
            f"Available: {row['is_available']}\n"
            f"Stock Status: {row['stock_status']}\n"
            f"Created: {row['created_at']}\n"
            f"Updated: {row['last_updated']}\n"
            "---------------------------------------------"
        )
        pdf.multi_cell(0, 8, text)
        pdf.ln(2)

    pdf.output(output_path, dest='F')


pdf_path = "product_report.pdf"
create_pdf_from_df(df, pdf_path)

# ------------------------------------------
# LOAD + SPLIT PDF
# ------------------------------------------
loader = PyPDFLoader(pdf_path)
documents = loader.load()

for doc in documents:
    doc.page_content = doc.page_content.replace("\n", " ").strip()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=40)
chunks = text_splitter.split_documents(documents)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_db = FAISS.from_documents(chunks, embeddings)


# ------------------------------------------
# ANSWER FUNCTION
# ------------------------------------------
def answer_question(question):
    question_lower = question.lower()

    matched = [p for p in product_list if p in question_lower]
    if not matched:
        return "Product unavailable"

    product = matched[0]
    row = df[df["product_name"].str.lower() == product]

    if row.empty:
        return "Product unavailable"

    row = row.iloc[0]
    return {
        "shop_name": row["shop_name"],
        "address": row["shop_address"],
        "stock_status": row["stock_status"]
    }


# ------------------------------------------
# FastAPI Request Model
# ------------------------------------------
class Query(BaseModel):
    question: str


# ------------------------------------------
# API ROUTE
# ------------------------------------------
@app.post("/ask")
def ask_bot(query: Query):
    return answer_question(query.question)


@app.get("/")
def home():
    return {"status": "Backend Running on Railway!"}
