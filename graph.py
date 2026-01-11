from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
import pandas as pd
from datetime import datetime, timezone, timedelta

from news import get_gdelt
from bitc import get_btc_usd_range

app = FastAPI()

@app.get("/")
def home():
    return FileResponse("static/main.html")
def data(start: str, end: str):
    start_dt = datetime.fromisoformat(start).replace(tzinfo=timezone.utc)
    end_dt = datetime.fromisoformat(end).replace(tzinfo=timezone.utc) + timedelta(days=1)

    #convert to GDELT format YYYYMMDDhhmmss
    start_gdelt = start_dt.strftime("%Y%m%d%H%M%S")
    end_gdelt = end_dt.strftime("%Y%m%d%H%M%S")

    news_df = get_gdelt("(bitcoin OR btc OR crypto)", max_records=250,
                        startdatetime=start_gdelt, enddatetime=end_gdelt)
    btc_df = get_btc_usd_range(start_dt, end_dt)

    btc_df["time"] = pd.to_datetime(btc_df["time"], utc=True, errors="coerce")
    news_df["publishedAt"] = pd.to_datetime(news_df["publishedAt"], utc=True, errors="coerce")

    news_daily = (news_df.dropna(subset=["publishedAt"])
                        .set_index("publishedAt")
                        .resample("1D")
                        .agg(avg_negativity=("negativity", "mean"),
                             article_count=("negativity", "size"))
                        .reset_index())

    btc_daily = (btc_df.dropna(subset=["time"])
                      .set_index("time")
                      .resample("1D")
                      .agg(price=("price", "last"))
                      .reset_index())

    #return as JSON arrays
    return JSONResponse({
        "btc": {
            "x": btc_daily["time"].dt.strftime("%Y-%m-%d").tolist(),
            "y": btc_daily["price"].tolist(),
        },
        "news": {
            "x": news_daily["publishedAt"].dt.strftime("%Y-%m-%d").tolist(),
            "y": news_daily["avg_negativity"].fillna(0).tolist(),
            "count": news_daily["article_count"].tolist(),
        }
    })
