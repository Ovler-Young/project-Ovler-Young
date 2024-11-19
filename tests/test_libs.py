import pytest
from ia_collection_analyzer.libs import (
    get_collection_items,
    get_item_metadata,
    get_collection_items_metadata,
)


def test_get_collection_items():
    collection_id = "us_senate"
    items = get_collection_items(collection_id)
    assert len(items) >= 3232


def test_get_item_metadata():
    collection_id = "us_senate"
    item_id = "armedA011614_1"
    metadata = get_item_metadata(item_id)
    assert collection_id in metadata["collection"]


def test_get_collection_items_metadata():
    collection_id = "speedydeletionwiki"
    items_metadata = get_collection_items_metadata(collection_id)
    assert len(items_metadata) >= 8
    for item_metadata in items_metadata:
        assert collection_id in item_metadata["collection"]
