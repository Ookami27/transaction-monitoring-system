import pandas as pd

df = pd.read_csv("data/transactions.csv")

print("\nCOLUNAS:")
print(df.columns)

print("\nPRIMEIRAS 5 LINHAS:")
print(df.head())