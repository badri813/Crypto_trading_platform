import torch
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pymysql

# Database connection
conn = pymysql.connect(
    user="root",
    host="localhost",
    db="mycrypto_2",
    password="Surya@1271"
)
cursor = conn.cursor()

# Load CryptoBERT model
MODEL_NAME = "ElKulako/cryptobert"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

labels = ["Bearish", "Neutral", "Bullish"]

def get_sentiment_score(texts):
    inputs = tokenizer(texts, padding=True, truncation=True, max_length=128, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)

    scores = []
    for p in probs:
        # Weighted score: Bearish=-1, Neutral=0, Bullish=1
        score = p[0].item() * -1 + p[1].item() * 0 + p[2].item() * 1
        scores.append(score)

    return scores

print('reading data........')
df=pd.read_csv('news_data.csv')
df2=pd.read_csv('news_data_3days.csv')
df2.dropna(inplace=True)
df.dropna(inplace=True)

# Get sentiment scores for each headline
df["sentiment_score"] = get_sentiment_score(df["Title"].tolist())
df2["sentiment_score"] = get_sentiment_score(df2["Title"].tolist())
print('calculating scores')
#print(df.describe())
#print(df2.describe())
# Average sentiment score per coin
#avg_scores1=df.groupby("Ticker")["sentiment_score"].
avg_scores = df.groupby("Ticker")["sentiment_score"].mean().reset_index()
avg_scores.rename(columns={"sentiment_score": "avg_sentiment_score"}, inplace=True)
print(avg_scores)
avg_scores1 = df2.groupby("Ticker")["sentiment_score"].mean().reset_index()
avg_scores1.rename(columns={"sentiment_score": "avg_sentiment_score1"}, inplace=True)

# Print table
print(avg_scores)
print(avg_scores1)

insert_query = """
    INSERT INTO sentiment_scores (ticker, avg_sentiment_score, avg_sentiment_score1)
    VALUES (%s, %s, %s)
"""

avg_scores_a=pd.merge(avg_scores, avg_scores1, on="Ticker")
print(avg_scores_a)
for _, row in avg_scores_a.iterrows():
    cursor.execute(insert_query, (row["Ticker"], row["avg_sentiment_score"],  row["avg_sentiment_score1"]))



conn.commit()

print("Sentiment scores inserted into database successfully")

