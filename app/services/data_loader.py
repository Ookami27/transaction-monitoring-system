import pandas as pd

def load_transactions():
    df = pd.read_csv("data/transactions.csv")
    return df