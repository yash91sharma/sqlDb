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
    convert_str_to_date,
    TRANSACTION_TXN_TYPE_VALUES,
    TRANSACTION_ENTITY_TYPE_VALUES,
    validate_field_value,
)
import logging

logger = logging.getLogger()


def add_transaction(request, db):
    try:
        data = request.json
        logger.info(f"Add transaction request received for with fields: {data}")
        # general transaction field checks
        fields_validation_error = validate_fields(
            data, ADD_TRANSACTION_REQUIRED_FIELDS_AND_TYPES
        )
        if fields_validation_error:
            raise Exception(fields_validation_error)

        portfolio_id = data["portfolio_id"]
        txn_type = data["txn_type"]
        qty = data["qty"]
        price = data["price"]
        date_str = data["date"]
        ticker = data["ticker"]
        entity_type = data["entity_type"]

        txn_type_validation_error = validate_field_value(
            txn_type, "txn_type", TRANSACTION_TXN_TYPE_VALUES
        )
        if txn_type_validation_error is not None:
            raise Exception(txn_type_validation_error)
        entity_type_validation_error = validate_field_value(
            entity_type, "entity_type", TRANSACTION_ENTITY_TYPE_VALUES
        )
        if entity_type_validation_error is not None:
            raise Exception(entity_type_validation_error)
        if txn_type == "sell" and qty >= 0:
            raise Exception("Sell transactions should have negative quantity.")
        if txn_type == "buy" and qty <= 0:
            raise Exception("Buy transactions should have positive quantity.")
        if price < 0:
            raise Exception("Price can not be negative.")
        if entity_type == "cash" and ticker != "$":
            raise Exception("Case transaction should have a '$' ticker.")

        # defaults for option columns, in case transaction is non-option
        strike = 0
        expiry_date_str = DEFAULT_DATE_STR
        expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()

        # Validate date format
        date = convert_str_to_date(date_str)
        if date is None:
            raise Exception(generate_missing_field_type_api_error("date", "YYYY-MM-DD"))

        # option transaction field check
        if entity_type in OPTION_ENTITY_TYPE_STRING:
            option_fields_validation_error = validate_fields(
                data, ADD_TRANSACTION_REQUIRED_OPTION_FIELDS_AND_TYPES
            )
            if option_fields_validation_error:
                raise Exception(option_fields_validation_error)
            strike = data["strike"]
            expiry_date_str = data["expiry_date"]
            # Validate expiry date format
            expiry_date = convert_str_to_date(expiry_date_str)
            if expiry_date is None:
                raise Exception(
                    generate_missing_field_type_api_error("expiry_date", "YYYY-MM-DD")
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
                expiry_date,
                strike,
            ),
        )
        db.commit()
        logger.info(f'Success adding transaction for portfolio "{portfolio_id}"')
        return make_response(
            jsonify({"message": "Transaction inserted successfully"}), 201
        )
    except Exception as e:
        logger.error("Error occured while adding transaction: ", e)
        return make_response(
            jsonify({"error": "Error occured while adding transaction: " + str(e)}),
            500,
        )
