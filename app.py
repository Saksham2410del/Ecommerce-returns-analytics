# Small web page for the "Ask your data" assistant.
#
# Usage: streamlit run app.py

import os
import streamlit as st
from ask_data import ask, DB_PATH
import etl_pipeline

st.title("Ask the Returns Data")
st.write("Ask a question in plain English. The assistant writes the SQL, runs it on "
         "the database and shows you both the answer and the query it used.")

# On a fresh deploy the database doesn't exist yet, so build it once from the raw files
if not os.path.exists(DB_PATH):
    with st.spinner("Building the database from the raw data..."):
        etl_pipeline.main()

st.caption("Try: Which category has the highest return rate?  |  "
           "How much was refunded for Apparel?  |  Which city has the most customers?")

question = st.text_input("Your question")

if st.button("Ask") and question:
    try:
        sql, result = ask(question)
        st.subheader("Answer")
        st.dataframe(result, hide_index=True)
        st.subheader("SQL used")
        st.code(sql, language="sql")
    except Exception as e:
        st.error(f"Couldn't answer that: {e}")
