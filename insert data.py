import pymysql
import csv

conn = pymysql.connect(
    user="root",
    host="localhost",
    db="mycrypto_2",
    password="Surya@1271"
)
cursor = conn.cursor()

with open('crypto_price_data.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    headers = next(reader)

    if headers != ['ticker', 'current_price', 'fiat_currency']:
        print(" Error: CSV headers must be exactly: ticker,current_price,fiat_currency")
    else:
        insert_query = """
            INSERT INTO crypto_price (ticker, current_price, fiat_currency)
            VALUES (%s, %s, %s)
        """

        for row in reader:
            cursor.execute(insert_query, row)

        conn.commit()
        print(" CSV data successfully inserted into mycrypto_2.crypto_price.")
