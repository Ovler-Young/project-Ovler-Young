from pathlib import Path
import json
import logging
import os
import time

import requests
import internetarchive as ia
from tqdm import tqdm
from ia_collection_analyzer.constdatas import (
    CACHE_DIR,
    ITEM_CACHE_DIR,
    COLLECTION_TTL,
    REQUIRED_METADATA,
)


CACHE_DIR.mkdir(exist_ok=True)
ITEM_CACHE_DIR.mkdir(exist_ok=True)

logger = logging.getLogger(__name__)
ia_session = ia.ArchiveSession()


def print_request(r: requests.Response, *args, **kwargs):
    for _r in r.history:
        print("Resp (history): ", _r.request.method, _r.status_code, _r.reason, _r.url)
    print(f"Resp: {r.request.method} {r.status_code} {r.reason} {r.url}")
    if r.raw._connection and r.raw._connection.sock:
        print(
            f"Conn: {r.raw._connection.sock.getsockname()} -> {r.raw._connection.sock.getpeername()[0]}"
        )


ia_session.hooks["response"].append(print_request)


def get_cache_filename(key) -> Path:
    return CACHE_DIR / f"{key}.json"


def is_cache_valid(filename, ttl: float | int) -> bool:
    if not os.path.exists(filename):
        return False

    file_mtime = os.path.getmtime(filename)
    return (time.time() - file_mtime) < ttl


def get_collection(collection_id, progress_hook=None) -> list:
    cache_key = f"collection_{collection_id}"
    cache_filename = get_cache_filename(cache_key)

    if is_cache_valid(cache_filename, COLLECTION_TTL):
        logger.info(f"Using cache for {collection_id}")
        with open(cache_filename, "r") as cache_file:
            collection = json.load(cache_file)
            if progress_hook:
                progress_hook(len(collection), len(collection))
    else:
        logger.info(f"Fetching collection {collection_id}")
        search = ia.Search(
            ia_session,
            query="collection:" + collection_id,
            sorts=["addeddate desc"],
            fields=["*"],
        )
        collection = []
        total_items = search.num_found
        if progress_hook:
            progress_hook(0, total_items)
        for result in tqdm(
            search, desc=f"Fetching {collection_id}", total=search.num_found
        ):
            collection.append(result)
            item_id = result["identifier"]
            item_cache_key = f"item/item_metadata_{item_id}"
            item_cache_filename = get_cache_filename(item_cache_key)
            if not is_cache_valid(item_cache_filename, COLLECTION_TTL):
                metadata = result
                with open(item_cache_filename, "w") as cache_file:
                    json.dump(metadata, cache_file)
            if progress_hook:
                progress_hook(1, total_items)

        with open(cache_filename, "w") as cache_file:
            json.dump(collection, cache_file, indent=2)

    return collection


def get_collection_items(collection_id) -> list:
    collection = get_collection(collection_id)
    return [item["identifier"] for item in collection]


def get_item_metadata(item_id) -> dict:
    cache_key = f"item/item_metadata_{item_id}"
    cache_filename = get_cache_filename(cache_key)

    if os.path.exists(cache_filename):
        with open(cache_filename, "r") as cache_file:
            return json.load(cache_file)
    else:
        metadata = ia_session.get_item(item_id).metadata

        with open(cache_filename, "w") as cache_file:
            json.dump(metadata, cache_file)

        return metadata


def get_collection_items_metadata(collection_id, progress_hook=None) -> list[dict]:
    metadatas = get_collection(collection_id, progress_hook)
    return metadatas


def filter_metadata(metadata: dict, additional_keys: list[str] = []) -> dict | None:
    # assert a list of things are here and in right formart
    required_keys = REQUIRED_METADATA + additional_keys
    for key in required_keys:
        if key not in metadata:
            return None
    return metadata


def calculate_metadata(metadata: dict, additional_keys: list[str] = []) -> dict | None:
    metadata = filter_metadata(metadata, additional_keys)
    if metadata is None:
        return None

    # turn addeddate to addedyear
    metadata["addedyear"] = metadata["addeddate"][:4]
    metadata["addedmonth"] = metadata["addeddate"][5:7]

    metadata["publicyear"] = metadata["publicdate"][:4]
    metadata["publicmonth"] = metadata["publicdate"][5:7]

    return metadata


if __name__ == "__main__":
    collection_id = "speedydeletionwiki"
    items = get_collection_items(collection_id)
    print(items)
    metadata = get_item_metadata(items[0])
    print(metadata)
    items_metadata = get_collection_items_metadata(collection_id)
    print(items_metadata)
