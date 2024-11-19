import internetarchive as ia

CACHE_DIR = "cache"


def get_collection_items(collection_id):
    items = ia.search_items("collection:" + collection_id)
    return [item["identifier"] for item in items]


def get_item_metadata(item_id):
    return ia.get_item(item_id).metadata


def get_collection_items_metadata(collection_id):
    items = get_collection_items(collection_id)
    return [get_item_metadata(item) for item in items]
