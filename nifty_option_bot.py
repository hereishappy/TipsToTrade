import yfinance as yf
import pandas as pd
import ta
from telegram import Bot
from datetime import datetime
import os

TOKEN = os.getenv("8423358482:AAGB9R8CnDayqOhnr3fBbeGFQWu40I5SpL0")
CHAT_ID = os.getenv("6251267218")
bot = Bot(token=TOKEN)

def send_signal():
    try:
        df = yf.download("^NSEI", period="1d", interval="5m")
        df.dropna(inplace=True)

        df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
        df['VWAP'] = ta.volume.VolumeWeightedAveragePrice(df['High'], df['Low'], df['Close'], df['Volume']).vwap()
        
        latest = df.iloc[-1]
        rsi = latest['RSI']
        price = latest['Close']
        vwap = latest['VWAP']
        now = datetime.now().strftime('%H:%M:%S')

        if rsi > 60 and price > vwap:
            message = f"🚀 *BUY ALERT - NIFTY CE*\n🕒 {now}\n📈 RSI: {int(rsi)}\n💰 Price: {round(price)}\n🎯 Target: ₹90 | 🛑 SL: ₹35"
        elif rsi < 40 and price < vwap:
            message = f"🔻 *SELL ALERT - NIFTY PE*\n🕒 {now}\n📉 RSI: {int(rsi)}\n💰 Price: {round(price)}\n🎯 Target: ₹85 | 🛑 SL: ₹30"
        else:
            message = f"⚠️ *NO TRADE ZONE*\n🕒 {now}\nRSI: {int(rsi)} | Price: ₹{round(price)}\nReason: Rangebound or Weak Signal"

        bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')
    except Exception as e:
        bot.send_message(chat_id=CHAT_ID, text=f"❌ Error: {str(e)}")

send_signal()
