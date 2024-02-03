from datetime import datetime
from flask import jsonify, make_response
from src.utils import (
    GET_SNAPSHOT_BY_PORTFOLIO_REQUIRED_FIELDS_AND_TYPES,
    generate_missing_field_type_api_error,
    GET_SNAPSHOT_BY_PORTFOLIO_QUERY,
    GET_SNAPSHOT_BY_PORTFOLIO_WITH_DATE_QUERY,
    validate_fields,
)


def get_snapshot_by_portfolio(request, db):
    try:
        data = request.json
        field_validation_error = validate_fields(
            data, GET_SNAPSHOT_BY_PORTFOLIO_REQUIRED_FIELDS_AND_TYPES
        )
        if field_validation_error:
            return field_validation_error
        portfolio_id = data["portfolio_id"]
        snapshot_date = None

        if "snapshot_date" in data:
            try:
                snapshot_date = datetime.strptime(
                    data["snapshot_date"], "%Y-%m-%d"
                ).date()
            except ValueError:
                return generate_missing_field_type_api_error(
                    "snapshot_date", "YYYY-MM-DD"
                )

        with db:
            cursor = db.cursor()
            row = None
            if snapshot_date is not None:
                cursor.execute(
                    GET_SNAPSHOT_BY_PORTFOLIO_WITH_DATE_QUERY,
                    (portfolio_id, snapshot_date),
                )
            else:
                cursor.execute(
                    GET_SNAPSHOT_BY_PORTFOLIO_QUERY,
                    (portfolio_id,),
                )
            row = cursor.fetchone()

        if row:
            return make_response(jsonify({"data": dict(row)}), 200)
        else:
            return make_response(
                jsonify(
                    {
                        "message": f'Oops, snapshot for portfolio "{portfolio_id}" not found'
                    }
                ),
                404,
            )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
