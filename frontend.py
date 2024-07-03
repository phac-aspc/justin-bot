# Library imports
import os
import re
import sys
import logging
import datetime
import streamlit as st 
from dotenv import load_dotenv
from backend import load_llm, generate_answer



# Prep data
load_dotenv(".env")
ANTHROPIC_KEY = os.environ["ANTHROPIC_API_KEY"]

logging.basicConfig( 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)] # switch to below for file logging
    # filename='chatbot_log.txt'
)

llm = load_llm(ANTHROPIC_KEY)



# Setup page
st.title("Justin Bot")
st.write("A chatbot to answer your questions about Justin's modular code.")

with st.sidebar:
    with st.form(key='user_input'):
        query = st.text_area("Your question", max_chars=1000,
                              placeholder="How do I change the tick size in a horizontal bar graph's categorical axis?")
        graph = st.selectbox("The graph you're using", ['bar', 'line', 'map', 'pie'])
        submit = st.form_submit_button("Search")



# Respond to input
if submit and query:
    # Answer the question with the most related article
    answer = generate_answer(query, graph, llm)

    st.write("## Justin's answer:")
    st.write("> " + answer.content.replace("\n", "\n> "))

    logging.info(f"Question: {query}\n")
    logging.info(f"Answer: {answer.content}\n")

# Error message
elif submit and not query:
    st.write("Please enter a question in the text input on the left.")