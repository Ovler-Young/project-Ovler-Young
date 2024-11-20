from pathlib import Path

# File system paths
CACHE_DIR = Path("cache")
ITEM_CACHE_DIR =  CACHE_DIR / "item"

# Cache configuration 
COLLECTION_TTL = 7 * 24 * 3600  # 7 * 24 hours in seconds

# Required metadata fields
REQUIRED_METADATA = [
    "addeddate",
    "publicdate", 
    "identifier",
    "mediatype",
    # "uploader", # IA removed this field automatically.
]