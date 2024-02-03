from datetime import datetime
from flask import jsonify, make_response
import json
from src.utils import (
    OPTION_ENTITY_TYPE_STRING,
    ADD_TRANSACTION_REQUIRED_FIELDS_AND_TYPES,
    ADD_TRANSACTION_REQUIRED_OPTION_FIELDS_AND_TYPES,
    DEFAULT_DATE_STR,
    ADD_TRANSACTION_QUERY,
    generate_missing_field_type_api_error,
    validate_fields,
)


# TODO: merge entity and option_type. option and call -> option-call
def add_transaction(request, db):
    try:
        data = request.json

        # general transaction field checks
        fields_validation_error = validate_fields(
            data, ADD_TRANSACTION_REQUIRED_FIELDS_AND_TYPES
        )
        if fields_validation_error:
            return fields_validation_error

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
            option_fields_validation_error = validate_fields(
                data, ADD_TRANSACTION_REQUIRED_OPTION_FIELDS_AND_TYPES
            )
            if option_fields_validation_error:
                return option_fields_validation_error
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
        return make_response(
            jsonify({"message": "Transaction inserted successfully"}), 201
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
