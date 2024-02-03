from datetime import datetime
from flask import jsonify
from src.utils import (
    GET_TRANSACTIONS_BY_PORTFOLIO_DATE_REQUIRED_FIELDS_AND_TYPE,
    generate_missing_field_api_error,
    generate_missing_field_type_api_error,
    GET_TRANSACTIONS_BY_PORTFOLIO_DATE_QUERY,
)


def get_transactions_by_portfolio_date(request, db):
    try:
        data = request.get_json()
        for (
            field_name,
            field_type,
        ) in GET_TRANSACTIONS_BY_PORTFOLIO_DATE_REQUIRED_FIELDS_AND_TYPE:
            if field_name not in data:
                return generate_missing_field_api_error(field_name)
            if not isinstance(data[field_name], field_type):
                return generate_missing_field_type_api_error(field_name, field_type)

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
