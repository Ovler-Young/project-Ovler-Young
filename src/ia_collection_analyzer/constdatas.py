from pathlib import Path

# File system paths
CACHE_DIR = Path("cache")
ITEM_CACHE_DIR =  CACHE_DIR / "item"

# Cache configuration 
COLLECTION_TTL = 30 * 24 * 3600  # 30 * 24 hours in seconds

# Required metadata fields
REQUIRED_METADATA = [
    "addeddate",
    # "publicdate",  # don't have too much meaning for our analyze
    "identifier",
    "mediatype",
    # "uploader", # IA removed this field automatically.
]