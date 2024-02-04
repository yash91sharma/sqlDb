from datetime import datetime
from flask import jsonify, make_response
import json
from src.utils import (
    ADD_SNAPSHOT_REQUIRED_ASSETS_FIELDS_AND_TYPES,
    ADD_SNAPSHOT_REQUIRED_FIELDS_AND_TYPES,
    generate_missing_field_api_error,
    generate_missing_field_type_api_error,
    DEFAULT_DATE_STR,
    ADD_SNAPSHOT_QUERY,
    validate_fields,
    convert_str_to_date,
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

        assets = []
        for asset in data["assets"]:
            asset_fields_validation_error = validate_fields(
                asset, ADD_SNAPSHOT_REQUIRED_ASSETS_FIELDS_AND_TYPES
            )
            if asset_fields_validation_error:
                return asset_fields_validation_error
            expiry_date_str = asset["expiry_date"]
            expiry_date = convert_str_to_date(expiry_date_str)
            if expiry_date is None:
                return generate_missing_field_type_api_error(
                    f'expiry_date_str for "{asset["ticker"]}"', "YYYY-MM-DD"
                )
            assets.append(
                {
                    "entity_type": asset["entity_type"],
                    "ticker": asset["ticker"],
                    "value": asset["value"],
                    "qty": asset["qty"],
                    "cost_basis": asset["cost_basis"],
                    "expiry_date": expiry_date,
                }
            )
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
