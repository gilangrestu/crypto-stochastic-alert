import os
import requests
import pandas as pd

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })

def get_futures_symbols():
    url = "https://fapi.binance.com/fapi/v1/ticker/24hr"

    r = requests.get(url)
    print(r.status_code)
    print(r.text[:500])

    data = r.json()

    usdt_pairs = [
        x for x in data
        if isinstance(x, dict)
        and x["symbol"].endswith("USDT")
        and float(x["quoteVolume"]) > 10000000
    ]

    usdt_pairs.sort(
        key=lambda x: float(x["quoteVolume"]),
        reverse=True
    )

    return [x["symbol"] for x in usdt_pairs[:50]]

def stochastic_signal(symbol):
    try:
        url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval=4h&limit=100"

        response = requests.get(url)

        send_telegram(
            f"STATUS={response.status_code}\n{response.text[:300]}"
        )

    except Exception as e:
        send_telegram(f"ERROR {symbol}\n{str(e)}")

stochastic_signal("HYPEUSDT")
