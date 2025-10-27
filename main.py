import pymysql
from flask import Flask, request, render_template, redirect, session, jsonify
import pandas as pd
app = Flask(__name__)
admin_username = "admin"
admin_password = "admin"
app.secret_key = "abc"
conn=pymysql.connect(user="root",host="localhost",db="mycrypto_2", password="Surya@1271")
cursor = conn.cursor()
import os
path=os.path.dirname(os.path.abspath(__file__))
image_icon=path+"/static/image_icon"



import pymysql
from pymysql.cursors import DictCursor


@app.route("/")
def index():
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="Surya@1271",
        db="mycrypto_2",
        cursorclass=DictCursor
    )
    cursor = conn.cursor()

    query = """
    SELECT cd.Ticker AS ticker,
           ROUND(cd.Open, 2) AS open,
           FORMAT(cd.Volume, 0) AS volume,
           cd.percentage_change AS percentage_change,
           ss.avg_sentiment_score,
           ss.avg_sentiment_score1,
        
           ii.image_name
    FROM crypto_data cd
    INNER JOIN (
        SELECT Ticker, MAX(Date) AS latest_date
        FROM crypto_data
        GROUP BY Ticker
    ) AS latest
    ON cd.Ticker = latest.Ticker AND cd.Date = latest.latest_date
    LEFT JOIN (
        SELECT REPLACE(ticker, '-', '') AS ticker_clean,
               AVG(avg_sentiment_score) AS avg_sentiment_score,
               AVG(avg_sentiment_score1) AS avg_sentiment_score1
        FROM sentiment_scores
        GROUP BY REPLACE(ticker, '-', '')
    ) ss
    ON REPLACE(cd.Ticker, '-', '') = ss.ticker_clean
    LEFT JOIN image_icon ii 
           ON REPLACE(cd.Ticker, '-', '') = REPLACE(REPLACE(ii.image_name, '.png', ''), '-', '')
    ORDER BY percentage_change DESC;
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    return render_template("index.html", data=rows)


@app.route("/admin_login")
def admin_login():
    return render_template("admin_login.html")


@app.route("/admin_login_action", methods=['post'])
def admin_login_action():
    username = request.form.get("username")
    password = request.form.get("password")
    if username == admin_username and password == admin_password:
        session['role'] = 'admin'
        return redirect("/admin_home")
    else:
        return render_template("/message.html", message="Invalid Login Details")


@app.route("/user_login")
def user_login():
    return render_template("user_login.html")


@app.route("/user_login_action", methods=["POST"])
def user_login_action():
    email = request.form.get("email")
    password = request.form.get("password")
    count = cursor.execute(
        "SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
    if count > 0:
        users = cursor.fetchall()
        if users[0][5] == 'Not verified':
            return render_template("message.html", message="Your Account Not Verified")
        else:
            session['user_id'] = users[0][0]
            session['role'] = 'user'
            return redirect("/user_home")
    else:
        return render_template("message.html", message="Invalid login details")


@app.route("/user_register_action", methods=["POST"])
def user_register_action():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    phone = request.form.get("phone")
    status = 'Not Verified'
    count = cursor.execute("SELECT * FROM users WHERE email = %s AND phone = %s", (email, phone))
    if count > 0:
        return render_template("message.html", message="Duplicate Details Exist")
    else:
        cursor.execute(
            "INSERT INTO users (name, email, password, phone, status) VALUES (%s, %s, %s, %s, %s)",
            (name, email, password, phone, status)
        )
        conn.commit()
        return render_template("message.html", message="User Registration Successful")


@app.route("/admin_home")
def admin_home():
    return render_template("admin_home.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/view_verify_users")
def view_verify_users():
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    return render_template("view_verify_users.html", users=users)


@app.route("/verify_user_acc")
def verify_user():
    user_id = request.args.get("account_id")
    cursor.execute("update users set status='verified' where user_id='"+str(user_id)+"'")
    conn.commit()
    return redirect("/view_verify_users")


@app.route("/de_verify_user_acc")
def de_verify_user():
    user_id = request.args.get("account_id")
    cursor.execute("update users set status='Not verified' where user_id='"+str(user_id)+"'")
    conn.commit()
    return redirect("/view_verify_users")


@app.route("/user_home")
def user_home():
    user_id = session.get("user_id")  # or customer_id based on your model
    cursor.execute("SELECT * FROM crypto_price")
    crypto_prices = cursor.fetchall()

    cursor.execute("SELECT * FROM wallet WHERE user_id = %s", (user_id,))
    wallet_amount = cursor.fetchone()

    return render_template("user_home.html", crypto_prices=crypto_prices, wallet_amount=wallet_amount)


@app.route("/buy")
def buy():
    user_id = session.get("user_id")

    cursor.execute("SELECT * FROM crypto_price")
    crypto_prices = cursor.fetchall()

    cursor.execute("SELECT * FROM wallet WHERE user_id = %s", (user_id,))
    wallet_amount = cursor.fetchone()

    return render_template("buy.html", crypto_prices=crypto_prices, wallet_amount=wallet_amount)




@app.route("/wallet")
def wallet():
    user_id = session['user_id']
    cursor.execute("SELECT * FROM wallet where user_id='"+str(user_id)+"'")
    wallet = cursor.fetchone()
    return render_template("wallet.html",wallet=wallet)


@app.route("/add_amount")
def add_amount():
    return render_template("add_amount.html")


@app.route("/add_amount_action", methods=["GET"])
def add_amount_action():
    user_id = session.get("user_id")
    amount = request.args.get("amount")
    card_number = request.args.get("card_number")
    name_on_card = request.args.get("name_on_card")
    cvv = request.args.get("cvv")
    expiry = request.args.get("expiry")

    if not all([user_id, amount, card_number, name_on_card, cvv, expiry]):
        return "Missing required fields", 400

    cursor = conn.cursor()

    # Check if user already has a wallet record
    cursor.execute("SELECT amount FROM wallet WHERE user_id = %s", (user_id,))
    existing = cursor.fetchone()

    if existing:
        # Update existing amount (add to balance)
        update_query = """
            UPDATE wallet 
            SET amount = amount + %s 
            WHERE user_id = %s
        """
        cursor.execute(update_query, (amount, user_id))
    else:
        # Insert new wallet entry
        insert_query = """
            INSERT INTO wallet (user_id, amount) 
            VALUES (%s, %s)
        """
        cursor.execute(insert_query, (user_id, amount))

    conn.commit()

    return render_template("message_action.html", message="Amount added successfully")



@app.route("/send_to_balance")
def send_to_balance():
    wallet_amount = request.args.get("wallet_amount")
    return render_template("send_to_balance.html",wallet_amount=wallet_amount)



@app.route("/send_to_balance_action")
def send_to_balance_action():
    user_id = session.get("user_id")
    entered_amount = request.args.get("amount")
    cursor.execute("UPDATE wallet SET amount = amount  - '" + str(entered_amount) + "' WHERE user_id='" + str(
        user_id) + "'")
    conn.commit()
    return render_template("message_action.html",message="Amount added Successfully")


@app.route("/buy_coin")
def buy_coin():
    crypto_price_id = request.args.get("crypto_price_id")
    number_of_coins = request.args.get("number_of_coins")
    amount = request.args.get("cost")
    user_id = session['user_id']
    cost =  float(amount)/float(number_of_coins)
    transaction_type = 'buy'
    cursor.execute("insert into transactions(user_id, crypto_price_id, number_of_coins, amount, cost, transaction_type,created_at) values('"+str(user_id)+"', '"+str(crypto_price_id)+"', '"+str(number_of_coins)+"', '"+str(amount)+"', '"+str(cost)+"', '"+str(transaction_type)+"', now())")
    conn.commit()
    cursor.execute("UPDATE wallet SET amount = amount  - '" + str(amount) + "' WHERE user_id='" + str(
        user_id) + "'")
    conn.commit()
    return render_template("message_action.html", message="Coins Bought Successfully")


@app.route("/sell_coin")
def sell_coin():
    crypto_price_id = request.args.get("crypto_price_id")
    number_of_coins = request.args.get("number_of_coins")
    cost = request.args.get("cost")
    user_id = session['user_id']
    amount = float(number_of_coins) * float(cost)
    transaction_type = 'sell'
    cursor.execute("insert into transactions(user_id, crypto_price_id, number_of_coins, amount, cost, transaction_type,created_at) values('"+str(user_id)+"', '"+str(crypto_price_id)+"', '"+str(number_of_coins)+"', '"+str(amount)+"', '"+str(cost)+"', '"+str(transaction_type)+"', now())")
    conn.commit()
    cursor.execute("UPDATE wallet SET amount = amount  + '" + str(amount) + "' WHERE user_id='" + str(
        user_id) + "'")
    conn.commit()
    return render_template("message_action.html", message="Coins Sell Successfully")


@app.route("/transactions")
def transactions():
    user_id = session['user_id']
    print(user_id)
    cursor.execute("select * from transactions where user_id='"+str(user_id)+"'")
    transactions = cursor.fetchall()
    print(transactions)
    return render_template("transactions.html",transactions=transactions,get_crypto_price_by_txn=get_crypto_price_by_txn)


def get_crypto_price_by_txn(crypto_price_id):
    cursor.execute("SELECT * FROM crypto_price WHERE crypto_price_id='" + str(crypto_price_id) + "'")
    return cursor.fetchone()



@app.route("/get_coins")
def get_coins():
    if 'user_id' not in session:
        return {"data": None}

    crypto_price_id = request.args.get("crypto_price_id")
    user_id = session['user_id']

    cursor.execute(
        "SELECT COALESCE(SUM(number_of_coins), 0) FROM transactions WHERE crypto_price_id = %s AND transaction_type = 'buy' AND user_id = %s",
        (crypto_price_id, user_id)
    )
    total_bought = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COALESCE(SUM(number_of_coins), 0) FROM transactions WHERE crypto_price_id = %s AND transaction_type = 'sell' AND user_id = %s",
        (crypto_price_id, user_id)
    )
    total_sold = cursor.fetchone()[0]

    available_coins = total_bought - total_sold

    return {"data": available_coins if available_coins > 0 else None}


from pymysql.cursors import DictCursor

@app.route("/p2p")
def p2p():
    conn = pymysql.connect(
        user="root",
        host="localhost",
        db="mycrypto_2",
        password="Surya@1271",
        cursorclass=DictCursor
    )
    cursor = conn.cursor()

    # get logged in user
    current_user_id = session.get("user_id", None)

    # fetch all P2P orders
    query = """
        SELECT o.order_id, o.user_id, u.name AS user_name, u.email,
               o.ticker, o.price, o.payment_mode, o.status, o.created_at
        FROM p2p_orders o
        JOIN users u ON o.user_id = u.user_id
        ORDER BY o.created_at DESC
    """
    cursor.execute(query)
    all_orders = cursor.fetchall()

    # split into own orders vs others
    user_orders = []
    market_orders = []

    if current_user_id:
        for order in all_orders:
            if order["user_id"] == current_user_id:
                user_orders.append(order)   # show own P2P orders
            else:
                market_orders.append(order) # available for this user to buy
    else:
        market_orders = all_orders  # if not logged in, just show market

    # collect unique tickers for tabs (from market orders)
    tickers = list(set([order["ticker"] for order in market_orders]))

    return render_template(
        "p2p.html",
        tickers=tickers,
        user_orders=user_orders,
        market_orders=market_orders
    )




@app.route("/buy_ticker", methods=["GET", "POST"])
def buy_ticker():
    if "user_id" not in session:
        return redirect("/login")

    transaction_id = request.args.get("transaction_id")
    conn = pymysql.connect(
        user="root",
        host="localhost",
        db="mycrypto_2",
        password="Surya@1271",
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()

    # Fetch transaction details (anyone can see)
    cursor.execute("""
        SELECT t.transaction_id, t.user_id AS seller_id, t.number_of_coins, t.amount, c.ticker, c.current_price
        FROM transactions t
        JOIN crypto_price c ON t.crypto_price_id = c.crypto_price_id
        WHERE t.transaction_id = %s
    """, (transaction_id,))
    tx = cursor.fetchone()

    if not tx:
        return "Transaction not found."

    # Prevent buying own order
    if tx["seller_id"] == session["user_id"]:
        return "❌ You cannot buy your own order."

    if request.method == "POST":
        payment_type = request.form["payment_type"]
        acc_number = request.form["acc_number"]
        buy_cost = float(tx["number_of_coins"]) * float(tx["current_price"])

        # Insert new transaction as 'buy' for current user
        cursor.execute("""
            INSERT INTO transactions (user_id, crypto_price_id, number_of_coins, amount, cost, transaction_type)
            VALUES (%s,
                (SELECT crypto_price_id FROM crypto_price WHERE ticker=%s),
                %s, %s, %s, 'buy')
        """, (session["user_id"], tx["ticker"], tx["number_of_coins"], tx["amount"], buy_cost))

        # Update seller transaction status (mark as sold)
        cursor.execute("UPDATE transactions SET transaction_type='sell' WHERE transaction_id=%s", (transaction_id,))

        # Update wallet if payment_type = wallet
        if payment_type == "wallet":
            cursor.execute("SELECT amount FROM wallet WHERE user_id=%s", (session["user_id"],))
            wallet = cursor.fetchone()
            if wallet:
                new_amount = float(wallet["amount"]) - buy_cost
                cursor.execute("UPDATE wallet SET amount=%s WHERE user_id=%s", (new_amount, session["user_id"]))
            else:
                cursor.execute("INSERT INTO wallet (user_id, amount) VALUES (%s, %s)", (session["user_id"], -buy_cost))

        conn.commit()
        return redirect("/dashboard")

    return render_template("buy_ticker.html", tx=tx)

#

@app.route("/user_profile")
def user_profile():
    user_id = session.get("user_id")
    if not user_id:
        return "User not logged in", 401

    conn = pymysql.connect(
        user="root",
        host="localhost",
        db="mycrypto_2",
        password="Surya@1271",
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()

    # Fetch user details
    cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
    user = cursor.fetchone()

    # Fetch wallet details
    cursor.execute("SELECT * FROM wallet WHERE user_id=%s", (user_id,))
    wallet = cursor.fetchone()

    # Fetch portfolio summary
    cursor.execute("""
        SELECT 
            c.ticker,
            SUM(CASE WHEN t.transaction_type='buy' THEN t.number_of_coins ELSE 0 END) AS total_bought,
            SUM(CASE WHEN t.transaction_type='sell' THEN t.number_of_coins ELSE 0 END) AS total_sold,
            (SUM(CASE WHEN t.transaction_type='buy' THEN t.number_of_coins ELSE 0 END) -
             SUM(CASE WHEN t.transaction_type='sell' THEN t.number_of_coins ELSE 0 END)) AS remaining_coins,
            SUM(CASE WHEN t.transaction_type='buy' THEN t.cost ELSE 0 END) -
            SUM(CASE WHEN t.transaction_type='sell' THEN t.cost ELSE 0 END) AS net_cost,
            (
              (SUM(CASE WHEN t.transaction_type='buy' THEN t.number_of_coins ELSE 0 END) -
               SUM(CASE WHEN t.transaction_type='sell' THEN t.number_of_coins ELSE 0 END))
              * CAST(c.current_price AS DECIMAL(15,8))
            ) AS market_value
        FROM transactions t
        JOIN crypto_price c ON t.crypto_price_id = c.crypto_price_id
        WHERE t.user_id = %s
        GROUP BY c.ticker, c.current_price
        HAVING remaining_coins > 0
    """, (user_id,))
    portfolio = cursor.fetchall()

    # Normalize numeric types & compute total market value
    total_market_value = 0.0

    for row in portfolio:
        row["total_bought"] = float(row["total_bought"] or 0)
        row["total_sold"] = float(row["total_sold"] or 0)
        row["remaining_coins"] = float(row["remaining_coins"] or 0)  # ✅ keep decimals
        row["net_cost"] = float(row["net_cost"] or 0)
        row["market_value"] = float(row["market_value"] or 0)
        total_market_value += row["market_value"]

    # Fetch user P2P orders and remaining coins per ticker
    cursor.execute("""
        SELECT 
            p.order_id, p.ticker, p.price, p.payment_mode, p.status, p.created_at,
            COALESCE(
                (SELECT 
                    SUM(CASE WHEN t.transaction_type='buy' THEN t.number_of_coins ELSE 0 END) - 
                    SUM(CASE WHEN t.transaction_type='sell' THEN t.number_of_coins ELSE 0 END)
                 FROM transactions t
                 JOIN crypto_price c ON t.crypto_price_id = c.crypto_price_id
                 WHERE t.user_id = p.user_id AND c.ticker = p.ticker
                 GROUP BY c.ticker), 
            0) AS coins_available
        FROM p2p_orders p
        WHERE p.user_id = %s
        ORDER BY p.created_at DESC
    """, (user_id,))
    p2p_orders = cursor.fetchall()
    return render_template(
        "user_profile.html",
        user=user,
        wallet=wallet,
        wallet_currency="USD",
        portfolio=portfolio,
        total_market_value=total_market_value,
        p2p_orders=p2p_orders
    )



from decimal import Decimal

@app.route("/sell_p2p", methods=["GET", "POST"])
def sell_p2p():
    current_user_id = session.get("user_id")
    if not current_user_id:
        return redirect("/login")

    conn = pymysql.connect(
        user="root",
        host="localhost",
        db="mycrypto_2",
        password="Surya@1271",
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()

    # Fetch user available tickers (with remaining coins > 0 + latest transaction_id)
    cursor.execute("""
        SELECT 
            c.ticker,
            (SUM(CASE WHEN t.transaction_type='buy' THEN t.number_of_coins ELSE 0 END) -
             SUM(CASE WHEN t.transaction_type='sell' THEN t.number_of_coins ELSE 0 END)) AS remaining_coins,
            MAX(t.transaction_id) AS transaction_id
        FROM transactions t
        JOIN crypto_price c ON t.crypto_price_id = c.crypto_price_id
        WHERE t.user_id = %s
        GROUP BY c.ticker
        HAVING remaining_coins > 0
    """, (current_user_id,))
    portfolio = cursor.fetchall()

    if request.method == "POST":
        ticker = request.form.get("ticker")
        price = request.form.get("price")  # new user-entered price (cost per coin)
        payment_mode = request.form.get("payment_mode")
        transaction_id = request.form.get("transaction_id")

        if not ticker or not price or not payment_mode or not transaction_id:
            return render_template("sell_p2p.html", portfolio=portfolio, message="All fields are required")

        # Fetch seller transaction details
        cursor.execute("""
            SELECT user_id, number_of_coins 
            FROM transactions 
            WHERE transaction_id = %s
        """, (transaction_id,))
        txn = cursor.fetchone()
        if not txn:
            return render_template("sell_p2p.html", portfolio=portfolio, message="Transaction not found")

        seller_id = txn["user_id"]
        number_of_coins = Decimal(str(txn["number_of_coins"]))
        cost = Decimal(str(price))
        amount = number_of_coins * cost  # total price for buyer

        # --- Case 1: Seller creating order ---
        if current_user_id == seller_id:
            # Update transaction to p2p-sell
            cursor.execute("""
                UPDATE transactions
                SET cost = %s,
                    amount = %s,
                    transaction_type = 'p2p-sell'
                WHERE transaction_id = %s
            """, (cost, amount, transaction_id))

            # Insert into P2P Orders
            cursor.execute("""
                INSERT INTO p2p_orders (user_id, ticker, price, payment_mode, status, transaction_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (seller_id, ticker, cost, payment_mode, "pending", transaction_id))

            conn.commit()
            return render_template("sell_p2p.html", portfolio=portfolio, message="Sell order placed successfully!")

        # --- Case 2: Buyer purchasing ---
        else:
            # Deduct buyer wallet balance
            cursor.execute("SELECT amount FROM wallet WHERE user_id = %s", (current_user_id,))
            buyer_wallet = cursor.fetchone()

            if not buyer_wallet or Decimal(buyer_wallet["amount"]) < amount:
                return render_template("sell_p2p.html", portfolio=portfolio, message="Insufficient balance")

            new_buyer_balance = Decimal(buyer_wallet["amount"]) - amount
            cursor.execute("UPDATE wallet SET amount = %s WHERE user_id = %s", (new_buyer_balance, current_user_id))

            # If payment_mode = Wallet → Credit seller
            if payment_mode == "Wallet":
                cursor.execute("SELECT amount FROM wallet WHERE user_id = %s", (seller_id,))
                seller_wallet = cursor.fetchone()
                seller_balance = Decimal(seller_wallet["amount"]) if seller_wallet else Decimal("0")
                new_seller_balance = seller_balance + amount

                # Insert or update seller wallet
                if seller_wallet:
                    cursor.execute("UPDATE wallet SET amount = %s WHERE user_id = %s", (new_seller_balance, seller_id))
                else:
                    cursor.execute("INSERT INTO wallet (user_id, amount) VALUES (%s, %s)", (seller_id, new_seller_balance))

            # Update transaction to 'buy'
            cursor.execute("""
                UPDATE transactions
                SET transaction_type = 'buy'
                WHERE transaction_id = %s
            """, (transaction_id,))

            # Mark order completed
            cursor.execute("""
                UPDATE p2p_orders
                SET status = 'completed'
                WHERE transaction_id = %s
            """, (transaction_id,))

            conn.commit()
            return render_template("sell_p2p.html", portfolio=portfolio, message="Purchase successful!")

    return render_template("sell_p2p.html", portfolio=portfolio)



