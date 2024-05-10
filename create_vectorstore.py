"""CREATE_VECTORSTORE.PY
This script creates a Faiss vectorstore from the page descriptions.
Dependencies: `dotenv`, 'faiss-cpu', `langchain`, `tqdm`
"""

# Library imports
import re
import os
import time
import bs4
import json
import requests

from tqdm import tqdm
from dotenv import load_dotenv

from langchain.vectorstores.faiss import FAISS
from langchain.docstore.document import Document
from langchain.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter


# Load API key
load_dotenv(".env")
KEY = os.environ["ANTHROPIC_API_KEY"]

def scrape_data() -> list:
    """ Returns list of website snippets """

    # Get article list
    res = requests.get("https://health-infobase.canada.ca/src/json/articles.json")
    articles = res.json()

    # Get main section's inner text
    for article in articles:
        print(".")
        res = requests.get(article['link'])
        soup = bs4.BeautifulSoup(res.text, "html.parser")
        article["content"] = soup.find("main").text

        # clean
        article["content"] = article["content"].strip()
        article["content"] = re.sub(r'\s+', ' ', article["content"])

        time.sleep(0.5)
    
    # Save to JSON
    with open("unprocessed/articles.json", "w") as f:
        json.dump(articles, f, indent=4)

def format_documents(path: str) -> list:
    """ Returns list of processed LangChain Documents """

    # Load documents
    print("Loading documents...")
    articles = json.load(open(path, "r"))
    documents = []
    none_count = 0

    for b in bios: 
        if b["bio"] is not None:
            documents.append(Document(page_content=b["bio"], metadata={
                "name": b["name"],
                "position": b["position"],
                "email": b["email"],
                "expertise": b["expertise"],
                "profile": b["profile"],
            }))
        else:
            none_count += 1
    
    print(f"Loaded {len(documents)} documents. {none_count} documents skipped since bio was None")

    print(f"Splitting {len(documents)} documents...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    fragments = splitter.split_documents(documents)

    return fragments

def get_vectorstore(fragments: list, model: HuggingFaceInferenceAPIEmbeddings, 
                    save_path: str) -> FAISS:
    """ Embeds documents and returns vectorstore """
    
    # Create vectorstore (400 docs at a time, else HuggingFace API blocks)
    print(f"Creating vectorstore with {len(fragments)} documents...")
    dbs = []
    for i in tqdm(range(0, len(fragments), 400)):
        db = FAISS.from_documents(fragments[i : i+400], model)
        db.save_local(f"{save_path}_{i}")
        dbs.append(db)
        time.sleep(5)

    # Merge partial vectorstores and save final copy
    for db in tqdm(dbs[1:]):
        dbs[0].merge_from(db)
    db.save_local(f"{save_path}_merged")

def main():
    # Load embeddings model
    model = HuggingFaceInferenceAPIEmbeddings(
        api_key=KEY, model_name="sentence-transformers/all-MiniLM-l6-v2"
    )

    # Get vectorstore
    fragments = get_data("data_new/json/bios.json")
    get_vectorstore(fragments, model, "data_new/faiss/bios_faiss")

if __name__ == "__main__":
    #main()
    #scrape_data()