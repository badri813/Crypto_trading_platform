import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pymysql
import pandas as pd
import csv

conn = pymysql.connect(
    user="root",
    host="localhost",
    db="mycrypto_2",
    password="Surya@1271",
    charset="utf8mb4"
)
cursor = conn.cursor()

chrome_driver_path = r"C:\chromedriver-win64\chromedriver-win64\chromedriver.exe"

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

tickers = ["AVAXUSD", "SOLUSD", "ADAUSD", "BTCUSD", "XRPUSD", "ETHUSD", "BNBUSD", "USDTUSD", "DOGEUSD", "DOTUSD"]

all_data = []
ticker_date_info = {}   # store per-ticker from/to

try:
    for ticker in tickers:
        print("\n" + "=" * 80)
        print(f"📊 Fetching news for {ticker}")
        print("=" * 80)

        url_templates = [
            f"https://in.tradingview.com/news-flow/?symbol=BITSTAMP:{ticker}",
            f"https://in.tradingview.com/news-flow/?symbol=CRYPTO:{ticker}"
        ]

        articles_found = False
        container = None

        for url in url_templates:
            driver.get(url)
            time.sleep(3)

            container = driver.execute_script("""
            var els = document.querySelectorAll('div');
            for (var i = 0; i < els.length; i++) {
                var el = els[i];
                if (el.querySelector && el.querySelector('article[data-qa-id="news-headline-card"]')) {
                    if (el.scrollHeight > el.clientHeight) {
                        return el;
                    }
                }
            }
            return null;
            """)

            articles = driver.find_elements(By.CSS_SELECTOR, "article[data-qa-id='news-headline-card']")
            if articles:
                print(f" Found news using URL: {url}")
                articles_found = True
                break
            else:
                print(f" No news found at {url}, trying next fallback...")

        if not articles_found:
            print(f" No articles found for {ticker}, skipping.")
            continue

        seen = set()
        printed_count = 0
        MAX_CARDS = 100
        SLEEP_AFTER_SCROLL = 1.5
        ticker_data = []
        ticker_dates = []

        while printed_count < MAX_CARDS:
            articles = driver.find_elements(By.CSS_SELECTOR, "article[data-qa-id='news-headline-card']")

            for art in articles:
                if printed_count >= MAX_CARDS:
                    break
                try:
                    # Title
                    try:
                        title_elem = art.find_element(By.CSS_SELECTOR, "div[data-qa-id='news-headline-title']")
                        title = title_elem.get_attribute("data-overflow-tooltip-text") or title_elem.text.strip()
                    except:
                        title = "N/A"

                    # Provider
                    try:
                        provider_elem = art.find_element(By.CSS_SELECTOR, "span[class*='provider']")
                        provider = provider_elem.text.strip()
                    except:
                        provider = "N/A"

                    try:
                        try:
                            time_elem = art.find_element(By.TAG_NAME, "relative-time")
                            date_time = time_elem.get_attribute("event-time") or "N/A"
                        except:
                            time_elem = art.find_element(By.TAG_NAME, "time")
                            date_time = time_elem.get_attribute("datetime") or time_elem.text or "N/A"
                    except:
                        date_time = "N/A"

                    key = (title or "").strip() + "||" + (provider or "").strip()
                    if key not in seen:
                        seen.add(key)
                        printed_count += 1

                        row = [ticker, title, provider, date_time]
                        ticker_data.append(row)

                        try:
                            if "GMT" in date_time:
                                parsed = datetime.strptime(date_time, "%a, %d %b %Y %H:%M:%S GMT")
                            else:
                                parsed = datetime.fromisoformat(date_time.replace("Z", "+00:00"))
                            ticker_dates.append(parsed)
                        except:
                            pass

                        print(f"{printed_count}.  Title: {title}")
                        print(f"    Provider: {provider}")
                        print(f"    Date/Time: {date_time}")
                        print("-" * 110)
                except:
                    continue

            if printed_count < MAX_CARDS:
                try:
                    if container:
                        driver.execute_script(
                            "arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].clientHeight;",
                            container
                        )
                    else:
                        driver.execute_script("window.scrollBy(0, window.innerHeight);")
                except:
                    driver.execute_script("window.scrollBy(0, window.innerHeight);")

                time.sleep(SLEEP_AFTER_SCROLL)

        all_data.extend(ticker_data)

        # per-ticker date summary
        if ticker_dates:
            from_date = min(ticker_dates)
            to_date = max(ticker_dates)
            days = (to_date - from_date).days
            ticker_date_info[ticker] = (from_date, to_date, days)

finally:
    driver.quit()

# ---------------- SAVE TO CSV USING PANDAS ----------------
df = pd.DataFrame(all_data, columns=["Ticker", "Title", "Source", "Date/Time"])
csv_filename = "news_data.csv"

# Clean weekday from date (e.g., "Fri, 05 Sep 2025..." -> "05 Sep 2025...")
def clean_datetime(val):
    if isinstance(val, str) and "," in val:
        return val.split(",", 1)[1].strip()
    return val

df["Date/Time"] = df["Date/Time"].apply(clean_datetime)

# ✅ Save to CSV (no backslashes, minimal quotes only when needed)
df.to_csv(
    csv_filename,
    index=False,
    encoding="utf-8-sig",
    quoting=csv.QUOTE_MINIMAL
)

print(f"\n✅ All data saved to {csv_filename} (clean format)")

# Print ticker-wise summaries
print("\n📅 Ticker-wise Date Ranges:\n")
for ticker, (from_date, to_date, days) in ticker_date_info.items():
    print(f"🔹 {ticker}:")
    print(f"   From: {from_date}")
    print(f"   To:   {to_date}")
    print(f"   Range: {days} days\n")

insert_query = """
    INSERT INTO news_data (ticker, title, source, date_time)
    VALUES (%s, %s, %s, %s)
"""

for row in all_data:
    ticker, title, source, date_time = row
    try:
        parsed_date = None
        try:
            if "GMT" in date_time:
                parsed_date = datetime.strptime(date_time, "%a, %d %b %Y %H:%M:%S GMT")
            else:
                parsed_date = datetime.fromisoformat(date_time.replace("Z", "+00:00"))
        except:
            parsed_date = None

        cursor.execute(insert_query, (ticker, title, source, parsed_date))
    except Exception as e:
        print("⚠️ Insert failed:", e)

conn.commit()
print("\n✅ All data inserted into MySQL successfully")


