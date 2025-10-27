import yfinance as yf
import pandas as pd
import pymysql

# Tickers
tickers = ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD",
           "ADA-USD", "DOGE-USD", "AVAX-USD", "DOT-USD", "USDT-USD"]

# Download daily OHLCV data
data = yf.download(tickers, period="3d", interval="1d", group_by="ticker")

# Convert to clean tabular format
df = data.stack(level=0).reset_index()
df.rename(columns={"level_1": "Ticker"}, inplace=True)

# Calculate percentage change
df['percentage_change'] = df.groupby('Ticker')['Close'].pct_change()
df.dropna(inplace=True)

df.to_csv("crypto_data.csv", index=False)
print("Data saved to crypto_data.csv")

print('printing data with percentage change...........')
print(df)


conn=pymysql.connect(user="root",host="localhost",db="mycrypto_2", password="Surya@1271")
cursor = conn.cursor()


insert_query = """
INSERT INTO crypto_data (Date, Ticker, Open, High, Low, Close, Volume, percentage_change)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""


for _, row in df.iterrows():
    cursor.execute(insert_query, (
        row['Date'].strftime('%Y-%m-%d'),   # format date properly
        row['Ticker'],
        row['Open'],
        row['High'],
        row['Low'],
        row['Close'],
        int(row['Volume']) if not pd.isna(row['Volume']) else None,
        row['percentage_change'] if not pd.isna(row['percentage_change']) else None
    ))


conn.commit()


print("Data inserted into MySQL successfully")
