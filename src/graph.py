import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv(
    "data/Metro_Interstate_Traffic_Volume.csv"
)

df["holiday"] = df["holiday"].fillna("No Holiday")
df["date_time"] = pd.to_datetime(df["date_time"])

# Daily average traffic
daily = (
    df.groupby(
        df["date_time"].dt.date
    )["traffic_volume"]
    .mean()
)

plt.figure(figsize=(12,5))
plt.plot(daily.index,
         daily.values)

plt.title("Daily Average Traffic")
plt.xlabel("Date")
plt.ylabel("Traffic Volume")
plt.xticks(rotation=45)

plt.show()