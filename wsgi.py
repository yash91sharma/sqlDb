from sql_db_server import app
import gunicorn  # pylint: disable=unused-import

if __name__ == "__main__":
    app.run()