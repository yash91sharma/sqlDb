from datetime import datetime
from flask import jsonify
import json
from src.utils import (
    OPTION_ENTITY_TYPE_STRING,
    REQUIRED_FIELDS_AND_TYPES,
    REQUIRED_OPTION_FIELDS_AND_TYPES,
    DEFAULT_DATE_STR,
    ADD_TRANSACTION_QUERY,
    generate_missing_field_api_error,
    generate_missing_field_type_api_error,
)


def add_transaction(request, db):
    try:
        data = request.get_json()

        # general transaction field checks
        for field, field_type in REQUIRED_FIELDS_AND_TYPES:
            if field not in data:
                return generate_missing_field_api_error(field)
            if not isinstance(data[field], field_type):
                return generate_missing_field_type_api_error(field, field_type)

        portfolio_id = data["portfolio_id"]
        txn_type = data["txn_type"]
        qty = data["qty"]
        price = data["price"]
        date_str = data["date"]
        ticker = data["ticker"]
        notes = data["notes"] if "notes" in data else ""
        entity_type = data["entity_type"]
        metadata = {
            "notes": notes,
        }

        # defaults for option columns, in case transaction is non-option
        strike = 0
        option_type = ""
        expiry_date_str = DEFAULT_DATE_STR
        expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()

        # Validate date format
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return generate_missing_field_type_api_error("date", "YYYY-MM-DD")

        # option transaction field check
        if entity_type == OPTION_ENTITY_TYPE_STRING:
            for field, field_type in REQUIRED_OPTION_FIELDS_AND_TYPES:
                if field not in data:
                    return generate_missing_field_api_error(field)
                if not isinstance(data[field], field_type):
                    return generate_missing_field_type_api_error(field, field_type)
            strike = data["strike"]
            expiry_date_str = data["expiry_date"]
            option_type = data["option_type"]
            # Validate expiry date format
            try:
                expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
            except ValueError:
                return generate_missing_field_type_api_error(
                    "expiry_date", "YYYY-MM-DD"
                )

        # Insert data into the table using parameterized query
        db.execute(
            ADD_TRANSACTION_QUERY,
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
