import pandas as pd

df = pd.read_csv(
    "data/Metro_Interstate_Traffic_Volume.csv"
)

print(df.info())

print("\nMissing Values:")
print(df.isnull().sum())

print("\nStatistics:")
print(df.describe())