import requests
import pandas as pd
from datetime import datetime, timezone

def get_btc_usd_range(start_dt: datetime, end_dt: datetime):
    start_date = int(start_dt.replace(tzinfo=timezone.utc).timestamp())
    end_date   = int(end_dt.replace(tzinfo=timezone.utc).timestamp())
    print(start_date, end_date)

    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range"
    params = {"vs_currency": "usd", "from": start_date, "to": end_date}

    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()

    prices = r.json()["prices"]  # [[ms, price], ...]
    df = pd.DataFrame(prices, columns=["ts_ms", "price"])
    df["time"] = pd.to_datetime(df["ts_ms"], unit="ms", utc=True)
    return df[["time", "price"]]