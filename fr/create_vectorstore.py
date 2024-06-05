"""CREATE_VECTORSTORE.PY
This script creates a Faiss vectorstore from the page descriptions.
Dependencies: `dotenv`, `tqdm`, `bs4`, `requests`, `langchain-community`, `langchain-voyageai`, 'faiss-cpu', `langchain`,
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

from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain_voyageai import VoyageAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter


# Load API key
load_dotenv(".env")
KEY = os.environ["VOYAGE_API_KEY"]

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

def format_documents(path: str, chunk_size : int) -> list:
    """ Returns list of processed LangChain Documents """

    # Load documents
    articles = json.load(open(path, "r"))
    documents = []

    for article in articles: 
        content = article.pop("content")
        documents.append(Document(page_content=content, metadata=article))
    
    print(f"Loaded {len(documents)} documents.")

    print(f"Splitting {len(documents)} documents...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=0)
    fragments = splitter.split_documents(documents)

    return fragments

def get_vectorstore(fragments: list, model: VoyageAIEmbeddings, 
                    save_path: str, batch_size : int) -> FAISS:
    """ Embeds documents and returns vectorstore """
    
    # Create vectorstore (batch_size docs at a time to respect rate limits)
    print(f"Creating vectorstore with {len(fragments)} documents...")
    
    dbs = []
    for i in tqdm(range(0, len(fragments), batch_size)):
        db = FAISS.from_documents(fragments[i : i+batch_size], model)
        db.save_local(f"{save_path}/vectorstore_{i}")
        dbs.append(db)
        time.sleep(5)

    # Merge partial vectorstores and save final copy
    for db in tqdm(dbs[1:]):
        dbs[0].merge_from(db)
    dbs[0].save_local(f"{save_path}/vectorstore_merged")

def main():
    batch_size = 20
    chunk_size = 5000

    # Load embeddings model
    model = VoyageAIEmbeddings(voyage_api_key=KEY, model="voyage-large-2", 
                               batch_size=batch_size)

    # Get vectorstore
    fragments = format_documents("./unprocessed/articles.json", chunk_size)
    get_vectorstore(fragments, model, "./processed/", batch_size)

if __name__ == "__main__":
    main()