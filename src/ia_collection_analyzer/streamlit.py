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
st.write("Getting metadata for collection:", collection_id)

# display the ids
items = get_collection_items_metadata(collection_id)
items_pd = pd.DataFrame(items)

st.write("The collection contains the following items:")
st.write(items_pd)
