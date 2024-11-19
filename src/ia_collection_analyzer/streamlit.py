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
data_transform_text.text("Data transformation and cleaning complete!")

st.write("The collection contains the following items:")
st.write(items_pd)
