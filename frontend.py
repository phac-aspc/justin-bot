# Library imports
import os
import re
import logging
import streamlit as st 
from dotenv import load_dotenv
from better_profanity import profanity
from backend import load_db, load_embeddings, load_llm, find_extracts, generate_answer



# Prep data
load_dotenv(".env")
EMBED_KEY = os.environ["VOYAGE_API_KEY"]
ANTHROPIC_KEY = os.environ["ANTHROPIC_API_KEY"]

logging.basicConfig(
    filename='chatbot_log.txt', 
    level=logging.WARN, 
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

embed_model = load_embeddings(EMBED_KEY)
db = load_db(embed_model, "./processed")
llm = load_llm(ANTHROPIC_KEY)



# Setup page
st.title("Infobase QA Chatbot")
st.write("Ask a public health question to be directed to a relevant article " + 
         "on the [Infobase website](https://health-infobase.canada.ca).")

with st.sidebar:
    with st.form(key='user_input'):
        query = st.text_area("Your question", max_chars=500,
                              placeholder="What are the largest challenges to teenagers' mental health?")
        submit = st.form_submit_button("Search")



# Respond to input
if submit and query:
    results = find_extracts(query, db)

    if not len(results):
        st.write("No relevant articles found. Please try visiting the [Infobase website](https://health-infobase.canada.ca) to find any content we missed.")
    else:
        # Show summary results
        st.write("## Relevant article(s):")
        unique_results = {}
        i = 1

        for res in results:
            # Don't display the same article many times
            if unique_results.get(res.metadata['title']):
                continue
            unique_results[res.metadata['title']] = True

            # Article descriptions
            st.write(f"{i}. [{res.metadata['title']}]({res.metadata['link']})" + 
                    f": {res.metadata['description']}")
            st.write("")
            i += 1

        # Answer the question with the most related article
        answer = generate_answer(query, results[0].page_content, llm)

        # Check for profanity and hallucinated numbers
        if (len(answer.content) > 100 and not re.search(r"\b[0-9]+\b", answer.content) 
            and not profanity.contains_profanity(answer.content)):            
            st.write("## Computer-generated summary:")
            st.write("A computer attempted to answer your question with the most relevant article found. **This content is not human-verified** so be careful and double-check specific claims, especially if there are numerical statistics or personal advice:")
            st.write("> " + answer.content.replace("\n", "\n> "))
        else:
            logging.warning(f"Question: {query}")
            logging.warning(f"Extract: {results[0].page_content}")
            logging.warning(f"Answer: {answer.content}")

    
# Error message
elif submit and not query:
    st.write("Please enter a question in the text input on the left.")