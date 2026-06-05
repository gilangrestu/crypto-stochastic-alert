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
        data = requests.get(url).json()

        df = pd.DataFrame(data)

        high = df[2].astype(float)
        low = df[3].astype(float)
        close = df[4].astype(float)

        lowest = low.rolling(14).min()
        highest = high.rolling(14).max()

        k = ((close - lowest) / (highest - lowest)) * 100
        d = k.rolling(3).mean()

        if len(k.dropna()) < 5:
            return

        # Golden Cross <20
        if (
            k.iloc[-2] < d.iloc[-2]
            and k.iloc[-1] > d.iloc[-1]
            and k.iloc[-1] < 20
        ):
            send_telegram(
                f"🚀 BUY ALERT\n\n{symbol}\n4H Stochastic Golden Cross <20\nK={k.iloc[-1]:.2f}\nD={d.iloc[-1]:.2f}"
            )

        # Death Cross >80
        if (
            k.iloc[-2] > d.iloc[-2]
            and k.iloc[-1] < d.iloc[-1]
            and k.iloc[-1] > 80
        ):
            send_telegram(
                f"🔻 SELL ALERT\n\n{symbol}\n4H Stochastic Death Cross >80\nK={k.iloc[-1]:.2f}\nD={d.iloc[-1]:.2f}"
            )

    except Exception as e:
        print(symbol, e)

send_telegram("✅ Bot berhasil berjalan dari GitHub Actions")
