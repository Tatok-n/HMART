from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the CSV file and create a hash map
def create_hash_map(file_path):
    df = pd.read_csv(file_path)
    # Replace NaN with None (to be converted to null in JSON)
    df = df.replace({np.nan: None})
    vin_hash_map = {}
    for _, row in df.iterrows():
        vin = row['VIN']
        vin_hash_map[vin] = row.to_dict()
    return vin_hash_map

vin_hash_map = create_hash_map("vehicles.csv")

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the VIN Lookup API! Use /vehicle?vin=<VIN_NUMBER> to search for a vehicle."})

@app.route('/vehicle', methods=['GET'])
def get_vehicle():
    vin = request.args.get('vin')
    if not vin:
        return jsonify({'error': 'VIN parameter is required'}), 400
    
    vehicle_info = vin_hash_map.get(vin, None)
    if vehicle_info:
        # Ensure all values in 'features' are strings
        vehicle_info['features'] = {key: str(value) for key, value in vehicle_info.items() if key != 'VIN'}
        return jsonify(vehicle_info)
    
    return jsonify({'error': 'Vehicle not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