@app.route("/swap", methods=["GET", "POST"])
def swap():
    user_id = session['user_id']
    conn = pymysql.connect(
        host="localhost",
        user="root",
        db="mycrypto_2",
        password="Surya@1271",
        cursorclass=DictCursor
    )
    cursor = conn.cursor()

    # Get owned coins (net available = buys - sells)
    cursor.execute("""
        SELECT 
            t.crypto_price_id,
            SUM(CASE WHEN t.transaction_type = 'buy' THEN t.number_of_coins ELSE 0 END) -
            SUM(CASE WHEN t.transaction_type = 'sell' THEN t.number_of_coins ELSE 0 END) AS total,
            c.ticker,
            c.current_price,
            c.fiat_currency
        FROM transactions t
        JOIN crypto_price c ON c.crypto_price_id = t.crypto_price_id
        WHERE t.user_id = %s
        GROUP BY t.crypto_price_id, c.ticker, c.current_price, c.fiat_currency
        HAVING total > 0
    """, (user_id,))
    owned_coins = cursor.fetchall()

    # Get all coins (for swap target)
    cursor.execute("SELECT * FROM crypto_price")
    coins = cursor.fetchall()

    # Default values
    selected_from = None
    selected_qty = 0
    selected_price = 0

    if request.method == "POST":
        selected_from = int(request.form.get("from_coin"))
        for c in owned_coins:
            if c["crypto_price_id"] == selected_from:
                selected_qty = c["total"]
                selected_price = float(c["current_price"])

    return render_template(
        "swap.html",
        owned_coins=owned_coins,
        coins=coins,
        selected_from=selected_from,
        selected_qty=selected_qty,
        selected_price=selected_price
    )


