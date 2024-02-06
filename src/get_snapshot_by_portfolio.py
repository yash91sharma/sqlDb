from flask import jsonify, make_response
from src.utils import (
    GET_SNAPSHOT_BY_PORTFOLIO_REQUIRED_FIELDS_AND_TYPES,
    generate_missing_field_type_api_error,
    GET_SNAPSHOT_BY_PORTFOLIO_QUERY,
    GET_SNAPSHOT_BY_PORTFOLIO_WITH_DATE_QUERY,
    validate_fields,
    convert_str_to_date,
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
        start_date = None
        end_date = None

        # If the request has start and end date, then fetch them.
        # Return errors if the dates are not in the correct format.
        if "start_date" in data and "end_date" in data:
            start_date = convert_str_to_date(data["start_date"])
            if start_date is None:
                return generate_missing_field_type_api_error("start_date", "YYYY-MM-DD")
            end_date = convert_str_to_date(data["end_date"])
            if end_date is None:
                return generate_missing_field_type_api_error("end_date", "YYYY-MM-DD")

        # Run the query based on input params.
        with db:
            cursor = db.cursor()
            rows = None
            if start_date is not None and end_date is not None:
                cursor.execute(
                    GET_SNAPSHOT_BY_PORTFOLIO_WITH_DATE_QUERY,
                    (portfolio_id, start_date, end_date),
                )
            else:
                cursor.execute(
                    GET_SNAPSHOT_BY_PORTFOLIO_QUERY,
                    (portfolio_id,),
                )

        rows = cursor.fetchall()
        if rows:
            columns = [desc[0] for desc in cursor.description]
            response = {
                "columns": columns,
                "rows": [dict(zip(columns, row)) for row in rows],
            }
            return make_response(jsonify(response), 200)
        return make_response(
            jsonify(
                {"message": f'Oops, snapshot for portfolio "{portfolio_id}" not found'}
            ),
            404,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
