# Library endpoints
import os
import re
import sys
import time
import logging
import datetime
from threading import Thread
from dotenv import load_dotenv
from better_profanity import profanity
from flask_cors import CORS
from flask import Flask, jsonify, request
from backend import load_db, load_embeddings, load_llm, find_extracts, generate_answer



# Prep data
load_dotenv(".env")
VOYAGE_KEY = os.environ["VOYAGE_API_KEY"]
ANTHROPIC_KEY = os.environ["ANTHROPIC_API_KEY"]
OPENAI_KEY = os.environ["OPENAI_API_KEY"]

logging.basicConfig( 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]   # console logging
    #filename='chatbot_log.txt'                    # file logging
)

embed_model_en = load_embeddings(VOYAGE_KEY, french=False)
embed_model_fr = load_embeddings(OPENAI_KEY, french=True)

db_en = load_db(embed_model_en, "./processed/en/")
db_fr = load_db(embed_model_fr, "./processed/fr/")

llm_en = load_llm(ANTHROPIC_KEY, french=False)
llm_fr = load_llm(ANTHROPIC_KEY, french=True)

app = Flask(__name__)
CORS(app)
CACHE = {}



# Helper functions
def cache_cleaner():
    while True:
        current = time.time()
        keys_to_delete = [key for key in CACHE.keys() if current - CACHE[key]['time'] > 10]
        if len(keys_to_delete): 
            logging.info(f"Cleaning cache. {len(keys_to_delete)} keys deleted:.")

        for key in keys_to_delete:
            del CACHE[key]
        time.sleep(60)

def no_stats(answer : str) -> bool:
    """
    Check if the answer contains any numerical statistics.
    """
    # If a percentage is in the answer, it's likely a statistic
    if "%" in answer:
        return False
    # Don't count the -19 in COVID-19 as a number
    answer = re.sub(r"COVID-19", "", answer)
    # Don't count numerical bullets as a number
    answer = re.sub(r'^\d+\.\s*', '', answer, flags=re.MULTILINE)

    numbers = re.findall(r'\b\d+\b', answer)
    for num in numbers:
        # Years in [2000, 2030] are allowed
        if len(num) < 5 and num[:2] == "20" and int(num[2:]) <= 30:
            continue
        elif len(num) < 3: # likely an age or a month
            continue
        return False # implicit else, we found a number
    
    return True # all good



# Get articles related to query
@app.route('/api/related', methods=['GET', 'POST'])
def query():
    query = request.args.get('query')
    cache = request.args.get('cache')
    lang = request.args.get('lang', 'en')

    # No query provided
    if not query:
        logging.warning(f"Error// No query sent.")
        if lang == 'fr':
            return jsonify({'erreur': 'Aucune requête fournie'}), 400
        else:
            return jsonify({'error': 'No query provided'}), 400
    
    # Query has code characters
    if re.search(r'([;|`|{|}|#|\*|\[|\]|\/\/|\\|\|]+|\-{2,})', query):
        logging.warning(f"Error// Coding characters in query: {query}.")
        if lang == 'fr':
            return jsonify({'erreur': 'Requête invalide'}), 403
        else:
            return jsonify({'error': 'Invalid query'}), 403

    # Query too long
    if len(query) > 300:
        logging.warning(f"Error// Bypassed length restrictions query: {query}.")
        if lang == 'fr':
            return jsonify({'erreur': 'Requête trop longue'}), 413
        else:
            return jsonify({'error': 'Query too long'}), 413
    
    # Get the extracts
    try:
        results = find_extracts(query, db_en if lang == 'en' else db_fr)
        logging.info(f"Query: {query}. Extracts found: {','.join([res.metadata['title'] for res in results])}.")

        # Results sorted by relevance by default. End user can resort as desired
        unique_results = {}
        out = {"links": []}

        for res in results:
            # Don't display the same article many times
            if unique_results.get(res.metadata['title']):
                continue
            unique_results[res.metadata['title']] = True

            out["links"].append({
                "title": res.metadata['title'],
                "url": res.metadata['link'],
                "description": res.metadata['description'],
                "date": res.metadata['date']
            })

        # If query is cached, create a cache key
        if cache == "TRUE":
            # datetime has microsecond precision compared to time
            cache_key = str(hash(query + str(datetime.datetime.now())))
            # Save only the most related extract
            CACHE[cache_key] = {"query": query, "extract": results[0], "time": time.time()}
            out["id"] = cache_key
        
        return jsonify(out)
    except Exception as e:
        logging.warning(f"Error// Query: {query}. Error: {e}.")
        if lang == 'fr':
            return jsonify({'erreur': 'Erreur interne du serveur'}), 500
        else:
            return jsonify({'error': 'Internal server error'}), 500



# Generate answer to question
@app.route('/api/answer', methods=['GET', 'POST'])
def answer():
    id = request.args.get('id')
    lang = request.args.get('lang', 'en')

    if not CACHE.get(id):
        logging.warning(f"Error// Invalid id: {id}.")
        if lang == 'fr':
            return jsonify({'erreur': 'Identifiant invalide'}), 400
        else:
            return jsonify({'error': 'Invalid id'}), 400
    
    query = CACHE[id]['query']
    extract = CACHE[id]['extract']
    try:
        answer = generate_answer(query, extract.page_content, llm_en if lang == 'en' else llm_fr)

        # Check if answer is valid
        if (len(answer.content) > 100 and no_stats(answer.content) 
            and not profanity.contains_profanity(answer.content)):
            logging.info(f"Query: {query}. Extract: {extract.page_content}. Answer: {answer.content}.")
            return jsonify({"answer": answer.content})
        else:
            logging.warning(f"Error// Invalid answer. Query: {query}. Extract: {extract.page_content}. Answer: {answer.content}.")
            
            if lang == 'fr':
                return jsonify({"answer": "Désolé, je n'ai pas de réponse à cela."}), 500
            else: 
                return jsonify({"answer": "Sorry, I don't have an answer for that."}), 500
    except Exception as e:
        logging.warning(f"Error// Query: {query}. Extract: {extract.page_content}. Error: {e}.")
        if lang == 'fr':
            return jsonify({'erreur': 'Erreur interne du serveur'}), 500
        else:
            return jsonify({'error': 'Internal server error'}), 500
    finally:
        CACHE.pop(id)

if __name__ == '__main__':
    cleaner_thread = Thread(target=cache_cleaner, daemon=True)
    cleaner_thread.start()

    app.run(host="0.0.0.0", port=5555)