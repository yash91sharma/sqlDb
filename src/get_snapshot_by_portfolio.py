from datetime import datetime
from flask import jsonify
from src.utils import (
    GET_SNAPSHOT_BY_PORTFOLIO_REQUIRED_FIELDS_AND_TYPES,
    generate_missing_field_api_error,
    generate_missing_field_type_api_error,
    GET_SNAPSHOT_BY_PORTFOLIO_QUERY,
    GET_SNAPSHOT_BY_PORTFOLIO_WITH_DATE_QUERY,
)


def get_snapshot_by_portfolio(request, db):
    try:
        data = request.get_json()

        for (
            field_name,
            field_type,
        ) in GET_SNAPSHOT_BY_PORTFOLIO_REQUIRED_FIELDS_AND_TYPES:
            if field_name not in data:
                return generate_missing_field_api_error(field_name)
            if not isinstance(data[field_name], field_type):
                return generate_missing_field_type_api_error(field_name, field_type)
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
            return jsonify({"data":dict(row)})
        else:
            return (
                jsonify(
                    {
                        "message": f'Oops, snapshot for portfolio "{portfolio_id}" not found'
                    }
                ),
                404,
            )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
