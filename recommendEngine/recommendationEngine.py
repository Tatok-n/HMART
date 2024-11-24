import json

DATA = 'vehicles.json'


def increase_score(score, car):
    """Increase the score of a car based on its VIN."""
    if car['VIN'] in score:
        score[car['VIN']] += 1
    else:
        score[car['VIN']] = 1

def filter_cars(car_data, filters):
    """Filter cars and rank them based on the number of filters they match."""
    score = {}

    for car in car_data:
        for key, value in filters.items():
            car_value = car.get(key)

            # Handle range-based filters
            if isinstance(value, tuple):
                if car_value is not None and value[0] <= car_value <= value[1]:
                    increase_score(score, car)

            # Handle exact matches
            elif car_value == value:
                increase_score(score, car)

    # Sort cars by score in descending order
    ranked_cars = sorted(car_data, key=lambda car: score.get(car['VIN'], 0), reverse=True)
    return ranked_cars, score

def recommend(features):
    """Main function to filter and recommend cars based on user input."""
    # Define ranges
    mileageRange = {"veryLow": (0, 20000), "low": (20001, 40000), "medium": (40001, 60000), "high": (60001, 80000), "veryHigh": (80001, float('inf'))}
    cityRange = {"veryLow": (0, 20), "low": (21, 40), "medium": (41, 60), "high": (61, 80), "veryHigh": (81, float('inf'))}
    highwayRange = {"veryLow": (0, 25), "low": (26, 50), "medium": (51, 75), "high": (76, 100), "veryHigh": (101, float('inf'))}
    priceRange = {"veryLow": (0, 10000), "low": (10001, 25000), "medium": (25001, 50000), "high": (50001, 75000), "veryHigh": (75001, float('inf'))}
    
    # Load JSON data
    with open(DATA, 'r') as file:
        car_data = json.load(file)
        
    # Create filters
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
            
    
    # Filter cars and rank them
    recommended_cars, scores = filter_cars(car_data, filters)
    
    topCars = {}
    
    # Get the top 9 cars
    for car in recommended_cars[:9]:
        topCars[car['VIN']] = ((scores[car['VIN']]/filter_count)*100)
       
    return topCars

if __name__ == "__main__":
    test_features = ['Used', None, 'Toyota', 'Yaris', None, None, None, None, None, None, None, None, None, None, None, None, None, None, '10000']
    print(recommend(test_features))


