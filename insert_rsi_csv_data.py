import pandas as pd
import pymysql
import os

project_path = r"C:\Users\Owner\PycharmProjects\Crypto"
csv_file = os.path.join(project_path, "rsi_summary.csv")

df = pd.read_csv(csv_file)

conn = pymysql.connect(
    user="root",
    host="localhost",
    db="mycrypto_2",
    password="Surya@1271"
)
cursor = conn.cursor()


# Optional: clear previous data
# cursor.execute("DELETE FROM rsi_summary")

for index, row in df.iterrows():
    cursor.execute("""
        INSERT INTO rsi_summary 
        (Ticker, Total, Overbought, Oversold, OverboughtPercent, OversoldPercent)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (row['Ticker'], row['Total'], row['Overbought'], row['Oversold'], row['Overbought%'], row['Oversold%']))

conn.commit()


print("CSV data inserted into MySQL database successfully.")
