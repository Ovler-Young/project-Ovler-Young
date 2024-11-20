import streamlit as st
import pandas as pd
import numpy as np
from ia_collection_analyzer.getmetadatas import fetch_metadata
from ia_collection_analyzer.constdatas import REQUIRED_METADATA

st.title("Internet Archive Collection Analyzer")

st.write(
    "This is a simple web app that analyzes the metadata of an Internet Archive collection."
)

st.markdown(
    "Here are some example / suggested collections to analyze:"
    "\n - [`wikiteam`](https://archive.org/details/wikiteam): `~421,000` items. A Large collection of archived wikis. (Not suggested currently, as this have 14 years of history, some data may cause bugs of this program.)"
    "\n - [`bilibili_videos`](https://archive.org/details/bilibili_videos): `~48,000` items. A collection of archived videos from an Chinese Youtube-like website [Bilibili](https://www.bilibili.com/). Archive tool can be found at [GitHub](https://github.com/saveweb/biliarchiver)."
    "\n - [`bilibili_videos_sub_1`](https://archive.org/details/bilibili_videos_sub_1): `~20,000` items. A subset of the `bilibili_videos` collection."
)

# cache system
if "collection_id" not in st.session_state:
    st.session_state.collection_id = "bilibili_videos"
if "got_metadata" not in st.session_state:
    st.session_state.got_metadata = False
if "items_pd" not in st.session_state:
    st.session_state.items_pd = None

# input the collection name
col1, col2 = st.columns([6, 1], vertical_alignment="bottom")
with col1:
    collection_id = st.text_input("Enter the collection ID:", "bilibili_videos")
with col2:
    conform_button = st.button("Conform")

if not conform_button and not st.session_state.got_metadata:
    st.stop()

# Check if we need to fetch new data
if not st.session_state.got_metadata or collection_id != st.session_state.collection_id:
    guide_text = st.markdown(
        f"Getting fresh metadata for collection: **{collection_id}**"
    )
    items = fetch_metadata(collection_id)
    items_pd = pd.DataFrame(items)

    # Update cache
    st.session_state.collection_id = collection_id
    st.session_state.items_pd = items_pd
    st.session_state.got_metadata = True
    st.session_state.selected_columns = []
else:
    guide_text = st.markdown(
        f"Using cached metadata for collection: **{collection_id}**"
    )
    items_pd = st.session_state.items_pd

data_transform_text = st.text("cleaning data...")
# drop columns with 80%+ nan
items_pd = items_pd.dropna(axis=1, thresh=0.8 * len(items_pd))
# drop columns with different types inner.
# for col in items_pd.columns:
#    items_pd[col] = items_pd[col].apply(lambda x: x if isinstance(x, type(items_pd[col][0])) else np.nan)
# drop columns with only one unique value
# items_pd = items_pd.dropna(axis=1, thresh=2)

# calculate metadata
data_transform_text.text("calculating metadata...")
data_transform_text.text("Data transformation and cleaning complete!")

st.write("The collection contains the following items:")
st.write(items_pd.head(10))  # display the first 10 rows of the dataframe

st.header("Selecting columns to analyze")
st.write("Select additional columns you want to analyze:")
seleactable_columns = [col for col in items_pd.columns if col not in REQUIRED_METADATA]

col1, col2 = st.columns([6, 1], vertical_alignment="bottom")
selected_columns = st.multiselect("Select columns:", seleactable_columns, default=[])

filtered_pd = items_pd[REQUIRED_METADATA + selected_columns]

st.write("Preview of the selected columns:")
st.write(items_pd.head(10))
