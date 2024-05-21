# Library imports
import os
import re
import sys
import logging
import datetime
import streamlit as st 
from dotenv import load_dotenv
from better_profanity import profanity
from backend import load_db, load_embeddings, load_llm, find_extracts, generate_answer



# Prep data
load_dotenv(".env")
EMBED_KEY = os.environ["VOYAGE_API_KEY"]
ANTHROPIC_KEY = os.environ["ANTHROPIC_API_KEY"]

logging.basicConfig( 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)] # switch to below for file logging
    # filename='chatbot_log.txt'
)

embed_model = load_embeddings(EMBED_KEY)
db = load_db(embed_model, "./processed")
llm = load_llm(ANTHROPIC_KEY)



# Helper function
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
        # Years are allowed
        if len(num) < 5 and num[:2] == "20" and int(num[2:]) <= 30:
            continue
        elif len(num) < 3: # likely an age or a month
            continue
        return False # implicit else, we found a number
    
    return True # all good



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
            
            # Format date
            date_obj = datetime.datetime.strptime(res.metadata['date'], "%Y-%m-%d")
            formatted_date = date_obj.strftime("%B %d, %Y")

            # Article descriptions
            st.write(f"{i}. [{res.metadata['title']}]({res.metadata['link']})" + 
                    f" ({formatted_date}): {res.metadata['description']}")
            st.write("")
            i += 1

        # Answer the question with the most related article
        answer = generate_answer(query, results[0].page_content, llm)

        # Check for profanity and hallucinated numbers
        if (len(answer.content) > 100 and no_stats(answer.content) 
            and not profanity.contains_profanity(answer.content)):            
            st.write("## Computer-generated summary:")
            st.write("A computer attempted to answer your question with the most relevant article found. **This content is not human-verified** so be careful and double-check specific claims, especially if there are numerical statistics or personal advice:")
            st.write("> " + answer.content.replace("\n", "\n> "))

            logging.info(f"Question: {query}\n")
            logging.info(f"Extract: {results[0].page_content}\n")
            logging.info(f"Answer: {answer.content}\n")
        else:
            logging.warning(f"Question: {query}\n")
            logging.warning(f"Extract: {results[0].page_content}\n")
            logging.warning(f"Answer: {answer.content}\n")

    
# Error message
elif submit and not query:
    st.write("Please enter a question in the text input on the left.")