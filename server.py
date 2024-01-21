from datetime import datetime
from flask import Flask, request, jsonify, g
import sqlite3

DATABASE = 'sqlDb.db'

app = Flask(__name__)
app.config['DATABASE'] = DATABASE

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'], check_same_thread=False)
        g.db.row_factory = sqlite3.Row
    return g.db

# Function to create the database table
def create_tables():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
          CREATE TABLE IF NOT EXISTS dailyPortfolioValues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolioId TEXT,
            date DATE,
            value FLOAT
          )
        ''')
        db.commit()

create_tables()

@app.route('/insertPortfolioValue', methods=['POST'])
def insert_portfolio_value():
    try:
        data = request.get_json()
        required_fields = ['portfolioId', 'date', 'value']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        portfolio_id = data['portfolioId']
        date_str = data['date']
        value = data['value']

        # Validate date format
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400

        # Insert data into the table using parameterized query
        db = get_db()
        db.execute('INSERT INTO dailyPortfolioValues (portfolioId, date, value) VALUES (?, ?, ?)',
                   (portfolio_id, date, value))
        db.commit()
        return jsonify({'message': 'Data inserted successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/getPortfolioValue', methods=['GET'])
def get_portfolio_value():
    try:
        data = request.get_json()
        required_fields = ['portfolioId', 'date']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        portfolio_id = data['portfolioId']
        date_str = data['date']

        # Validate date format
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format, "YYYY-MM-DD" is required.'}), 400

        # Retrieve data from the table using parameterized query
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM dailyPortfolioValues WHERE portfolioId = ? AND date = ?',
                       (portfolio_id, date))
        result = cursor.fetchone()

        if result:
            query_result = {
                'key': result['id'],
                'data': result['portfolioId'],
                'value': result['value']
            }
            return jsonify(query_result)
        else:
            return jsonify({'message': 'Data not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
  app.run(debug=True, port=12330)
