import pandas as pd

def filter_cars(data, filters):
    """
    Filters the dataset based on user input criteria.

    Args:
        data (pd.DataFrame): The car dataset.
        filters (dict): A dictionary of criteria to filter the data.
    
    Returns:
        pd.DataFrame: Filtered dataset.
    """
    filtered_data = data.copy()
    
    # Apply filters
    for column, value in filters.items():
        if value is not None:
            if isinstance(value, (list, tuple)):  # Range filters
                filtered_data = filtered_data[
                    (filtered_data[column] >= value[0]) & (filtered_data[column] <= value[1])
                ]
            else:  # Exact match filters
                filtered_data = filtered_data[filtered_data[column] == value]
    
    return filtered_data

def recommend_cars(filtered_data, top_n=3):
    """
    Recommends the top N cars based on price and mileage.

    Args:
        filtered_data (pd.DataFrame): Filtered car dataset.
        top_n (int): Number of top cars to return.
    
    Returns:
        str: List of VINs for the best cars or a message if no cars match.
    """
    if filtered_data.empty:
        return "No cars match the criteria."
    
    # Sort by price (ascending) and miles (ascending)
    best_cars = filtered_data.sort_values(by=["SellingPrice", "Miles"]).head(top_n)
    return "\n".join(f"{i+1}. VIN: {row['VIN']}"
        for i, row in best_cars.iterrows())

def recommend(type = None, year = None, make = None, model = None, body = None, door = None, extColor = None, intColor = None, engineCylinder = None, transmission = None, engineBlock = None, engineDesc = None, fuel = None, driveTrain = None, mktClass = None, capacity = None, mileage = None, mpg = None, price = None):
    
    mileageRange = { "veryLow":(0,20000), "low":(20001,40000),"medium":(40001,60000),"high":(60001,80000),"veryHigh":(80001,)}
    
    cityRange = { "veryLow":(0,20), "low":(21,40),"medium":(41,60),"high":(61,80),"veryHigh":(81,)}
    
    highwayRange = { "veryLow":(0,25), "low":(26,50),"medium":(51,75),"high":(76,100),"veryHigh":(101,)}
    
    priceRange = { "veryLow":(0,10000), "low":(10001,25000),"medium":(25001,50000),"high":(500001,75000),"veryHigh":(1000000,)}
    
    # Create filters, adding to the dictionary only if the value is not None
    filters = {}
    
    if type is not None:
        filters["type"] = type
    if year is not None:
        filters["year"] = year
    if make is not None:
        filters["make"] = make
    if model is not None:
        filters["model"] = model
    if body is not None:
        filters["body"] = body
    if door is not None:
        filters["door"] = door
    if extColor is not None:
        filters["extColor"] = extColor
    if intColor is not None:
        filters["intColor"] = intColor
    if engineCylinder is not None:
        filters["engineCylinder"] = engineCylinder
    if transmission is not None:
        filters["transmission"] = transmission
    if engineBlock is not None:
        filters["engineBlock"] = engineBlock
    if engineDesc is not None:
        filters["engineDesc"] = engineDesc
    if fuel is not None:
        filters["fuel"] = fuel
    if driveTrain is not None:
        filters["driveTrain"] = driveTrain
    if mktClass is not None:
        filters["mktClass"] = mktClass
    if capacity is not None:
        filters["capacity"] = capacity
    if mileage is not None:
        filters["mileage"] = mileageRange.get(mileage)  # Use the mileage range if it's provided
    if mpg is not None:
        filters["cityMPG"] = cityRange.get(mpg)  # Use the city MPG range if it's provided
        filters["highwayMPG"] = highwayRange.get(mpg)  # Use the highway MPG range if it's provided
    if price is not None:
        filters["price"] = priceRange.get(price)  # Use the price range if it's provided

    # Load the dataset
    car_data = pd.read_csv("data/vehiclesCleaned.csv")

    # Filter and recommend
    filtered_cars = filter_cars(car_data, filters)
    recommendation = recommend_cars(filtered_cars)
    print(recommendation)

if __name__ == "__main__":
    recommend()
    