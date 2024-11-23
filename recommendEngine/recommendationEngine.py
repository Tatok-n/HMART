import pandas as pd

def load_data(filename):
    """Loads the dataset from a CSV file."""
    return pd.read_csv("vehicles-cleaned.csv")

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

def main():
    # Load the dataset
    filename = "car_data.csv"  # Replace with your dataset file
    car_data = load_data(filename)

    # Filtering Input
    car_type = input("Type (e.g., 'New', 'Used'): ").strip() or None
    make = input("Make (e.g., 'Toyota', 'Hyundai'): ").strip() or None
    fuel_type = input("Fuel Type (e.g., 'Gasoline Fuel', 'Hybrid Fuel'): ").strip() or None
    price_range = input("Price range (min,max): ").strip() or None
    if price_range:
        price_range = tuple(map(int, price_range.split(',')))
    mileage_range = input("Mileage range (min,max): ").strip() or None
    if mileage_range:
        mileage_range = tuple(map(int, mileage_range.split(',')))

    # Filters dictionary
    filters = {
        "Type": car_type,
        "Make": make,
        "Fuel_Type": fuel_type,
        "SellingPrice": price_range,
        "Miles": mileage_range,
    }

    # Filter and recommend
    filtered_cars = filter_cars(car_data, filters)
    recommendation = recommend_cars(filtered_cars)
    print(recommendation)

if __name__ == "__main__":
    main()