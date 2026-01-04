import pandas as pd
import plotly.graph_objects as go
from news import get_gdelt
from bitc import get_btc_usd_range
from datetime import datetime, timezone

news_df = get_gdelt("(bitcoin OR btc OR crypto)", max_records=250, startdatetime="20251227000000",
    enddatetime="20260101000000")
end = datetime.now(timezone.utc)
start = end - pd.Timedelta(days=30)
btc_df = get_btc_usd_range(start, end)

btc_df = btc_df.copy()
news_df = news_df.copy()

btc_df["time"] = pd.to_datetime(btc_df["time"], utc=True, errors="coerce")
news_df["publishedAt"] = pd.to_datetime(news_df["publishedAt"], utc=True, errors="coerce")

news_daily = (
    news_df.dropna(subset=["publishedAt"])
           .set_index("publishedAt")
           .resample("1D")
           .agg(avg_negativity=("negativity", "mean"), article_count=("negativity", "size"))
           .reset_index())

btc_daily = (
    btc_df.dropna(subset=["time"])
          .set_index("time")
          .resample("1D")
          .agg(price=("price", "last"))
          .reset_index())

fig = go.Figure()


fig.add_trace(go.Scatter(
    x=btc_daily["time"],
    y=btc_daily["price"],
    name="BTC Price (USD)",
    yaxis="y1",
    mode="lines"
))

fig.add_trace(go.Scatter(
    x=news_daily["publishedAt"],
    y=news_daily["avg_negativity"],
    name="Avg News Negativity (0–1)",
    yaxis="y2",
    mode="lines+markers",
    # Optional: show volume on hover
    customdata=news_daily["article_count"],
    hovertemplate="Date=%{x}<br>Negativity=%{y:.3f}<extra></extra>",
))

fig.update_layout(
    title="BTC Price vs News Negativity",
    xaxis=dict(title="Date (UTC)"),
    yaxis=dict(title="BTC Price (USD)"),
    yaxis2=dict(title="Avg News Negativity", overlaying="y", side="right", rangemode="tozero"),
    legend=dict(orientation="h")
)

fig.show()