from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

DATA = 'vehicles.json'


def increase_score(score, car):
    if car['VIN'] in score:
        score[car['VIN']] += 1
    else:
        score[car['VIN']] = 1


def filter_cars(car_data, filters):
    score = {}
    for car in car_data:
        for key, value in filters.items():
            car_value = car.get(key)
            if isinstance(value, tuple):
                if car_value is not None and value[0] <= car_value <= value[1]:
                    increase_score(score, car)
            elif car_value == value:
                increase_score(score, car)
    ranked_cars = sorted(car_data, key=lambda car: score.get(car['VIN'], 0), reverse=True)
    return ranked_cars, score


def recommend(features):
    mileageRange = {"veryLow": (0, 20000), "low": (20001, 40000), "medium": (40001, 60000), "high": (60001, 80000), "veryHigh": (80001, float('inf'))}
    cityRange = {"veryLow": (0, 20), "low": (21, 40), "medium": (41, 60), "high": (61, 80), "veryHigh": (81, float('inf'))}
    highwayRange = {"veryLow": (0, 25), "low": (26, 50), "medium": (51, 75), "high": (76, 100), "veryHigh": (101, float('inf'))}
    priceRange = {"veryLow": (0, 10000), "low": (10001, 25000), "medium": (25001, 50000), "high": (50001, 75000), "veryHigh": (75001, float('inf'))}

    with open(DATA, 'r') as file:
        car_data = json.load(file)

    filters = {}
    keys = [
        "Type", "Year", "Make", "Model", "Body", "Doors",
        "Ext_Color_Generic", "Int_Color_Generic", "EngineCylinders",
        "Transmission", "Engine_Block_Type", "Engine_Description",
        "Fuel_Type", "Drivetrain", "MarketClass", "PassengerCapacity",
        "Miles", "CityMPG", "HighwayMPG", "SellingPrice"
    ]
    ranges = {
        "Miles": mileageRange,
        "CityMPG": cityRange,
        "HighwayMPG": highwayRange,
        "SellingPrice": priceRange
    }
    intList = ["Year", "Doors", "EngineCylinders", "Miles", "SellingPrice", "CityMPG", "HighwayMPG", "PassengerCapacity"]
    filter_count = 0

    for idx, value in enumerate(features):
        if value is not None:
            filter_count += 1
            if keys[idx] in ranges:
                filters[keys[idx]] = ranges[keys[idx]].get(value, None)
            else:
                filters[keys[idx]] = int(value) if keys[idx] in intList else value

    recommended_cars, scores = filter_cars(car_data, filters)
    topCars = {}
    for car in recommended_cars[:6]:
        topCars[car['VIN']] = ((scores[car['VIN']] / filter_count) * 100)

    return topCars


@app.route('/recommend', methods=['GET'])
def recommend_api():
    test_features = ['Used', None, 'Toyota', 'Yaris', None, None, None, None, None, None, None, None, None, None, None, None, None, None, '10000']
    recommendations = recommend(test_features)
    return jsonify(list(recommendations.keys()))

@app.route('/vehicle', methods=['GET'])
def get_vehicle():
    """Fetch details for a specific VIN."""
    vin = request.args.get('vin')  # Get VIN from query parameter

    # Load vehicles data
    try:
        with open(DATA, 'r') as file:
            car_data = json.load(file)
    except FileNotFoundError:
        return jsonify({"error": "Vehicle data not found"}), 500

    # Search for the car by VIN
    for car in car_data:
        if car['VIN'] == vin:
            return jsonify(car)  # Return car details if VIN matches

    # Return a 404 error if VIN not found
    return jsonify({"error": "Vehicle not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
 