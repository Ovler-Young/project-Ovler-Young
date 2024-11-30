import streamlit as st
import pandas as pd
import numpy as np
from ia_collection_analyzer.getmetadatas import fetch_metadata
from ia_collection_analyzer.constdatas import REQUIRED_METADATA
from ia_collection_analyzer.pdhelper import normalize_list_columns

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
if "items_length" not in st.session_state:
    st.session_state.items_length = 0
if "progress_message" not in st.session_state:
    st.session_state.progress_message = None
if "selected_columns" not in st.session_state:
    st.session_state.selected_columns = []
if "filtered_pd" not in st.session_state:
    st.session_state.filtered_pd = None
if "transform_history" not in st.session_state:
    st.session_state.transform_history = []
if "transformed_columns" not in st.session_state:
    st.session_state.transformed_columns = []
if "original_values" not in st.session_state:
    st.session_state.original_values = {}


@st.fragment
def collection_input():
    """Fragment for collection ID input and metadata fetching"""
    # input the collection name
    col1, col2 = st.columns([6, 1], vertical_alignment="bottom")
    with col1:
        collection_id = st.text_input("Enter the collection ID:", "bilibili_videos")
        collection_id = (
            collection_id.strip()
            .replace(" ", "_")
            .replace('"', "")
            .replace("'", "")
            .replace("(", "")
            .replace(")", "")
        )
    with col2:
        conform_button = st.button("Conform")

    if not conform_button and not st.session_state.got_metadata or collection_id == "":
        st.stop()

    if (
        st.session_state.got_metadata
        and collection_id == st.session_state.collection_id
    ):
        items_pd = st.session_state.items_pd
        # progress_message
        progress_message = st.session_state.progress_message
        st.markdown(progress_message)
        st.write("The collection contains the following items:")
        try:
            st.write(items_pd.head(10))
        except Exception as e:
            st.markdown("Failed to display top 10 lines. Only first will be shown.")
            st.write(items_pd.head(1))
            st.write(e)

        return

    # Check if we need to fetch new data
    if (
        not st.session_state.got_metadata
        or collection_id != st.session_state.collection_id
    ):
        st.markdown(f"Getting fresh metadata for collection: **{collection_id}**")
        items, progress_message = fetch_metadata(collection_id)
        data_transform_text = st.text("Transforming data...")
        items_pd = pd.DataFrame(items)
        if items_pd.empty:
            st.error(
                "Failed to fetch metadata for the collection. Please check the collection ID."
            )
            st.stop()

        data_transform_text.text("cleaning data...")
        # drop columns with 80%+ nan
        items_pd = items_pd.dropna(axis=1, thresh=0.8 * len(items_pd))
        items_pd = items_pd.dropna(axis=0, thresh=0.7 * len(items_pd.columns))
        # drop mediatype=collections
        items_pd = items_pd[items_pd["mediatype"] != "collection"]
        items_pd = normalize_list_columns(items_pd)

        # drop columns with different types inner.
        # for col in items_pd.columns:
        #    items_pd[col] = items_pd[col].apply(lambda x: x if isinstance(x, type(items_pd[col][0])) else np.nan)

        # calculate metadata
        data_transform_text.text("calculating metadata...")
        items_pd["addeddate"] = pd.to_datetime(items_pd["addeddate"])
        # items_pd["publicdate"] = pd.to_datetime(items_pd["publicdate"])

        # Use 'date' column if it exists, otherwise use 'addeddate'
        date_column = "date" if "date" in items_pd.columns else "addeddate"

        # year, month, and day should be recalculated
        items_pd["year"] = pd.to_datetime(items_pd[date_column]).dt.year
        items_pd["month"] = pd.to_datetime(items_pd[date_column]).dt.month
        items_pd["day"] = pd.to_datetime(items_pd[date_column]).dt.day
        data_transform_text.text("Data transformation and cleaning complete!")

        # Update cache
        st.session_state.items_pd = items_pd
        st.session_state.items_length = len(items_pd)
    else:
        st.markdown(f"Using cached metadata for collection: **{collection_id}**")
        items_pd = st.session_state.items_pd

    st.session_state.got_metadata = True
    st.session_state.collection_id = collection_id
    st.session_state.progress_message = progress_message
    st.session_state.selected_columns = []

    st.rerun()


@st.fragment
def column_selector():
    """Fragment for selecting columns to analyze"""
    items_pd = st.session_state.items_pd

    st.header("Selecting columns to analyze")
    st.write("Select additional columns you want to analyze:")
    seleactable_columns = [
        col for col in items_pd.columns if col not in REQUIRED_METADATA
    ]

    col1, col2 = st.columns([6, 1], vertical_alignment="bottom")
    selected_columns = st.multiselect(
        "Select columns:", seleactable_columns, default=[]
    )

    # Update the filtering code to use cache
    if (
        st.session_state.filtered_pd is None
        or selected_columns != st.session_state.selected_columns
    ):
        filtered_pd = items_pd[selected_columns + REQUIRED_METADATA]
        filtered_pd = filtered_pd.dropna(axis=0, how="any")

        # Cache the filtered dataframe and selected columns
        st.session_state.filtered_pd = filtered_pd
        st.session_state.selected_columns = selected_columns
    else:
        filtered_pd = st.session_state.filtered_pd

    # Display preview (existing code)
    st.write("Preview of the selected columns:")
    st.write(filtered_pd.head(30))


