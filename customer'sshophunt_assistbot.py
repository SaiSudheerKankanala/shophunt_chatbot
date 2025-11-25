# -*- coding: utf-8 -*-
# Customer ShopHunt AssistBot – Fixed Version

!pip install langchain-text-splitters
!pip install reportlab
!pip install fpdf
!pip install pypdf
!pip install langchain-community
!pip install mysql-connector-python

import os
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"

import mysql.connector
import pandas as pd
from fpdf import FPDF
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from transformers import pipeline


# ------------------------------------------------------------
# 1. FIXED MYSQL CONNECTION
# ------------------------------------------------------------
conn = mysql.connector.connect(
    host='ballast.proxy.rlwy.net',
    user='root',
    password='SjmGYKKMDAYKGzYQzlkISNiLSMeBvlfi',
    database='railway',
    port=3306
)

df = pd.read_sql("SELECT * FROM product_inventory;", conn)

# Create product list (lowercase)
product_list = df['product_name'].str.lower().tolist()


# ------------------------------------------------------------
# 2. CREATE PDF FROM DATABASE
# ------------------------------------------------------------
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


# ------------------------------------------------------------
# 3. LOAD PDF + CLEAN TEXT
# ------------------------------------------------------------
loader = PyPDFLoader(pdf_path)
documents = loader.load()

for doc in documents:
    doc.page_content = " ".join(doc.page_content.split())


# ------------------------------------------------------------
# 4. SPLIT INTO CHUNKS
# ------------------------------------------------------------
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=40
)
chunks = text_splitter.split_documents(documents)


# ------------------------------------------------------------
# 5. EMBEDDINGS + VECTOR DB
# ------------------------------------------------------------
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_db = FAISS.from_documents(chunks, embeddings)


# ------------------------------------------------------------
# 6. QA MODEL
# ------------------------------------------------------------
qa_model = pipeline("text2text-generation", model="google/flan-t5-base")


# ------------------------------------------------------------
# 7. IMPROVED ANSWER FUNCTION
# ------------------------------------------------------------
def answer_question(vector_db, question):
    q = question.lower()

    # match words inside product name
    best_match = None
    for product in product_list:
        if all(word in q for word in product.split()):
            best_match = product
            break

    if not best_match:
        return "Product unavailable"

    product_row = df[df['product_name'].str.lower() == best_match]

    if product_row.empty:
        return "Product unavailable"

    row = product_row.iloc[0]

    return f"""
Shop Name   : {row['shop_name']}
Address     : {row['shop_address']}
Stock Status: {row['stock_status']}
"""


# ------------------------------------------------------------
# 8. USER QUERY
# ------------------------------------------------------------
question = input("Ask your question: ")
print("\nAssistant:", answer)
