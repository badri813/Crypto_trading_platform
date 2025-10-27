from confluent_kafka import Consumer
import json
import pandas as pd
import numpy as np
import time
import boto3


# Kafka consumer configuration
consumer_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'stock_data_consumer_group',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(consumer_config)
topic = 'stock_data'
consumer.subscribe([topic])

print(f"Subscribed to topic: {topic}")
data = []

# Timeout settings
timeout_seconds = 30
last_message_time = time.time()

try:
    while True:
        msg = consumer.poll(1.0)  # wait up to 1 second for a message

        if msg is None:
            # Check if we've reached the timeout
            if time.time() - last_message_time > timeout_seconds:
                print(f"No new messages for {timeout_seconds} seconds. Stopping consumer...")
                break
            continue

        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue

        # Reset the timeout clock on new message
        last_message_time = time.time()

        # Parse JSON message
        record = json.loads(msg.value().decode('utf-8'))
        record['Date'] = pd.to_datetime(record['Date'])
        data.append(record)

        print(f"Received record: {record}")

except KeyboardInterrupt:
    print("Stopping consumer manually...")

finally:
    consumer.close()

# Convert to DataFrame after timeout
df = pd.DataFrame(data)
if df.empty:
    print("No data received, exiting...")
    exit()

print("Raw Data:")
print(df.head())

# # Sort by Date per Ticker
# df = df.sort_values(by=["Ticker", "Date"])

# RSI Calculation function
# RSI Calculation function
def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Use transform instead of apply for aligned index
df['RSI'] = df.groupby("Ticker")['Close'].transform(lambda x: calculate_rsi(x))
df = df.dropna(subset=['RSI'])
df.to_csv('rsi.csv',index=False)


print("\nData with RSI:")
print(df[['Date', 'Ticker', 'Close', 'RSI']].tail(20))



#RSI summary
df["Overbought"] = df["RSI"] > 70
df["Oversold"] = df["RSI"] < 30

# Group by Ticker
ticker_summary = df.groupby("Ticker").agg(
    Total=("RSI", "count"),
    Overbought=("Overbought", "sum"),
    Oversold=("Oversold", "sum")
).reset_index()

# Calculate percentages
ticker_summary["Overbought%"] = 100 * ticker_summary["Overbought"] / ticker_summary["Total"]
ticker_summary["Oversold%"] = 100 * ticker_summary["Oversold"] / ticker_summary["Total"]

ticker_summary.to_csv('rsi_summary.csv',index=False)
# uploading to cloud


import boto3

# AWS credentials
aws_access_key = "AKIA3T5PI3WKGLBLF7OS"
aws_secret_key = "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"
bucket_name = "crypto-project12"

file_name1 = "rsi.csv"
file_name2 = "rsi_summary.csv"

# Create S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key
)

# Upload both files
s3.upload_file(file_name1, bucket_name, f"rsi_data/{file_name1}")
print(f"File uploaded to s3://{bucket_name}/rsi_data/{file_name1}")

s3.upload_file(file_name2, bucket_name, f"rsi_data/{file_name2}")
print(f"File uploaded to s3://{bucket_name}/rsi_data/{file_name2}")

