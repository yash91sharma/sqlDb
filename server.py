from datetime import datetime
from flask import Flask, request, jsonify
import sqlite3
import atexit

DATABASE = 'sqlDb.db'

app = Flask(__name__)

# Function to create the database table
conn = sqlite3.connect(DATABASE , check_same_thread=False)
cursor = conn.cursor()
# cursor.execute("DROP TABLE IF EXISTS dailyPortfolioValues;")
cursor.execute('''
  CREATE TABLE IF NOT EXISTS dailyPortfolioValues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolioId TEXT,
    date DATE,
    value FLOAT
  )
''')
conn.commit()

# Route to insert data
@app.route('/insertPortfolioValue', methods=['POST'])
def insert_data():
  data = request.get_json()

  portfolioId = data['portfolioId']
  date = datetime.strptime(data['date'], '%Y-%m-%d').date()
  value = data['value']

  # Insert data into the table
  cursor.execute('INSERT INTO dailyPortfolioValues (portfolioId, date, value) VALUES (?, ?, ?)',
                 (portfolioId, date, value))
  conn.commit()
  return jsonify({'message': 'Data inserted successfully'}), 201

# Route to retrieve data
@app.route('/getPortfolioValue', methods=['GET'])
def retrieve_data():
  data = request.get_json()
  portfolioId = data['portfolioId']
  date = datetime.strptime(data['date'], '%Y-%m-%d').date()

  cursor.execute('SELECT * FROM dailyPortfolioValues WHERE portfolioId = ? AND date = ?',
                 (portfolioId,date))
  result = cursor.fetchone()

  if result:
    queryResult = {
        'key': result[0],
        'data': result[1],
        'value': result[2]
    }
    return jsonify(queryResult)
  else:
    return jsonify({'message': 'Data not found'}), 404

# Register a function to close the connection when the server shuts down
def close_connection():
  if conn is not None:
    conn.close()

atexit.register(close_connection)

if __name__ == '__main__':
    app.run(debug=True, port=12330)