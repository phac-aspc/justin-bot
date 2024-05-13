"""BACKEND.PY
This script finds Infobase articles that are relevant to your query
Dependencies: `dotenv`, `langchain`, `langchain-community`, `langchain-voyageai`, `faiss-cpu`
"""

# Load libraries
import os
import argparse
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_voyageai import VoyageAIEmbeddings

# Load API key
load_dotenv(".env")
KEY = os.environ["VOYAGE_API_KEY"]

def load_embeddings(key: str) -> VoyageAIEmbeddings:
    """ Load the embeddings model """
    if key is None:
        raise ValueError("Please pass VoyageAI API key")

    return VoyageAIEmbeddings(voyage_api_key=key, model="voyage-large-2")

def load_db(embeddings: VoyageAIEmbeddings, 
            db_path: str) -> FAISS:
    """ Load the database from disk """
    
    # Load individual vectorstores
    base = FAISS.load_local(f"{db_path}/vectorstore_merged", embeddings, 
                            allow_dangerous_deserialization=True)
    return base

def search(query: str, db: FAISS, k: int=4) -> list:
    """ Search for the top k similar records in the database """
    return db.similarity_search(query, k=k)

def main(query: str, k: int=4):
    # Load data
    model = load_embeddings(KEY)
    db = load_db(model, "./processed")

    # Search
    results = search(query, db, k=k)
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="A topic you're interested in")
    parser.add_argument("-r", "--results", help="Number of results to return", type=int, default=4)

    args = parser.parse_args()
    main(args.query, args.results)