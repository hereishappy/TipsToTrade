import yfinance as yf
import pandas as pd
import ta
from telegram import Bot
from datetime import datetime
import time
from flask import Flask
import threading

bot = Bot(token="8423358482:AAGB9R8CnDayqOhnr3fBbeGFQWu40I5SpL0")
CHAT_ID = "6251267218"

TICKERS = {
    "NIFTY 50": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "FINNIFTY": "NIFTY_FIN_SERVICE.NS",
    "SENSEX": "^BSESN"
}

def analyze_market(name, symbol):
    try:
        df = yf.download(symbol, period="1d", interval="5m", progress=False)
        df.dropna(inplace=True)

        df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
        df['VWAP'] = ta.volume.VolumeWeightedAveragePrice(
            df['High'], df['Low'], df['Close'], df['Volume']).vwap()

        latest = df.iloc[-1]
        rsi = latest['RSI']
        price = latest['Close']
        vwap = latest['VWAP']
        now = datetime.now().strftime('%H:%M:%S')

        if rsi > 60 and price > vwap:
            message = f"🚀 *BUY ALERT - {name} CE*\n🕒 {now}\n📈 RSI: {int(rsi)}\n💰 Price: ₹{round(price)}\n🎯 Target: ₹90 | 🛑 SL: ₹35"
        elif rsi < 40 and price < vwap:
            message = f"🔻 *SELL ALERT - {name} PE*\n🕒 {now}\n📉 RSI: {int(rsi)}\n💰 Price: ₹{round(price)}\n🎯 Target: ₹85 | 🛑 SL: ₹30"
        else:
            message = f"⚠️ *NO TRADE ZONE - {name}*\n🕒 {now}\nRSI: {int(rsi)} | Price: ₹{round(price)}\nReason: Weak or Sideways"

        bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')
        print(f"✅ Sent: {message}")
    except Exception as e:
        bot.send_message(chat_id=CHAT_ID, text=f"❌ Error: {str(e)}")
        print(f"❌ Error: {e}")

# Flask server to keep bot alive
app = Flask('')
@app.route('/')
def home():
    return "Bot is running."

def run():
    app.run(host='0.0.0.0', port=8080)

t = threading.Thread(target=run)
t.start()

# Bot loop
while True:
    print("📊 Checking Market...")
    for name, symbol in TICKERS.items():
        analyze_market(name, symbol)
    print("🛌 Sleeping for 5 mins...\n")
    time.sleep(300)
