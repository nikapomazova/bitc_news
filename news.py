import requests
import pandas as pd
import plotly.express as px
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def get_gdelt(query="bitcoin", max_records=250, startdatetime=None, enddatetime=None):

    url = "https://api.gdeltproject.org/api/v2/doc/doc"

    params = {
        "query": query,
        "mode": "ArtList",
        "format": "json",
        "maxrecords": max_records,
        "sort": "hybridrel",
    }
    if startdatetime:
        params["startdatetime"] = startdatetime
    if enddatetime:
        params["enddatetime"] = enddatetime

    r = requests.get(url, params=params, timeout=30)

    if r.status_code != 200:
        print("GDELT status:", r.status_code)
        print("Response (first 500 chars):")
        print(r.text[:500])
        r.raise_for_status()

    try:
        payload = r.json()
    except Exception:
        print("Response was not JSON. First 500 chars:")
        print(r.text[:500])
        raise

    articles = payload.get("articles", [])
    print("Keys in first article:", list(articles[0].keys()) if articles else "no articles")
    rows = []
    for a in articles:
        rows.append({
            "publishedAt": a.get("seendate"),
            "title": a.get("title"),
            "source": a.get("sourceCountry") or a.get("sourceCollection") or a.get("domain"),
            "url": a.get("url"),
            "desc": a.get("description"),
        })

    df = pd.DataFrame(rows)
    def negativity_score(text: str) -> float: #Returns a 0-1 score where 1 = very negative.

        if not isinstance(text, str) or not text.strip():
            return 0.0
        return analyzer.polarity_scores(text)["neg"]
    
    if not df.empty:
        df["publishedAt"] = pd.to_datetime(df["publishedAt"], utc=True, errors="coerce")
        df["text_for_sentiment"] = (df["title"].fillna("") + " " + df["desc"].fillna(""))
        df["negativity"] = df["text_for_sentiment"].apply(negativity_score)

    df = df.drop_duplicates(subset=["url"])
    return df