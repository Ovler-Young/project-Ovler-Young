import time

import streamlit as st

from ia_collection_analyzer.iahelper import get_collection_items_metadata


def fetch_metadata(collection_id):
    progress_message = st.markdown("Getting count and estimating time...")
    progress_bar = st.progress(0)
    items_processed = 0
    start_time = time.time()

    def progress_hook(add, total):
        nonlocal items_processed
        items_processed += add
        progress = 0 if total == 0 else items_processed / total
        current_time = time.time()
        elapsed_time = current_time - start_time

        last_progress_message = (
            f"`{items_processed}/{total}` processed, "
            f"`{progress*100:.2f}%` done, "
            f"`{items_processed/(elapsed_time):.2f}`/s, "
            f"Elapsed: `{elapsed_time:.2f}`s, "
            f"ETA: `{' ∞ ' if progress == 0 else f'{(elapsed_time / progress) * (1 - progress):.2f}'}`s, "
            f"Total: `{' ∞ ' if progress == 0 else f'{elapsed_time / progress:.2f}'}`s"
        )
        progress_message.markdown(last_progress_message)
        progress_bar.progress(progress)

    items = get_collection_items_metadata(collection_id, progress_hook)
    progress_bar.progress(100)

    return items
