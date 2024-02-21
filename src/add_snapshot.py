from datetime import datetime
from flask import jsonify, make_response
import json
from src.utils import (
    ADD_SNAPSHOT_REQUIRED_ASSETS_FIELDS_AND_TYPES,
    ADD_SNAPSHOT_REQUIRED_FIELDS_AND_TYPES,
    generate_missing_field_api_error,
    generate_missing_field_type_api_error,
    ADD_SNAPSHOT_QUERY,
    validate_fields,
    convert_str_to_date,
    ADD_TRANSACTION_REQUIRED_FIELDS_AND_TYPES,
    ADD_TRANSACTION_REQUIRED_OPTION_FIELDS_AND_TYPES,
)


def add_snapshot(request, db):
    try:
        data = request.json
        fields_validation_error = validate_fields(
            data, ADD_SNAPSHOT_REQUIRED_FIELDS_AND_TYPES
        )
        if fields_validation_error:
            return fields_validation_error
        portfolio_id = data["portfolio_id"]
        snapshot_date_str = data["snapshot_date"]
        value = data["portfolio_value"]
        snapshot_date = convert_str_to_date(snapshot_date_str)
        if snapshot_date is None:
            return generate_missing_field_type_api_error("snapshot_date", "YYYY-MM-DD")

        if "assets" not in data:
            return generate_missing_field_api_error("assets")

        assets = {"cash": 0, "stock": {}, "option": [], "premium":{}}
        request_assets = data["assets"]
        if len(request_assets) > 0:
            asset_fields_validation_error = validate_fields(
                request_assets, ADD_SNAPSHOT_REQUIRED_ASSETS_FIELDS_AND_TYPES
            )
            if asset_fields_validation_error:
                return asset_fields_validation_error
            # should follow 'AAPL': [value, qty, cost_basis]
            for ticker, ticker_values in request_assets["stock"].items():
                if not isinstance(ticker_values, list) or len(ticker_values) != 3:
                    return generate_missing_field_type_api_error(
                        f"values for stock key {ticker}", "list of 3 items"
                    )
                if not all(isinstance(i, (int, float)) for i in ticker_values):
                    return generate_missing_field_type_api_error(
                        f"values for stock key {ticker}", "int or float"
                    )
            for option in request_assets["option"]:
                option_validation_field_error = validate_fields(
                    option,
                    ADD_TRANSACTION_REQUIRED_FIELDS_AND_TYPES
                    + ADD_TRANSACTION_REQUIRED_OPTION_FIELDS_AND_TYPES,
                )
                if option_validation_field_error is not None:
                    return option_validation_field_error
            for _, premium_value in request_assets["premium"].items():
                if not isinstance(premium_value, (int, float)):
                    return generate_missing_field_type_api_error(
                        "premium values", "int or float"
                    )

            # validation is complete, now fetch values from assets
            assets["cash"] = request_assets.get("cash")
            assets["stock"] = request_assets.get("stock")
            assets["option"] = request_assets.get("option")
            assets["premium"] = request_assets.get("premium")

        # TODO: add a check to see if this data already exists in the DB.
        db.execute(
            ADD_SNAPSHOT_QUERY,
            (
                portfolio_id,
                snapshot_date,
                value,
                json.dumps(assets, default=str),
            ),
        )
        db.commit()
        return make_response(
            jsonify({"message": "Snapshot inserted successfully"}), 201
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
