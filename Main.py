import pandas as pd
import plotly.graph_objects as go
from news import get_gdelt
from bitc import get_btc
from datetime import datetime, timezone

end = datetime.now(timezone.utc)
start = end - pd.Timedelta(days=30)
start_gdelt = start.strftime("%Y%m%d%H%M%S")
end_gdelt = end.strftime("%Y%m%d%H%M%S")
news = get_gdelt("(bitcoin OR btc OR crypto)", max_records=250, startdatetime=start_gdelt,
    enddatetime=end_gdelt)
btc = get_btc(start, end)
resample_time = "1D"

btc = btc.copy()
news = news.copy()

btc["time"] = pd.to_datetime(btc["time"], utc=True, errors="coerce")
news["publishedAt"] = pd.to_datetime(news["publishedAt"], utc=True, errors="coerce")

news_daily = (
    news.dropna(subset=["publishedAt"])
           .set_index("publishedAt")
           .resample(resample_time)
           .agg(avg_negativity=("negativity", "mean"), article_count=("negativity", "size"))
           .reset_index())

btc_daily = (
    btc.dropna(subset=["time"])
          .set_index("time")
          .resample(resample_time)
          .agg(price=("price", "last"))
          .reset_index())

fig = go.Figure()


fig.add_trace(go.Scatter(
    x=btc_daily["time"],
    y=btc_daily["price"],
    name="BTC Price (CAD)",
    yaxis="y1",
    mode="lines"
))

fig.add_trace(go.Scatter(
    x=news_daily["publishedAt"],
    y=news_daily["avg_negativity"],
    name="Avg News Negativity (0–1)",
    yaxis="y2",
    mode="lines+markers",
    customdata=news_daily["article_count"],
    hovertemplate="Date=%{x}<br>Negativity=%{y:.3f}<extra></extra>",
))

fig.update_layout(
    title="BTC Price vs News Negativity",
    xaxis=dict(title="Date (UTC)"),
    yaxis=dict(title="BTC Price (USD)"),
    yaxis2=dict(title="Avg News Negativity", overlaying="y", side="right"),
    legend=dict(orientation="h")
)

fig.show()