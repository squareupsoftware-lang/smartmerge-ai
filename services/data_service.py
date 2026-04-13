from functools import lru_cache
from core.config import settings
import pandas as pd
import logging
import threading


FILE_PATH = settings.MERGED_FILE_PATH

logging.info(f"Aggregation request: {x}, {y}, {agg}")

@lru_cache()
def load_data():
    return pd.read_excel(FILE_PATH)


def get_data():
    df = load_data()
    return df.to_dict(orient="records")


def aggregate_data(x, y, agg):
    df = load_data()

    agg_map = {
        "sum": "sum",
        "avg": "mean",
        "count": "count"
    }

    grouped = df.groupby(x)[y].agg(agg_map.get(agg, "sum")).reset_index()
    return grouped.to_dict(orient="records")
    
from functools import lru_cache
from core.config import settings
import pandas as pd
import logging
import threading

FILE_PATH = settings.FILE_PATH


# ✅ Load data with caching
@lru_cache()
def load_data():
    logging.info("Loading data from file...")
    return pd.read_excel(FILE_PATH)


# ✅ Clear cache (IMPORTANT when file updates)
def refresh_data():
    load_data.cache_clear()
    logging.info("Data cache cleared")


# ✅ Get data with pagination
def get_data(limit=100, offset=0):
    df = load_data()
    return df.iloc[offset:offset+limit].to_dict(orient="records")


# ✅ Aggregation with validation + logging
def aggregate_data(x, y, agg):
    df = load_data()

    # 🔐 Validation
    if x not in df.columns or y not in df.columns:
        logging.error(f"Invalid columns: {x}, {y}")
        return {"error": "Invalid column name"}

    agg_map = {
        "sum": "sum",
        "avg": "mean",
        "count": "count"
    }

    logging.info(f"Aggregation request: x={x}, y={y}, agg={agg}")

    grouped = df.groupby(x)[y].agg(agg_map.get(agg, "sum")).reset_index()

    return grouped.to_dict(orient="records")


# ✅ Background processing with safety
def process_large_file():
    try:
        logging.info("Background job started")

        df = load_data()

        # Simulate heavy work
        df.describe()

        logging.info("Processing complete")

    except Exception as e:
        logging.error(f"Background job failed: {str(e)}")


# ✅ Start background job
def start_background_job():
    thread = threading.Thread(target=process_large_file, daemon=True)
    thread.start()

    logging.info("Background thread started")