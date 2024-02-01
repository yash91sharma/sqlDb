from datetime import datetime
import json
from flask import Flask, request, jsonify, g
import sqlite3

DATABASE = "sqlDb.db"

app = Flask(__name__)
app.config["DATABASE"] = DATABASE


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
            txn_type TEXT,
            qty FLOAT,
            price FLOAT,
            date DATE,
            ticker TEXT,
            metadata JSON
          )
        """
        )
        db.commit()


create_tables()


# Used to add a stock or cash transaction to the DB
@app.route("/addTransaction", methods=["POST"])
def add_transaction():
    try:
        data = request.get_json()
        required_fields = ["portfolio_id", "txn_type", "qty", "price", "date", "ticker"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        portfolio_id = data["portfolio_id"]
        txn_type = data["txn_type"]
        qty = data["qty"]
        price = data["price"]
        date_str = data["date"]
        ticker = data["ticker"]
        notes = data["notes"] if "notes" in data else ""
        metadata = {"notes": notes}

        # Validate date format
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return (
                jsonify({"error": 'Invalid date format, "YYYY-MM-DD" is required'}),
                400,
            )

        # Insert data into the table using parameterized query
        db = get_db()
        db.execute(
            "INSERT INTO transactions (portfolio_id, txn_type, qty, price, date, ticker, metadata) VALUES (?,?,?,?,?,?,?)",
            (
                portfolio_id,
                txn_type,
                qty,
                price,
                date_str,
                ticker,
                json.dumps(metadata),
            ),
        )
        db.commit()
        return jsonify({"message": "Data inserted successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/getTransactionsByPortfolioDate", methods=["GET"])
def get_transaction_by_portfolio_date():
    try:
        data = request.get_json()
        required_fields = ["portfolio_id", "date"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        portfolio_id = data["portfolio_id"]
        date_str = data["date"]

        # Validate date format
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return (
                jsonify(
                    {
                        "error": f'Invalid date format, received "{date_str}" but "YYYY-MM-DD" is required.'
                    }
                ),
                400,
            )

        # Retrieve data from the table using parameterized query
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM transactions WHERE portfolio_id = ? AND date = ?",
            (portfolio_id, date),
        )
        rows = cursor.fetchall()

        if rows:
            columns = [desc[0] for desc in cursor.description]
            result = [
                {"columns": columns, "data": [dict(zip(columns, row)) for row in rows]}
            ]
            return jsonify(result)
        else:
            return (
                jsonify(
                    {
                        "message": f'Data for portfolio "{portfolio_id}" for data "{date}" not found'
                    }
                ),
                404,
            )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=12330)
