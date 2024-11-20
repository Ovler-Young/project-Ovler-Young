import pytest
from ia_collection_analyzer.iahelper import (
    get_collection_items,
    get_item_metadata,
    get_collection_items_metadata,
)


get_collection_items_tests = [
    ("speedydeletionwiki", 8, "wikipedia-delete-v3-2012-08"),
    ("us_senate",  3232, "armedA011614_1"),
]

get_item_metadata_tests = [
    ("wikipedia-delete-v2-2012-12", "speedydeletionwiki"),
    ("wikipedia-delete-v3-2012-08", "speedydeletionwiki"),
    ("wikipedia-delete-v3-2012-07", "speedydeletionwiki"),
]


@pytest.mark.parametrize("collection_id, expected_min_length, one_expected_id", get_collection_items_tests)
def test_get_collection_items(collection_id, expected_min_length, one_expected_id):
    items = get_collection_items(collection_id)
    assert isinstance(items, list)
    assert len(items) >= expected_min_length
    assert one_expected_id in items


@pytest.mark.parametrize("item_id, collection_id", get_item_metadata_tests)
def test_get_item_metadata(item_id, collection_id):
    metadata = get_item_metadata(item_id)
    assert isinstance(metadata, dict)
    assert collection_id in metadata["collection"]


def test_get_collection_items_metadata():
    collection_id = "speedydeletionwiki"
    items_metadata = get_collection_items_metadata(collection_id)
    assert isinstance(items_metadata, list)
    assert len(items_metadata) >= 8
    for item_metadata in items_metadata:
        assert isinstance(item_metadata, dict)
        assert collection_id in item_metadata["collection"]
