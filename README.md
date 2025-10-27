
# Crypto Trading Platform 

This project is a web-based **Crypto Trading Platform** prototype designed to fetch real-time or historical cryptocurrency data, perform technical analysis, and visualize the results. It uses Python for data processing and a web framework (Flask) for the user interface.

---

## 🚀 Features

* **Real-Time/Historical Data Fetching:** Utilizes `fetch_data_from_S3.py` to retrieve cryptocurrency data.
* **Data Processing & Technical Analysis:** Calculates technical indicators like the **Relative Strength Index (RSI)** using files like `rsi.py` and `daily_score.py`.
* **Database Integration:** Scripts such as `insert data.py`, `insert_crypto_price_data.py`, and `insert_rsi_csv_data.py` handle data insertion into a SQL database (schema in the `SQL_file` folder).
* **Web Visualization:** Uses `main.py` (likely the main web application file) and `plotting.py` to display data and analysis results via HTML templates (`templates/`) and static assets (`static/`).
* **News Sentiment:** Includes files like `news.py` and CSVs like `news_data.csv` and `today_news.csv`, suggesting a component for fetching and possibly analyzing news sentiment.
* **Message Queuing:** The presence of `producer.py` and `consumer.py` indicates the use of a message queue (e.g., Kafka or RabbitMQ) for asynchronous data handling.

---

## 🛠️ Project Structure

| Folder/File | Description |
| :--- | :--- |
| `main.py` | Main application entry point (likely a Flask/Django app). |
| `producer.py` / `consumer.py` | Scripts for message queue functionality. |
| `daily.py` / `daily_score.py` | Scripts for daily data processing and scoring. |
| `plotting.py` | Code for generating charts and visualizations. |
| `fetch_data_from_S3.py` | Handles data retrieval from an AWS S3 bucket. |
| `insert*.py` | Scripts for inserting processed data into the database. |
| `SQL_file/` | Contains SQL schemas and initial setup files. |
| `templates/` | HTML files for the web interface. |
| `static/` | CSS, JavaScript, and images for the web interface. |
| `*.csv` | Various data files used in the project (e.g., `crypto_data.csv`, `rsi.csv`). |

---

## ⚙️ Getting Started

### Prerequisites

* Python (version 3.8)
* A SQL database (e.g., PostgreSQL, MySQL)
* An AWS account/S3 bucket configured for data fetching (optional, depending on setup)
* A message queue system (Kafka)

### Installation and Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/badri813/Crypto_trading_platform.git](https://github.com/badri813/Crypto_trading_platform.git)
    cd Crypto_trading_platform
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    
    ```
3.  **Database Setup:**
    * Set up your SQL database.
    * Run the schema creation script found in the `SQL_file/` directory.
4.  **Configuration:**
    * Configure database connection strings and AWS credentials in a configuration file (not shown, but likely required).

### Running the Application

1.  Start the message queue **producer** and **consumer** processes.
2.  Run the main application:
    ```bash
    python main.py
    ```
3.  Access the platform in your web browser at `http://127.0.0.1:5000` (default for Flask).

---

## 🤝 Contributing

Feel free to open issues or submit pull requests.
