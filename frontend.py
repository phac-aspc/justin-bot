import os
import streamlit as st 
from dotenv import load_dotenv
from backend import load_db, load_embeddings, search

# Prep data
load_dotenv(".env")
EMBED_KEY = os.environ["VOYAGE_API_KEY"]

embed_model = load_embeddings(EMBED_KEY)
db = load_db(embed_model, "./processed")

# Context
st.title("Infobase QA Chatbot")
st.write("Ask a public health question to be directed to a relevant article " + 
         "on the [Infobase website](https://health-infobase.canada.ca).")

# Search inputs
with st.sidebar:
    with st.form(key='user_input'):
        query = st.text_area("Your question", max_chars=500,
                              placeholder="What are the largest challenges to teenagers' mental health?")
        submit = st.form_submit_button("Search")

if submit and query:
    results = search(query, db)

    # Show summary results
    st.write("Here are some relevant article(s):")
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

    
# Error message
elif submit and not query:
    st.write("Please enter a question in the text input on the left.")