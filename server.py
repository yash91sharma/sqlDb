from datetime import datetime
from flask import Flask, request, jsonify, g
import sqlite3
from src.add_transaction import add_transaction
from src.get_transactions_by_portfolio_date import get_transactions_by_portfolio_date
from src.utils import DATABASE_FILE_NAME

app = Flask(__name__)
app.config["DATABASE"] = DATABASE_FILE_NAME


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"], check_same_thread=False)
        g.db.row_factory = sqlite3.Row
    return g.db


# Function to create the database table
def create_tables():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
          CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id TEXT,
            entity_type TEXT,
            txn_type TEXT,
            qty FLOAT,
            price FLOAT,
            date DATE,
            ticker TEXT,
            option_type TEXT,
            expiry_date DATE,
            strike FLOAT,
            metadata JSON
          )
        """
        )
        db.commit()


create_tables()


# Used to add any transaction to the DB
@app.route("/addTransaction", methods=["POST"])
def add_transaction_route():
    return add_transaction(request, get_db())


@app.route("/getTransactionsByPortfolioDate", methods=["GET"])
def get_transaction_by_portfolio_date_route():
    return get_transactions_by_portfolio_date(request, get_db())


if __name__ == "__main__":
    app.run(debug=True, port=12330)
