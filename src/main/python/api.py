# api.py
from flask import Flask, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Configuration de la base de données
db_config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'database': 'speed_data_db'
}

def get_speed_data():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM speed_data"
            cursor.execute(query)
            result = cursor.fetchall()
            return result
    except Error as e:
        print(f"Error: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/speed_data', methods=['GET'])
def speed_data():
    data = get_speed_data()
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
