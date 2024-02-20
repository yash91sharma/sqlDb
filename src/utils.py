from datetime import datetime

DATABASE_FILE_NAME = "data/sqlDb.db"
OPTION_ENTITY_TYPE_STRING = ["option-call", "option-put"]
ADD_TRANSACTION_REQUIRED_FIELDS_AND_TYPES = [
    ("portfolio_id", str),
    ("txn_type", str),
    ("qty", (int, float)),
    ("price", (int, float)),
    ("date", str),
    ("ticker", str),
    ("entity_type", str),
]
ADD_TRANSACTION_REQUIRED_OPTION_FIELDS_AND_TYPES = [
    ("strike", float),
    ("expiry_date", str),
]
DEFAULT_DATE_STR = "2021-11-23"
GET_TRANSACTIONS_BY_PORTFOLIO_DATE_REQUIRED_FIELDS_AND_TYPE = [
    ("portfolio_id", str),
    ("start_date", str),
    ("end_date", str),
]


def generate_missing_field_api_error(field_name):
    return f'Missing "{field_name}" in the input data'


def generate_missing_field_type_api_error(field_name, field_type):
    return f'Field "{field_name}" should be of type "{field_type}"'


ADD_TRANSACTION_QUERY = """
    INSERT INTO transactions (
        portfolio_id,
        txn_type,
        qty, price,
        date, ticker,
        entity_type,
        expiry_date,
        strike,
        metadata
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

GET_TRANSACTIONS_BY_PORTFOLIO_DATE_QUERY = """SELECT * FROM transactions WHERE portfolio_id = ? AND date BETWEEN ? AND ? ORDER BY date ASC, id ASC"""

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
            expiry_date DATE,
            strike FLOAT,
            metadata JSON
          )
        """

CREATE_SNAPSHOT_TABLE_QUERY = """
          CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id TEXT,
            snapshot_date DATE,
            portfolio_value FLOAT,
            assets JSON
          )
        """

ADD_SNAPSHOT_REQUIRED_FIELDS_AND_TYPES = [
    ("portfolio_id", str),
    ("snapshot_date", str),
    ("portfolio_value", float),
]

ADD_SNAPSHOT_REQUIRED_ASSETS_FIELDS_AND_TYPES = [
    ("cash", (float, int)),
    ("stock", dict),
    ("option", list),
]

ADD_SNAPSHOT_QUERY = """
    INSERT INTO snapshots (
        portfolio_id,
        snapshot_date,
        portfolio_value,
        assets
    ) VALUES (?, ?, ?, ?)
"""

GET_SNAPSHOT_BY_PORTFOLIO_REQUIRED_FIELDS_AND_TYPES = [
    ("portfolio_id", str),
]

GET_SNAPSHOT_BY_PORTFOLIO_QUERY = (
    "SELECT * FROM snapshots WHERE portfolio_id = ? ORDER BY snapshot_date DESC LIMIT 1"
)

GET_SNAPSHOT_BY_PORTFOLIO_WITH_DATE_QUERY = """
    SELECT *
    FROM snapshots
    WHERE
        portfolio_id = ? 
        and snapshot_date BETWEEN ? and ?
"""


def validate_fields(data, field_with_types):
    for field_name, field_type in field_with_types:
        if field_name not in data:
            return generate_missing_field_api_error(field_name)
        if not isinstance(data[field_name], field_type):
            return generate_missing_field_type_api_error(field_name, field_type)
    return None


def convert_str_to_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None


TRANSACTION_TXN_TYPE_VALUES = ["sell", "buy", "deposit", "withdraw"]

TRANSACTION_ENTITY_TYPE_VALUES = ["cash", "stock", "option-put", "option-call"]


def generate_invalid_field_api_error(field_name, field_value):
    return f'Transaction field "{field_name}" cannot be "{field_value}".'


def validate_field_value(field_value, field_name, possible_values):
    if field_value not in possible_values:
        return generate_invalid_field_api_error(field_name, field_value)
    return None
