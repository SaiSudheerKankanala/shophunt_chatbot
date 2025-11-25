from fastapi import FastAPI
from pydantic import BaseModel
import mysql.connector
import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from fpdf import FPDF
from langchain_community.document_loaders import PyPDFLoader
from transformers import pipeline

app = FastAPI()

# ------------------ DATABASE ------------------

conn = mysql.connector.connect(
    host='ballast.proxy.rlwy.net',
    user='root',
    password='SjmGYKKMDAYKGzYQzlkISNiLSMeBvlfi',
    database='railway',
    port=19240
)

df = pd.read_sql("SELECT * FROM product_inventory;", conn)
product_list = df['product_name'].str.lower().tolist()

# ------------------ PDF ------------------
pdf_path = "product_report.pdf"

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

    pdf.output(output_path)

create_pdf_from_df(df, pdf_path)

# ------------------ PDF LOAD + VECTOR DB ------------------

loader = PyPDFLoader(pdf_path)
documents = loader.load()
for d in documents:
    d.page_content = " ".join(d.page_content.split())

splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=40)
chunks = splitter.split_documents(documents)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_db = FAISS.from_documents(chunks, embeddings)

qa_model = pipeline("text2text-generation", model="google/flan-t5-base")

# ------------------ API REQUEST MODEL ------------------

class Question(BaseModel):
    question: str

# ------------------ FUNCTION ------------------

def answer_question(question):
    q = question.lower()

    best_match = None
    for product in product_list:
        if all(word in q for word in product.split()):
            best_match = product
            break

    if not best_match:
        return {"answer": "Product unavailable"}

    row = df[df['product_name'].str.lower() == best_match].iloc[0]

    return {
        "shop_name": row['shop_name'],
        "address": row['shop_address'],
        "stock_status": row['stock_status']
    }

# ------------------ API ROUTE ------------------

@app.post("/ask")
def ask_api(data: Question):
    return answer_question(data.question)
