import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

# Load data
df = pd.read_csv(
    "data/Metro_Interstate_Traffic_Volume.csv"
)
city_df = pd.read_csv(
    "data/city_data.csv"
)


cities = city_df["city"].tolist()

import numpy as np

np.random.seed(42)

df["city"] = np.random.choice(
    city_df["city"],
    size=len(df)
)

# Preprocessing
df["holiday"] = df["holiday"].fillna(
    "No Holiday"
)

df["date_time"] = pd.to_datetime(
    df["date_time"]
)

df["year"] = df["date_time"].dt.year
df["month"] = df["date_time"].dt.month
df["day"] = df["date_time"].dt.day
df["hour"] = df["date_time"].dt.hour
df["weekday"] = df["date_time"].dt.weekday


# Features
X = df[
    [
        "temp",
        "rain_1h",
        "snow_1h",
        "clouds_all",
        "year",
        "month",
        "day",
        "hour",
        "weekday",
        
    ]
]

y = df["traffic_volume"]

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Train model
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

# Test prediction
pred = model.predict(X_test)

mae = mean_absolute_error(
    y_test,
    pred
)

print("MAE :", mae)

# Sample prediction
sample = pd.DataFrame(
    [[290,0,0,75,2026,7,15,10,2]],
    columns=X.columns
)

prediction = model.predict(sample)

print(
    "Predicted Traffic:",
    int(prediction[0])
)
import joblib

joblib.dump(model, "models/traffic_model.pkl")

print("Model Saved!")