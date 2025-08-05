import yfinance as yf
import pandas as pd
import ta
from telegram import Bot
from datetime import datetime
import time
from flask import Flask
import threading
import os

# ✅ Securely fetch token and chat ID from environment
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ✅ Telegram Bot Setup
bot = Bot(token=TOKEN)

# ✅ Market Index Tickers
TICKERS = {
    "NIFTY 50": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "FINNIFTY": "^NSEFIN",     # Usually correct for FinNifty (else use yfinance symbol search)
    "SENSEX": "^BSESN"
}

# ✅ Market Analysis Function
def analyze_market(name, symbol):
    try:
        df = yf.download(symbol, period="1d", interval="5m", progress=False)
        df.dropna(inplace=True)

        df['RSI'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()
        df['VWAP'] = ta.volume.VolumeWeightedAveragePrice(
            high=df['High'], low=df['Low'], close=df['Close'], volume=df['Volume']
        ).vwap()

        latest = df.iloc[-1]
        rsi = latest['RSI']
        price = latest['Close']
        vwap = latest['VWAP']
        now = datetime.now().strftime('%H:%M:%S')

        # Signal Generation
        if rsi > 60 and price > vwap:
            message = f"🚀 *BUY ALERT - {name} CE*\n🕒 {now}\n📈 RSI: {int(rsi)}\n💰 Price: ₹{round(price)}\n🎯 Target: ₹90 | 🛑 SL: ₹35"
        elif rsi < 40 and price < vwap:
            message = f"🔻 *SELL ALERT - {name} PE*\n🕒 {now}\n📉 RSI: {int(rsi)}\n💰 Price: ₹{round(price)}\n🎯 Target: ₹85 | 🛑 SL: ₹30"
        else:
            message = f"⚠️ *NO TRADE ZONE - {name}*\n🕒 {now}\nRSI: {int(rsi)} | Price: ₹{round(price)}\nReason: Weak or Sideways"

        # Send to Telegram
        bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')
        print(f"✅ Sent: {message}")
    
    except Exception as e:
        error_msg = f"❌ Error while analyzing {name}: {str(e)}"
        print(error_msg)
        bot.send_message(chat_id=CHAT_ID, text=error_msg)

# ✅ Flask Server to Keep Alive (for Replit/UptimeRobot)
app = Flask('')
@app.route('/')
def home():
    return "💡 Trading Bot is Running!"

def run_server():
    app.run(host='0.0.0.0', port=8080)

threading.Thread(target=run_server).start()

# ✅ Main Loop - runs every 5 mins
while True:
    print("🔍 Market Scan Started...")
    for name, symbol in TICKERS.items():
        analyze_market(name, symbol)
    print("🛌 Sleeping for 5 mins...\n")
    time.sleep(300)
