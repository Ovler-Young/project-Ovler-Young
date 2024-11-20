import streamlit as st
import pandas as pd
import numpy as np
from ia_collection_analyzer.iahelper import get_collection_items_metadata, calculate_metadata
from ia_collection_analyzer.constdatas import REQUIRED_METADATA
import time

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
progress_text = st.markdown("Getting count and estimating time...")
progress_bar = st.progress(0)
current_progress = 0
start_time = time.time()


def progress_hook(add, total):
    global current_progress
    current_progress += add
    if total == 0:
        progress = 0
    else:
        progress = current_progress / total
    current_time = time.time()
    elapsed_time = current_time - start_time

    progress_bar.progress(progress)
    last_progress_message = (
        f"`{current_progress}/{total}` processed, "
        f"`{progress*100:.2f}%` done, "
        f"`{current_progress/(elapsed_time):.2f}`/s, "
        f"Elapsed: `{elapsed_time:.2f}`s, "
        f"ETA: `{' ∞ ' if progress == 0 else f'{(elapsed_time / progress) * (1 - progress):.2f}'}`s, "
        f"Total: `{' ∞ ' if progress == 0 else f'{elapsed_time / progress:.2f}'}`s"
    )
    progress_text.markdown(last_progress_message)


items = get_collection_items_metadata(collection_id, progress_hook)

progress_bar.progress(100)

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
