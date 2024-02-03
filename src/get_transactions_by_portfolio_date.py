from datetime import datetime
from flask import jsonify
from src.utils import (
    GET_TRANSACTIONS_BY_PORTFOLIO_DATE_REQUIRED_FIELDS_AND_TYPE,
    generate_missing_field_type_api_error,
    GET_TRANSACTIONS_BY_PORTFOLIO_DATE_QUERY,
    validate_fields,
)


def get_transactions_by_portfolio_date(request, db):
    try:
        data = request.get_json()
        fields_validation_error = validate_fields(
            data, GET_TRANSACTIONS_BY_PORTFOLIO_DATE_REQUIRED_FIELDS_AND_TYPE
        )
        if fields_validation_error:
            return fields_validation_error

        portfolio_id = data["portfolio_id"]
        date_str = data["date"]

        # Validate date format
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return generate_missing_field_type_api_error("date", "YYYY-MM-DD")

        # Retrieve data from the table using parameterized query
        cursor = db.cursor()
        cursor.execute(
            GET_TRANSACTIONS_BY_PORTFOLIO_DATE_QUERY,
            (portfolio_id, date),
        )
        rows = cursor.fetchall()

        if rows:
            columns = [desc[0] for desc in cursor.description]
            result = [
                {"columns": columns, "data": [dict(zip(columns, row)) for row in rows]}
            ]
            return jsonify(result)
        else:
            return (
                jsonify(
                    {
                        "message": f'Data for portfolio "{portfolio_id}" for data "{date}" not found'
                    }
                ),
                404,
            )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
