from flask import jsonify

DATABASE_FILE_NAME = "sqlDb.db"
OPTION_ENTITY_TYPE_STRING = "option"
REQUIRED_FIELDS_AND_TYPES = [
    ("portfolio_id", str),
    ("txn_type", str),
    ("qty", (int, float)),
    ("price", float),
    ("date", str),
    ("ticker", str),
    ("entity_type", str),
]
REQUIRED_OPTION_FIELDS_AND_TYPES = [
    ("strike", float),
    ("expiry_date", str),
    ("option_type", str),
]
DEFAULT_DATE_STR = "2021-11-23"


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
