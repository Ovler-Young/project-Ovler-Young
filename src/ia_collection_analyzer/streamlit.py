import streamlit as st
import pandas as pd
import numpy as np
from ia_collection_analyzer.getmetadatas import fetch_metadata
from ia_collection_analyzer.constdatas import REQUIRED_METADATA

st.title("Internet Archive Collection Analyzer")

st.write(
    "This is a simple web app that analyzes the metadata of an Internet Archive collection."
)

# input the collection name
col1, col2 = st.columns([6, 1], vertical_alignment="bottom")
with col1:
    collection_id = st.text_input("Enter the collection ID:", "bilibili_videos")
with col2:
    conform_button = st.button("Conform")

if not conform_button:
    st.stop()

guide_text = st.markdown(f"Getting metadata for collection: **{collection_id}**:")
items = fetch_metadata(collection_id)

data_transform_text = st.text("transforming data...")
items_pd = pd.DataFrame(items)
data_transform_text.text("cleaning data...")
# drop columns with 80%+ nan
items_pd = items_pd.dropna(axis=1, thresh=0.8 * len(items_pd))
# drop columns with different types inner.
#for col in items_pd.columns:
#    items_pd[col] = items_pd[col].apply(lambda x: x if isinstance(x, type(items_pd[col][0])) else np.nan)
# drop columns with only one unique value
# items_pd = items_pd.dropna(axis=1, thresh=2)

# calculate metadata
data_transform_text.text("calculating metadata...")
data_transform_text.text("Data transformation and cleaning complete!")

st.write("The collection contains the following items:")
st.write(items_pd.head(10)) # display the first 10 rows of the dataframe

st.header("Selecting columns to analyze")
st.write("Select additional columns you want to analyze:")
seleactable_columns = [col for col in items_pd.columns if col not in REQUIRED_METADATA]

col1, col2 = st.columns([6, 1], vertical_alignment="bottom")
selected_columns = st.multiselect("Select columns:", seleactable_columns, default=[])

filtered_pd = items_pd[REQUIRED_METADATA + selected_columns]


st.write("Preview of the selected columns:")
st.write(items_pd.head(10))
