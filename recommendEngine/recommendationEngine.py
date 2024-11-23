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
    return "\n".join(f"{i+1}. VIN: {row['VIN']}, Price: {row['SellingPrice']}, Miles: {row['Miles']}"
                     for i, row in best_cars.iterrows())

def recommend(type, year, make, model, body, door, extColor, intColor, engineCylinder, transmission, engineBlock, engineDesc, fuel, driveTrain, mktClass, capacity, mileage, mpg, price):
    
    mileageRange = { "veryLow":(0,20000), "low":(20001,40000),"medium":(40001,60000),"high":(60001,80000),"veryHigh":(80001,)}
    
    cityRange = { "veryLow":(0,20), "low":(21,40),"medium":(41,60),"high":(61,80),"veryHigh":(81,)}
    
    highwayRange = { "veryLow":(0,25), "low":(26,50),"medium":(51,75),"high":(76,100),"veryHigh":(101,)}
    
    priceRange = { "veryLow":(0,10000), "low":(10001,25000),"medium":(25001,50000),"high":(500001,75000),"veryHigh":(1000000,)}
    
    filters = {
        "type": type,
        "year": year,
        "make": make,
        "model": model,
        "body": body,
        "door": door,
        "extColor": extColor,
        "intColor": intColor,
        "engineCylinder": engineCylinder,
        "transmission": transmission,
        "engineBlock": engineBlock,
        "engineDesc": engineDesc,
        "fuel": fuel,
        "driveTrain": driveTrain,
        "mktClass": mktClass,
        "capacity": capacity,
        "mileage" : mileageRange[mileage],
        "cityMPG" : cityRange[mpg],
        "highwayMPG" : highwayRange[mpg],
        "price" : priceRange[price]
    }
    # Load the dataset
    car_data = pd.read_csv("vehicles-cleaned.csv")

    # Filtering discrete input
    for criteria, value in filters:
        filters[criteria] = value or None
        
    # Filter continuous input
    
    




    # Filter and recommend
    filtered_cars = filter_cars(car_data, filters)
    recommendation = recommend_cars(filtered_cars)
    print(recommendation)

if __name__ == "__main__":
    recommend()