@st.fragment
def transform_data():
    """Fragment for transforming data"""
    transform_needed = st.selectbox(
        "Would you like to transform any columns before analysis?",
        ["No", "Yes"],
        index=0,
        placeholder="No",
    )

    if transform_needed == "No":
        return

    selected_columns = st.session_state.selected_columns
    items_length = st.session_state.items_length
    filtered_pd = st.session_state.filtered_pd

    st.header("Transform Column")
    st.write("Transform an existing column with data transformations")

    col1, col2 = st.columns([2, 3], vertical_alignment="bottom")

    with col1:
        source_col = st.selectbox("Select column to transform:", selected_columns)

    with col2:
        transform_type = st.selectbox(
            "Select transformation:",
            [
                "Value Mapping",
                "Date Quarter",
                "Date Week",
                "String Prefix",
                "Numeric Bins",
            ],
        )

    # Add transformation params based on type
    if transform_type == "String Prefix":
        prefix_len = st.number_input("Prefix length:", min_value=1, value=10)

    elif transform_type == "Value Mapping":
        # Initialize storage
        if "used_values" not in st.session_state:
            st.session_state.used_values = set()
        if "mapping_table" not in st.session_state:
            st.session_state.mapping_table = []

        # Threshold control
        st.subheader("Grouping Settings")
        threshold_type = st.selectbox(
            "Group rare values threshold:",
            ["Minimum count", "1%", "0.1%", "0.01%", "Custom ratio"],
            index=1,
        )

        if threshold_type == "Custom ratio":
            ratio = st.number_input(
                "Enter ratio (e.g. 0.001 for 0.1%):",
                min_value=0.0,
                max_value=1.0,
                value=0.001,
                step=0.000001,
            )
            threshold = ratio
        elif threshold_type == "Minimum count":
            min_count = st.number_input(
                "Minimum count per value:", min_value=1, value=100
            )
            threshold = min_count / items_length
        else:
            ratio_map = {"1%": 0.01, "0.1%": 0.001, "0.01%": 0.0001}
            threshold = ratio_map[threshold_type]

        # Value analysis with grouping
        value_counts = filtered_pd[source_col].value_counts()
        total_count = value_counts.sum()

        small_values = value_counts[value_counts < threshold * total_count]
        main_values = value_counts[value_counts >= threshold * total_count]

        if not small_values.empty:
            main_values["Others (values < " + str(threshold * 100) + "%)"] = (
                small_values.sum()
            )

        # Format values for display
        formatted_values = [f"{v} ({c})" for v, c in main_values.items()]

        # Mapping interface
        st.subheader("Create Mapping")
        # Column layout for selector controls
        col1, col2, col3 = st.columns([5, 3, 1], vertical_alignment="bottom")
        with col1:
            available_values = [
                v for v in formatted_values if v not in st.session_state.used_values
            ]
            selected_sources = st.multiselect(
                "Source Values:",
                available_values,
                placeholder="Choose values to map",
                key="source_values",
                default=[available_values[0]] if available_values else [],
                on_change=None,
            )

        with col2:
            available_targets = [
                v for v in formatted_values if v not in st.session_state.used_values
            ]
            available_targets.append("Custom value...")

            target_value = st.selectbox(
                "Target Value:", available_targets, key="target_value"
            )

            if target_value == "Custom value...":
                custom_target = st.text_input(
                    "Enter custom value:", key="custom_target"
                )
                target_value = f"{custom_target} (custom)"

        with col3:
            if st.button("Add", key="add_mapping"):
                if target_value and selected_sources:
                    source_values = [s.split(" (")[0] for s in selected_sources]
                    target = target_value.split(" (")[0]

                    # Calculate counts
                    orig_count = sum(value_counts[s] for s in source_values)

                    st.session_state.mapping_table.append(
                        {
                            "sources": source_values,
                            "target": target,
                            "count": orig_count,
                        }
                    )
                    st.session_state.used_values.update(selected_sources)

                    st.rerun(scope="fragment")

        # Display mappings with counts
        if st.session_state.mapping_table:
            st.write("Current Mappings:")
            for mapping in st.session_state.mapping_table:
                sources = " | ".join(mapping["sources"])
                st.write(
                    f"{sources} => {mapping['target']} (Count: {mapping['count']})"
                )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Clear All Mappings", key="clear_mappings"):
                    st.session_state.mapping_table = []
                    st.session_state.used_values = set()
                    st.rerun(scope="fragment")
            with col2:
                if st.button("Revert Last Mapping", key="revert_mapping"):
                    # Remove values from used_values set
                    last_mapping = st.session_state.mapping_table[-1]
                    last_sources = [
                        f"{s} ({value_counts[s]})" for s in last_mapping["sources"]
                    ]
                    st.session_state.used_values.difference_update(last_sources)

                    # Remove last mapping
                    st.session_state.mapping_table.pop()
                    st.rerun(scope="fragment")

    elif transform_type == "Numeric Bins":
        num_bins = st.number_input("Number of bins:", min_value=2, value=5)

    if st.button("Preview Transformation"):
        if transform_type == "Date Quarter":
            new_col = pd.to_datetime(filtered_pd[source_col]).dt.quarter
        elif transform_type == "Date Week":
            new_col = pd.to_datetime(filtered_pd[source_col]).dt.isocalendar().week
        elif transform_type == "String Prefix":
            new_col = filtered_pd[source_col].str[:prefix_len]
        elif transform_type == "Numeric Bins":
            new_col = pd.qcut(filtered_pd[source_col], num_bins, labels=False)
        elif transform_type == "Value Mapping":
            new_col = filtered_pd[source_col].copy()
            for mapping in st.session_state.mapping_table:
                new_col = new_col.replace(mapping["sources"], mapping["target"])

        # Show preview
        preview_df = pd.DataFrame(
            {"Original": filtered_pd[source_col], "Transformed": new_col}
        )
        st.write("Preview of first 30 rows:")
        st.write(preview_df.head(30).T)

        if st.button("Apply Transformation"):
            filtered_pd[source_col] = new_col
            st.session_state.filtered_pd = filtered_pd
            st.session_state.transformed_columns.append(source_col)
            st.session_state.transform_history.append(
                {"source_col": source_col, "transform_type": transform_type}
            )
            st.session_state.original_values[source_col] = preview_df["Original"]

            st.rerun()


