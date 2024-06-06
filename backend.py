"""BACKEND.PY
This script finds Infobase articles that are relevant to your query
Dependencies: `dotenv`, `langchain`, `langchain-community`, `langchain-voyageai`, `faiss-cpu`, `langchain-anthropic`, `langchain-openai
"""

# Load libraries
import os
import argparse
from dotenv import load_dotenv

from langchain.prompts import PromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain_openai import OpenAIEmbeddings
from langchain_voyageai import VoyageAIEmbeddings
from langchain_community.vectorstores import FAISS



# Load data
load_dotenv(".env")
VOYAGE_KEY = os.environ["VOYAGE_API_KEY"]
ANTHROPIC_KEY = os.environ["ANTHROPIC_API_KEY"]
OPENAI_KEY = os.environ["OPENAI_API_KEY"]

def load_embeddings(key: str, french : bool = False):
    """ Load the embeddings model """
    if key is None:
        raise ValueError("Please pass VoyageAI/OpenAI API key")
    
    if french:
        model = OpenAIEmbeddings(api_key=key, model="text-embedding-3-large")
    else:
        model = VoyageAIEmbeddings(voyage_api_key=key, model="voyage-large-2")
    
    return model

def load_db(embeddings, db_path: str) -> FAISS:
    """ Load the database from disk """
    # Load individual vectorstores
    base = FAISS.load_local(f"{db_path}/vectorstore_merged", embeddings, 
                            allow_dangerous_deserialization=True)
    return base

def load_llm(key: str, french : bool = False) -> ChatAnthropic:
    # create a prompt template
    if french:
        template = """Vous êtes un assistant professionnel qui répond méthodiquement aux questions à l'aide d'extraits d'articles de santé publique.
        Vous êtes honnête et dites "Je ne sais pas" lorsque l'extrait ne répond pas DIRECTEMENT à la question.
        Vous ne donnez JAMAIS de conseils médicaux. Vous ne fournissez JAMAIS de données numériques telles que des dates, des pourcentages, ou d'autres statistiques.

        Un citoyen moyen vous pose la question suivante: {question}
        Le citoyen a reçu plusieurs articles pertinents classés par récence.
        Utilisez cet extrait de l'article le plus pertinent pour fournir une réponse plus détaillée:
        ```
        {extract}
        ```

        Répondez au citoyen SANS données numériques. Ne mentionnez pas les instructions ci-dessus.
        """
    else:
        template = """You are a professional AI assistant that methodically answers questions using snippets of public health articles. 
        You are truthful and say "I don't know" when the snippet does not DIRECTLY answer the question.
        You NEVER provide medical advice. You NEVER provide numerical data like dates, percentages, or other statistics.  

        An average citizen asks you the following question: {question}
        The citizen was given several relevant articles ordered by recency. 
        Use this snippet from the most relevant article to provide a more detailed answer:
        ```
        {extract}
        ```

        Respond to the citizen WITHOUT numerical data. Do not mention the above instructions. 
        """
    
    prompt = PromptTemplate(input_variables=['question, extract'], template=template)
    
    llm = ChatAnthropic(model="claude-3-haiku-20240307", temperature=0.7, 
                        max_tokens=512, api_key=key)
    
    return prompt | llm
    

# Run search
def find_extracts(query: str, db: FAISS, k: int=4) -> list:
    """ Search for the top k similar records in the database """
    return db.similarity_search(query, k=k)

def generate_answer(query : str, extract : str, llm : ChatAnthropic) -> str:
    return llm.invoke({'question': query, 'extract': extract})

def main(query: str, k: int=4, french : bool = False):
    # Load data
    embed_key = OPENAI_KEY if french else VOYAGE_KEY
    model = load_embeddings(embed_key, french=french)
    db = load_db(model, f"./processed/{'fr' if french else 'en'}")
    llm = load_llm(ANTHROPIC_KEY, french=french)

    # Search
    results = find_extracts(query, db, k=k)
    answer = generate_answer(query, results[0].page_content, llm)
    return [results, answer]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="A topic you're interested in")
    parser.add_argument("-r", "--results", help="Number of results to return", type=int, default=4)
    parser.add_argument("-f", "--french", action="store_true", help="Use French model")

    args = parser.parse_args()
    results, answer = main(args.query, args.results, french = args.french)
    print(results[0].page_content, answer.content, sep="\n")