from decimal import Decimal

@app.route("/swap_action", methods=["POST"])
def swap_action():
    user_id = 1  # later from session

    from_coin_id = int(request.form.get("from_coin"))
    to_coin_id = int(request.form.get("to_coin"))

    from_qty = Decimal(request.form.get("from_qty") or "0")
    from_price = Decimal(request.form.get("from_price") or "0")
    to_price = Decimal(request.form.get("to_price") or "0")

    if from_qty <= 0 or from_price <= 0 or to_price <= 0:
        return "Invalid swap request", 400

    # calculate with decimals
    old_value = from_qty * from_price
    new_qty = old_value / to_price

    conn = pymysql.connect(
        host="localhost",
        user="root",
        db="mycrypto_2",
        password="Surya@1271",
        cursorclass=DictCursor
    )
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE transactions
        SET crypto_price_id = %s,
            number_of_coins = %s,
            amount = %s,
            cost = %s
        WHERE user_id = %s
        AND crypto_price_id = %s
        AND transaction_type = 'buy'
        LIMIT 1
    """, (to_coin_id, str(new_qty), str(old_value), str(to_price), user_id, from_coin_id))

    conn.commit()

    message = f"Swapped successfully! New {new_qty:.8f} coins of ID {to_coin_id}"

    return render_template("message_action.html", message=message)


from pymysql.cursors import DictCursor

def get_db_connection():
    return pymysql.connect(
        user="root",
        host="localhost",
        db="mycrypto_2",
        password="Surya@1271",
        cursorclass=DictCursor
    )

def get_user_balance(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT user_id,
               SUM(CASE WHEN transaction_type IN ('buy','p2p-buy') THEN amount ELSE 0 END) -
               SUM(CASE WHEN transaction_type IN ('sell','p2p-sell','p2p-sell') THEN amount ELSE 0 END) AS balance
        FROM transactions
        WHERE user_id = %s
        GROUP BY user_id
    """
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()

    return float(result["balance"]) if result and result["balance"] is not None else 0.0



