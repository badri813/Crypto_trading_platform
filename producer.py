import yfinance as yf
import pandas as pd
from confluent_kafka import Producer
import json

# Define tickers
tickerStrings = ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "ADA-USD", "DOGE-USD", "AVAX-USD", "DOT-USD", "USDT-USD"]

# Download 2 days of data for each ticker
df = yf.download(tickerStrings, group_by='Ticker', period='30d')

# Transform the DataFrame: stack tickers into multi-index (Date, Ticker)
df = df.stack(level=0).rename_axis(['Date', 'Ticker']).reset_index(level=1)

# Flatten columns to single-level
df.columns = ['Ticker'] + [col if isinstance(col, str) else col[0] for col in df.columns[1:]]

# Reset index to make Date a column instead of index
df = df.reset_index()

# Convert DataFrame rows to JSON objects
records = df.to_dict(orient='records')

# Kafka producer configuration
producer_config = {
    'bootstrap.servers': 'localhost:9092'
}
producer = Producer(producer_config)

# Send each record to Kafka
df['Date'] = df['Date'].astype(str)  # or df['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')
records = df.to_dict(orient='records')

topic = 'stock_data'
for record in records:
    producer.produce(topic, key=str(record['Date']), value=json.dumps(record))

producer.flush()

print("Data sent to Kafka successfully!")
