from fastapi import FastAPI
import pandas as pd

app = FastAPI()

# Load sample data (later replace with DB)
df = pd.read_excel("sales_dashboard_report.xlsx")
app.include_router(merge_router, prefix="/api/v1/merge", tags=["Merge"])

@app.get("/data")
def get_data():
    return df.to_dict(orient="records")


@app.get("/aggregate")
def aggregate(x: str, y: str, agg: str):
    agg_map = {
        "sum": "sum",
        "avg": "mean",
        "count": "count"
    }

    grouped = df.groupby(x)[y].agg(agg_map.get(agg, "sum")).reset_index()

    return grouped.to_dict(orient="records")