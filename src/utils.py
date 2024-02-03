from flask import jsonify

DATABASE_FILE_NAME = "sqlDb.db"
OPTION_ENTITY_TYPE_STRING = "option"
ADD_TRANSACTION_REQUIRED_FIELDS_AND_TYPES = [
    ("portfolio_id", str),
    ("txn_type", str),
    ("qty", (int, float)),
    ("price", float),
    ("date", str),
    ("ticker", str),
    ("entity_type", str),
]
ADD_TRANSACTION_REQUIRED_OPTION_FIELDS_AND_TYPES = [
    ("strike", float),
    ("expiry_date", str),
    ("option_type", str),
]
DEFAULT_DATE_STR = "2021-11-23"
GET_TRANSACTIONS_BY_PORTFOLIO_DATE_REQUIRED_FIELDS_AND_TYPE = [
    ("portfolio_id", str),
    ("date", str),
]


def generate_missing_field_api_error(field_name):
    return jsonify({"error": f'Missing "{field_name}" in the input data'}), 400


def generate_missing_field_type_api_error(field_name, field_type):
    return (
        jsonify({"error": f'Field "{field_name}" should be of type "{field_type}"'}),
        400,
    )


ADD_TRANSACTION_QUERY = """
    INSERT INTO transactions (
        portfolio_id,
        txn_type,
        qty, price,
        date, ticker,
        entity_type,
        option_type,
        expiry_date,
        strike,
        metadata
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

GET_TRANSACTIONS_BY_PORTFOLIO_DATE_QUERY = (
    "SELECT * FROM transactions WHERE portfolio_id = ? AND date = ?"
)

CREATE_TRANSACTION_TABLE_QUERY = """
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

CREATE_SNAPSHOT_TABLE_QUERY = """
          CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id TEXT,
            entity_type TEXT,
            ticker TEXT,
            qty FLOAT,
            value FLOAT,
            cost_basis FLOAT,
            option_type TEXT,
            expiry_date DATE,
            snapshot_date DATE,
            strike FLOAT
          )
        """

ADD_TRANSACTION_REQUIRED_FIELDS_AND_TYPES = [
    ("portfolio_id", str),
    ("entity_type", str),
    ("ticker", str),
    ("qty", (int, float)),
    ("value", float),
    ("cost_basis",float),
    ("snapshot_date", str),
    
    
]