@st.fragment
def plot_data():
    """Fragment for data visualization"""
    if not st.session_state.filtered_pd is not None:
        return

    filtered_pd = st.session_state.filtered_pd
    plotable_columns = st.session_state.selected_columns + REQUIRED_METADATA

    col1, col2, col3 = st.columns([3, 3, 1], vertical_alignment="bottom")
    with col1:
        x_axis = st.selectbox("Select the x-axis:", plotable_columns, index=0)
    with col2:
        y_axis = st.selectbox("Select the y-axis:", plotable_columns, index=1)
    with col3:
        plot_button = st.button("Plot")

    if plot_button and x_axis != y_axis:
        st.write("Plotting the data...")
        st.write(f"X-axis: {x_axis}, Y-axis: {y_axis}")

        # if y_axis is hashable , plot
        if isinstance(filtered_pd[y_axis].iloc[0], (int, float, np.int64, np.float64)):
            # Create comprehensive aggregation table
            all_metrics = (
                filtered_pd.groupby(x_axis)[y_axis]
                .agg(
                    [
                        ("Count", "count"),
                        ("Sum", "sum"),
                        ("Mean", "mean"),
                        ("Median", "median"),
                        ("Min", "min"),
                        ("Max", "max"),
                    ]
                )
                .reset_index()
            )

            # Display complete aggregated data
            st.write("Complete aggregation metrics:")
            # Create multi-line chart (excluding Count since it's often on different scale)
            metrics_for_plot = all_metrics.drop(columns=["Count", "Sum", "Max"])
            metrics_for_plot = metrics_for_plot.set_index(x_axis)

            st.write("Multi-metric trend lines:")
            st.line_chart(metrics_for_plot)

            st.write(all_metrics)

        # if y_axis is not numeric, count and plot
        else:
            st.write("Analyzing distribution across categories...")

            # Create mask for list and non-list values
            is_list_mask = filtered_pd[y_axis].apply(lambda x: isinstance(x, list))

            # Handle list values
            list_data = filtered_pd[is_list_mask][[x_axis, y_axis]].copy()
            exploded_list = list_data.explode(y_axis)

            # Handle non-list values
            non_list_data = filtered_pd[~is_list_mask][[x_axis, y_axis]]

            # Combine results efficiently
            expanded_df = pd.concat([exploded_list, non_list_data])

            # Create pivot table and plot
            pivot_table = (
                pd.crosstab(expanded_df[x_axis], expanded_df[y_axis], normalize="index")
                * 100
            )

            st.bar_chart(pivot_table)

            st.write("Distribution counts:")
            counts_df = pd.crosstab(expanded_df[x_axis], expanded_df[y_axis])
            st.write(counts_df)


def main():
    collection_input()
    if st.session_state.got_metadata:
        column_selector()
        if st.session_state.filtered_pd is not None:
            transform_data()
            plot_data()


if __name__ == "__main__":
    main()
