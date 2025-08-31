# src/data_processor.py

import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
import google.generativeai as genai
from dotenv import load_dotenv

# Tải API key từ file .env
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Định nghĩa các đường dẫn
DATA_PATH = "data/"
VECTOR_STORE_PATH = "vector_store/"

def create_vector_store():
    """
    Load tài liệu, chia nhỏ, vector hóa và lưu vào ChromaDB.
    """
    # Kiểm tra xem vector store đã tồn tại chưa
    if os.path.exists(VECTOR_STORE_PATH):
        print(f"Vector store already exists at {VECTOR_STORE_PATH}. Skipping creation.")
        return

    print("Loading documents...")
    # Dùng DirectoryLoader để tải tất cả các file .txt
    loader = DirectoryLoader(DATA_PATH, glob=["**/*.txt", "**/*.md"], loader_cls=TextLoader, loader_kwargs={'encoding': 'utf8'})
    documents = loader.load()

    if not documents:
        print("No documents found. Please add your .txt files to the 'data' directory.")
        return

    print(f"Loaded {len(documents)} document(s).")

    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100,separators=["\n---\n", "\n\n", "\n", " "])
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")

    print("Creating embeddings and storing in ChromaDB...")
    # Khởi tạo model embedding
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # Tạo và lưu trữ vector store
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTOR_STORE_PATH
    )

    print(f"Vector store created successfully at {VECTOR_STORE_PATH}")

if __name__ == '__main__':
    create_vector_store()
