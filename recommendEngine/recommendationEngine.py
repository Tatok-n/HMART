import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler


# Load dataset
df = pd.read_csv('vehicles.csv')

# Features to use (example)
features = ['Type','Year','Make','Body','Doors','Int_Color_Generic','Transmission,Miles','SellingPrice','BookValue','Ext_Color_Generic','Drivetrain','Fuel_Type','CityMPG','HighwayMPG','PassengerCapacity']

target = 'Recommendation_Score'  # Create a score based on user preference or similarity

# Fill missing values
df = df[features].dropna()

