from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import io
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

client = MongoClient(os.getenv("MONGO_DB"))
db = client["onetap"]
collection = db["csv_data"]

@app.route('/upload', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    if not file.filename.endswith('.csv'):
        return jsonify({"error": "File must be a CSV"}), 400
    
    try:
        df = pd.read_csv(io.StringIO(file.stream.read().decode("UTF-8")))
        data_json = df.to_dict(orient='records')

        file_metadata = {
            "file_name": file.filename,
            "data": data_json
        }

        collection.insert_one(file_metadata)
        
        return jsonify({"message": "Data uploaded successfully", "file_name": file.filename}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-data', methods=['GET'])
def get_data():
    try:
        data = list(collection.find({}, {"_id": 0}))
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
