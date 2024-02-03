from datetime import datetime
import json
from flask import Flask, request, jsonify, g
import sqlite3

DATABASE = "sqlDb.db"
OPTION_ENTITY_TYPE_STRING = "option"

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


# Used to add a stock or cash transaction to the DB
@app.route("/addTransaction", methods=["POST"])
def add_transaction():
    try:
        data = request.get_json()
        required_fields = [
            ("portfolio_id", str),
            ("txn_type", str),
            ("qty", (int, float)),
            ("price", float),
            ("date", str),
            ("ticker", str),
            ("entity_type", str),
        ]
        for field, field_type in required_fields:
            if field not in data:
                return jsonify({"error": f'Missing "{field}" in the input data'}), 400
            if not isinstance(data[field], field_type):
                return (
                    jsonify(
                        {"error": f'Field "{field}" should be of type "{field_type}"'}
                    ),
                    400,
                )

        portfolio_id = data["portfolio_id"]
        txn_type = data["txn_type"]
        qty = data["qty"]
        price = data["price"]
        date_str = data["date"]
        ticker = data["ticker"]
        entity_type = data["entity_type"]
        notes = data["notes"] if "notes" in data else ""
        strike = 0
        expiry_date_str = "2023-01-01"
        expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
        option_type = ""
        if entity_type == OPTION_ENTITY_TYPE_STRING:
            required_option_fields = [
                ("strike", float),
                ("expiry_date", str),
                ("option_type", str),
            ]
            for field, field_type in required_option_fields:
                if field not in data:
                    return (
                        jsonify(
                            {
                                "error": f'Missing "{field}" in the input data for options transaction'
                            }
                        ),
                        400,
                    )
                if not isinstance(data[field], field_type):
                    return (
                        jsonify(
                            {
                                "error": f'Field "{field}" should be of type "{field_type}"'
                            }
                        ),
                        400,
                    )
            strike = data["strike"]
            expiry_date_str = data["expiry_date"]
            option_type = data["option_type"]
            # Validate expiry date format
            try:
                expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
            except ValueError:
                return (
                    jsonify({"error": 'Invalid date format, "YYYY-MM-DD" is required'}),
                    400,
                )
        metadata = {
            "notes": notes,
        }

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
            "INSERT INTO transactions (portfolio_id, txn_type, qty, price, date, ticker, entity_type,option_type,expiry_date,strike, metadata ) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                portfolio_id,
                txn_type,
                qty,
                price,
                date,
                ticker,
                entity_type,
                option_type,
                expiry_date,
                strike,
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
