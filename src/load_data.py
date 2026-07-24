import pandas as pd

df = pd.read_csv("data/Metro_Interstate_Traffic_Volume.csv")

print("Shape:", df.shape)
print("\nColumns:")
print(df.columns)

print("\nFirst 5 Rows:")
print(df.head())