from pymysql.cursors import DictCursor
from decimal import Decimal
from flask import session, request, render_template

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        db="mycrypto_2",
        password="Surya@1271",
        cursorclass=DictCursor,
        autocommit=False
    )

def ensure_wallet(cursor, user_id):
    cursor.execute("SELECT amount FROM wallet WHERE user_id=%s", (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO wallet (user_id, amount) VALUES (%s, %s)", (user_id, "0"))

def get_user_balance(cursor, user_id) -> Decimal:
    cursor.execute("SELECT amount FROM wallet WHERE user_id=%s", (user_id,))
    row = cursor.fetchone()
    return Decimal(str(row["amount"])) if row and row["amount"] is not None else Decimal("0")


@app.route("/buy_p2p/<int:order_id>", methods=["GET", "POST"])
def buy_p2p(order_id):
    user_id = session.get("user_id")
    if not user_id:
        return "User not logged in", 401

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Load order
        cursor.execute("SELECT * FROM p2p_orders WHERE order_id=%s", (order_id,))
        order = cursor.fetchone()
        if not order:
            return "Order not found", 404

        # Prevent buying own order
        if order["user_id"] == user_id:
            return "You cannot buy your own order", 400

        if request.method == "GET":
            # Just show UI form for payment
            return render_template("p2p_transaction.html", order=order)

        # POST = confirm purchase
        payment_mode = order["payment_mode"]
        price = Decimal(str(order["price"]))
        seller_id = order["user_id"]
        ticker = order["ticker"]

        # ✅ Ensure wallets exist
        ensure_wallet(cursor, user_id)
        ensure_wallet(cursor, seller_id)

        # ✅ Resolve crypto_price_id from ticker
        cursor.execute("SELECT crypto_price_id FROM crypto_price WHERE ticker=%s LIMIT 1", (ticker,))
        cp = cursor.fetchone()
        crypto_price_id = cp["crypto_price_id"] if cp else None

        # ✅ Check buyer balance
        buyer_balance = get_user_balance(cursor, user_id)
        if payment_mode == "Wallet" and buyer_balance < price:
            return "Insufficient wallet balance", 400

        # 🔹 Wallet mode: update balances + log transactions
        if payment_mode == "Wallet":
            cursor.execute(
                "UPDATE wallet SET amount = CAST(amount AS DECIMAL(18,8)) - %s WHERE user_id=%s",
                (price, user_id)
            )
            cursor.execute(
                "UPDATE wallet SET amount = CAST(amount AS DECIMAL(18,8)) + %s WHERE user_id=%s",
                (price, seller_id)
            )

            cursor.execute("""
                INSERT INTO transactions (user_id, crypto_price_id, number_of_coins, amount, cost, transaction_type)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, crypto_price_id, 1, price, price, "buy"))

            cursor.execute("""
                INSERT INTO transactions (user_id, crypto_price_id, number_of_coins, amount, cost, transaction_type)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (seller_id, crypto_price_id, 1, price, price, "p2p-sell"))

        # 🔹 Bank mode: only log buyer’s transaction
        elif payment_mode == "Bank":
            cursor.execute("""
                INSERT INTO transactions (user_id, crypto_price_id, number_of_coins, amount, cost, transaction_type)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, crypto_price_id, 1, price, price, "buy"))

        # ✅ Remove order from P2P table
        cursor.execute("DELETE FROM p2p_orders WHERE order_id=%s", (order_id,))

        conn.commit()
        return render_template("message_action2.html", message="P2P Transaction successful")

    except Exception as e:
        conn.rollback()
        return f"Error: {e}", 500


from datetime import datetime

def timeago(value):
    if not value:
        return "N/A"
    now = datetime.utcnow()
    diff = now - value

    seconds = diff.total_seconds()
    minutes = int(seconds // 60)
    hours = int(seconds // 3600)
    days = int(seconds // 86400)

    if seconds < 60:
        return f"{int(seconds)} sec ago"
    elif minutes < 60:
        return f"{minutes} min ago"
    elif hours < 24:
        return f"{hours} hr ago"
    elif days < 30:
        return f"{days} day{'s' if days > 1 else ''} ago"
    else:
        return value.strftime("%Y-%m-%d")

# Register filter
app.jinja_env.filters['timeago'] = timeago
@app.route("/news")
def news():
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # Fetch distinct tickers for dropdown
    cursor.execute("SELECT DISTINCT ticker FROM news_data ORDER BY ticker")
    tickers = [row["ticker"] for row in cursor.fetchall()]

    # Get selected ticker from query params
    selected_ticker = request.args.get("ticker")

    if selected_ticker:
        cursor.execute("""
            SELECT ticker, title, source, date_time 
            FROM news_data 
            WHERE ticker = %s
            ORDER BY date_time DESC
        """, (selected_ticker,))
    else:
        cursor.execute("""
            SELECT ticker, title, source, date_time 
            FROM news_data 
            ORDER BY date_time DESC
        """)
    news_data = cursor.fetchall()

    return render_template("news.html",
                           tickers=tickers,
                           selected_ticker=selected_ticker,
                           news_data=news_data)


def get_connection():
    return pymysql.connect(
        user="root",
        host="localhost",
        db="mycrypto_2",
        password="Surya@1271"
    )


@app.route("/upload_image")
def upload_image():
    return render_template("upload_image.html")

@app.route("/upload_image_action", methods=["POST"])
def upload_image_action():
    if "file" not in request.files:
        return "No file uploaded"
    file = request.files["file"]

    if file.filename == "":
        return "No file selected"

    # Save file to static folder
    file_path = os.path.join(image_icon, file.filename)
    file.save(file_path)

    # Insert only image name into DB
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO image_icon (image_name) VALUES (%s)", (file.filename,))
    conn.commit()
    return render_template("message_action3.html",message="Image uploaded successfully ✅")


@app.route("/rsi_chart")
def rsi_chart():
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    import pymysql

    # --- Load data ---
    csv_path = r"C:\Users\Owner\PycharmProjects\Crypto\rsi.csv"
    df = pd.read_csv(csv_path)

    # --- Ensure Date is datetime ---
    df["Date"] = pd.to_datetime(df["Date"])

    # --- Filter for past 7 days ---
    latest_date = df["Date"].max()
    one_week_ago = latest_date - pd.Timedelta(days=7)
    df_week = df[df["Date"] >= one_week_ago]

    print(f"Showing RSI data from {one_week_ago.date()} to {latest_date.date()}")

    # --- Create main scatter plot ---
    fig = px.scatter(
        df_week,
        x="Date",
        y="RSI",
        color="RSI",
        text="Ticker",
        color_continuous_scale="RdYlGn_r",
        title=f"RSI Heatmap (Past Week: {one_week_ago.date()} → {latest_date.date()})",
        hover_data={"RSI":":.2f","Date":True,"Ticker":True},
        template="plotly_dark"
    )

    # --- Reference lines ---
    fig.add_hline(y=70, line_dash="dash", line_color="red")
    fig.add_hline(y=30, line_dash="dash", line_color="green")

    # --- Legend entries ---
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='lines',
        line=dict(color='red', dash='dash'),
        name='Overbought (70)'
    ))
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='lines',
        line=dict(color='green', dash='dash'),
        name='Oversold (30)'
    ))

    # --- Trace formatting ---
    fig.update_traces(
        textposition="top center",
        textfont_size=11,
        marker=dict(size=14, opacity=0.8, line=dict(width=1, color="white"))
    )

    # --- Axis & layout tweaks ---
    fig.update_yaxes(range=[-5, 105], title="RSI")
    fig.update_xaxes(title="Date")

    fig.update_layout(
        height=800,
        width=800,
        margin=dict(l=60, r=60, t=70, b=60),
        legend=dict(
            title="Reference Levels",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # --- Convert figure to HTML ---
    graph_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    # --- Fetch summary data from MySQL ---
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM rsi_summary")
    summary_data = cursor.fetchall()

    # --- Render template ---
    return render_template(
        "rsi_template.html",
        graph_html=graph_html,
        summary_data=summary_data
    )
if __name__ == "__main__":
    app.run(debug=True)


