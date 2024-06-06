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
import chardet
import requests
import argparse

from tqdm import tqdm
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from langchain_voyageai import VoyageAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter


# Load API key
load_dotenv(".env")
VOYAGE_KEY = os.environ["VOYAGE_API_KEY"]
OPENAI_KEY = os.environ["OPENAI_API_KEY"]

def scrape_data(french : bool = False) -> list:
    """ Returns list of website snippets """

    # Get article list
    url = f"https://health-infobase.canada.ca/src/json/articles{'_fr' if french else ''}.json"
    res = requests.get(url)
    articles = res.json()

    print(f"Scraping {len(articles)} articles from website...")
    # Get main section's inner text
    for i in tqdm(range(len(articles))):
        article = articles[i]
        res = requests.get(article['link'])

        encoding = chardet.detect(res.content)['encoding']
        decoded_content = res.content.decode(encoding)

        soup = bs4.BeautifulSoup(decoded_content, "html.parser")
        article["content"] = soup.find("main").text

        # clean
        article["content"] = article["content"].strip()
        article["content"] = re.sub(r'\s+', ' ', article["content"])

        time.sleep(0.5)
    
    # Save to JSON
    with open(f"unprocessed/articles{'_fr' if french else ''}.json", "w") as f:
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

def main(french : bool = False, scrape : bool = False):
    batch_size = 20
    chunk_size = 5000

    # Scrape data
    if scrape:
        scrape_data(french)
        return

    # Load embeddings model
    if french:
        model = OpenAIEmbeddings(api_key=OPENAI_KEY, model="text-embedding-3-large")
    else:
        model = VoyageAIEmbeddings(voyage_api_key=VOYAGE_KEY, model="voyage-large-2", 
                               batch_size=batch_size)

    # Get vectorstore
    path = f"./unprocessed/articles{'_fr' if french else ''}.json"
    fragments = format_documents(path, chunk_size)
    get_vectorstore(fragments, model, f"./processed/{'fr' if french else 'en'}/", batch_size)

if __name__ == "__main__":
    # Setup argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-f", "--french", action="store_true", help="Create french vectorstore")
    parser.add_argument("-s", "--scrape", action="store_true", help="Scrape data")

    args = parser.parse_args()
    main(args.french, args.scrape)