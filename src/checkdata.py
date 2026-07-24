import pandas as pd
import os

folder = "data"

files = [f for f in os.listdir(folder) if f.endswith(".csv")]

print("CSV Files:")
for file in files:
    print(file)

print("\nChecking columns...\n")

for file in files:
    path = os.path.join(folder, file)

    try:
        df = pd.read_csv(path)

        print("File:", file)
        print("Columns:", list(df.columns))

        if "traffic_volume" in df.columns:
            print("✅ Is file me traffic_volume mila")
            print(df["traffic_volume"].describe())

        print("-"*50)

    except Exception as e:
        print(file, "error:", e)