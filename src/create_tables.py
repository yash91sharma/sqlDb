from src.utils import CREATE_TRANSACTION_TABLE_QUERY


def create_transaction_table(app, db):
    with app.app_context():
        cursor = db.cursor()
        cursor.execute(CREATE_TRANSACTION_TABLE_QUERY)
        db.commit()
