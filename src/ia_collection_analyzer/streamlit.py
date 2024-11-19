import streamlit as st
import pandas as pd
import numpy as np
from libs import get_collection_items_metadata
import time

st.title("Internet Archive Collection Analyzer")

st.write(
    "This is a simple web app that analyzes the metadata of an Internet Archive collection."
)

# input the collection name
col1, col2 = st.columns([6, 1], vertical_alignment="bottom")
with col1:
    collection_id = st.text_input("Enter the collection ID:", "speedydeletionwiki")
with col2:
    conform_button = st.button("Conform")

if not conform_button:
    st.stop()


guide_text = st.markdown(
    f"Getting metadata for collection: **{collection_id}**:"
)

progress_bar = st.progress(0)
current_progress = 0
start_time = time.time()
progress_text = st.markdown("getting count and estimating time...")

def progress_hook(add, total):
    global current_progress
    current_progress += add
    progress = current_progress / total
    progress_bar.progress(progress)
    progress_text.markdown(f"`{current_progress}/{total}` items processed, `{progress*100:.2f}%` done, elapsed time: `{time.time() - start_time:.2f}s`, ETA: `{((time.time() - start_time) / progress) * (1 - progress):.2f}s`")

items = get_collection_items_metadata(collection_id, progress_hook)

progress_bar.progress(100)

data_transform_text = st.text(
    "transforming data..."
)
items_pd = pd.DataFrame(items)
data_transform_text.text(
    "cleaning data..."
)
# drop columns with 80%+ nan
items_pd = items_pd.dropna(axis=1, thresh=0.8 * len(items_pd))
data_transform_text.text("Data transformation and cleaning complete!")

st.write("The collection contains the following items:")
st.write(items_pd)
