from fastapi import FastAPI, BackgroundTasks
import os
import chromadb
from PyPDF2 import PdfReader
import requests
from github import Github
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("GITHUB_REPO")
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")  # fallback for local dev
PDF_FOLDER = "pdfs"

app = FastAPI()

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = chroma_client.get_or_create_collection(name="documents")

# GitHub API setup
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

def fetch_pdfs_from_github():
    contents = repo.get_contents(PDF_FOLDER)
    for content_file in contents:
        if content_file.name.endswith(".pdf"):
            file_path = os.path.join("./pdfs", content_file.name)
            with open(file_path, "wb") as f:
                f.write(requests.get(content_file.download_url).content)
            process_pdf(file_path)

def process_pdf(pdf_path):
    with open(pdf_path, "rb") as f:
        reader = PdfReader(f)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        collection.add(
            documents=[text],
            metadatas=[{"source": pdf_path}],
            ids=[pdf_path]
        )

@app.post("/update")
def update_database(background_tasks: BackgroundTasks):
    background_tasks.add_task(fetch_pdfs_from_github)
    return {"message": "Updating database in the background..."}
