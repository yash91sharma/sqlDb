from flask import jsonify, make_response
from src.utils import (
    GET_TRANSACTIONS_BY_PORTFOLIO_DATE_REQUIRED_FIELDS_AND_TYPE,
    generate_missing_field_type_api_error,
    GET_TRANSACTIONS_BY_PORTFOLIO_DATE_QUERY,
    validate_fields,
    convert_str_to_date,
)
import logging

logger = logging.getLogger()


def get_transactions_by_portfolio_date(request, db):
    try:
        data = request.json
        logger.info(
            f'Get transactions by portfolio date request received with fields: "{data}"'
        )
        fields_validation_error = validate_fields(
            data, GET_TRANSACTIONS_BY_PORTFOLIO_DATE_REQUIRED_FIELDS_AND_TYPE
        )
        if fields_validation_error:
            raise Exception(fields_validation_error)

        portfolio_id = data["portfolio_id"]
        start_date_str = data["start_date"]
        end_date_str = data["end_date"]

        # Validate date format
        start_date = convert_str_to_date(start_date_str)
        if start_date is None:
            raise Exception(
                generate_missing_field_type_api_error("start_date", "YYYY-MM-DD")
            )

        # Validate date format
        end_date = convert_str_to_date(end_date_str)
        if end_date is None:
            raise Exception(
                generate_missing_field_type_api_error("end_date", "YYYY-MM-DD")
            )

        # Retrieve data from the table using parameterized query
        with db:
            cursor = db.cursor()
            cursor.execute(
                GET_TRANSACTIONS_BY_PORTFOLIO_DATE_QUERY,
                (portfolio_id, start_date, end_date),
            )
            rows = cursor.fetchall()

        columns = [desc[0] for desc in cursor.description]
        result = {"columns": columns, "rows": [dict(zip(columns, row)) for row in rows]}
        logger.info(f'Success getting transactions for portfolio "{portfolio_id}".')
        return make_response(jsonify(result), 200)
    except Exception as e:
        logger.error("Error getting transactions: ", e)
        return make_response(jsonify({"error": str(e)}), 500)
