import requests

def get_btc_usd():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin", "vs_currencies": "usd"}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()["bitcoin"]["usd"]

print("BTC/USD:", get_btc_usd())
