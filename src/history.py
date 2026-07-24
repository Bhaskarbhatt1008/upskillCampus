import pandas as pd

df = pd.read_csv(
    "data/Metro_Interstate_Traffic_Volume.csv"
)

df["date_time"] = pd.to_datetime(df["date_time"])

# Example: 9 AM traffic
hour = 9

history = df[
    df["date_time"].dt.hour == hour
]

print(
    history[
        ["date_time", "traffic_volume"]
    ].tail(10)
)