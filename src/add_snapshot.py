from datetime import datetime
from flask import jsonify
import json

def add_snapshot(request, db):
    try:
        data = request.get_json()
        print(data)
        return jsonify({"message": "Snapshot inserted successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500