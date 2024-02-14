from flask import Flask, request, g
import sqlite3
from src.add_transaction import add_transaction
from src.get_transactions_by_portfolio_date import get_transactions_by_portfolio_date
from src.utils import DATABASE_FILE_NAME
from src.create_tables import (
    create_transaction_table,
    create_snapshot_table,
)
from src.add_snapshot import add_snapshot
from src.get_snapshot_by_portfolio import get_snapshot_by_portfolio
from waitress import serve

app = Flask(__name__)
app.config["DATABASE"] = DATABASE_FILE_NAME


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"], check_same_thread=False)
        g.db.row_factory = sqlite3.Row
    return g.db


with app.app_context():
    create_transaction_table(app, get_db())
    create_snapshot_table(app, get_db())


# Used to add any transaction to the DB
@app.route("/addTransaction", methods=["POST"])
def add_transaction_route():
    return add_transaction(request, get_db())


@app.route("/getTransactionsByPortfolioDate", methods=["GET"])
def get_transaction_by_portfolio_date_route():
    return get_transactions_by_portfolio_date(request, get_db())


@app.route("/addSnapshot", methods=["POST"])
def add_snapshot_route():
    return add_snapshot(request, get_db())


@app.route("/getSnapshotByPortfolio", methods=["GET"])
def get_snapshot_by_portfolio_route():
    return get_snapshot_by_portfolio(request, get_db())


if __name__ == "__main__":
    # dev server
    # app.run(debug=True, port=12342)
    serve(app, host="0.0.0.0", port=12342)
