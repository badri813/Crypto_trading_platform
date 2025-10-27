import pymysql
import pandas as pd

# --- MySQL Connection ---
conn = pymysql.connect(
    user="root",
    host="localhost",
    db="mycrypto_2",
    password="Surya@1271"
)
cursor = conn.cursor()

# --- Read CSV File ---
df = pd.read_csv("crypto_data.csv")

# --- Convert Date to datetime for sorting ---
df["Date"] = pd.to_datetime(df["Date"])

# --- Sort by Date descending and take latest per Ticker ---
latest_df = df.sort_values("Date", ascending=False).drop_duplicates(subset=["Ticker"], keep="first")

# --- Round 'Open' to 2 decimals ---
latest_df["Close"] = latest_df["Close"].round(2)

# --- Insert into Database ---
for _, row in latest_df.iterrows():
    ticker_full = row["Ticker"]
    current_price = row["Close"]

    # Split ticker to get crypto and fiat currency
    if "-" in ticker_full:
        ticker, fiat_currency = ticker_full.split("-", 1)
    else:
        ticker = ticker_full
        fiat_currency = "UNKNOWN"

    insert_query = """
        INSERT INTO crypto_price (ticker, current_price, fiat_currency)
        VALUES (%s, %s, %s)
    """
    cursor.execute(insert_query, (ticker, str(current_price), fiat_currency))

conn.commit()
print("✅ Data inserted successfully with fiat currency!")
