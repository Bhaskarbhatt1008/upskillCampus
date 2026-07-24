import pandas as pd

df = pd.read_csv(
    "data/Metro_Interstate_Traffic_Volume.csv"
)

# Missing holiday values fill
df["holiday"] = df["holiday"].fillna("No Holiday")

# Convert datetime
df["date_time"] = pd.to_datetime(df["date_time"])

# Create new columns
df["year"] = df["date_time"].dt.year
df["month"] = df["date_time"].dt.month
df["day"] = df["date_time"].dt.day
df["hour"] = df["date_time"].dt.hour
df["weekday"] = df["date_time"].dt.day_name()

print(df.head())

print("\nNew Columns:")
print(df.columns)