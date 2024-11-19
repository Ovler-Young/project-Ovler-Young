import streamlit as st
import pandas as pd
import numpy as np
from libs import get_collection_items_metadata

st.title("Internet Archive Collection Analyzer")

st.write(
    "This is a simple web app that analyzes the metadata of an Internet Archive collection."
)


# input the collection name
collection_id = st.text_input("Enter the collection ID:", "speedydeletionwiki")

conform_button = st.button("Conform")

if not conform_button:
    st.stop()

# display we're getting the metadata
progress_text = st.text(f"Getting metadata for collection: {collection_id}, please wait...")
progress_bar = st.progress(0)
items = get_collection_items_metadata(collection_id)
progress_text.text(f"Getting metadata for collection: {collection_id}, transforming data...")
progress_bar.progress(95)
items_pd = pd.DataFrame(items)
progress_text.text(f"Getting metadata for collection: {collection_id}, cleaning data...")
# drop columns with 80%+ nan
items_pd = items_pd.dropna(axis=1, thresh=0.8 * len(items_pd))
progress_text.text(f"Getting metadata for collection: {collection_id}, done!")

progress_bar.progress(100)

st.write("The collection contains the following items:")
st.write(items_pd)
