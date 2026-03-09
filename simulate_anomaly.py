import pandas as pd
import numpy as np

INPUT_FILE = "data/transactions.csv"
OUTPUT_FILE = "data/transactions_anomaly.csv"

# -----------------------
# 1. Load dataset
# -----------------------
df = pd.read_csv(INPUT_FILE)
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)

df_anom = df.copy()

# ============================
# 🔥 2. Define last 60 minutes
# ============================

last_timestamp = df_anom["timestamp"].max()
last_60_start = last_timestamp - pd.Timedelta(minutes=60)

mask_last_60 = df_anom["timestamp"] >= last_60_start

# ============================
# 🔥 3. Dentro desses 60 minutos:
#    - Approved -> failed/denied
#    - Aumentar count
# ============================

# Aumenta o volume para simular crise
df_anom.loc[mask_last_60, "count"] = df_anom.loc[mask_last_60, "count"] * 5

# Entre os últimos 60 minutos, pegue as linhas approved
mask_approved_last_60 = mask_last_60 & (df_anom["status"] == "approved")

# Converte approved em failed ou denied (meio a meio)
df_anom.loc[mask_approved_last_60, "status"] = np.where(
    np.random.rand(mask_approved_last_60.sum()) > 0.5,
    "failed",
    "denied"
)

# ============================
# 🔥 4. Forçar os ÚLTIMOS 15 MINUTOS
#    a serem total FAIL
# ============================

last_35_start = last_timestamp - pd.Timedelta(minutes=35)
mask_last_35 = df_anom["timestamp"] >= last_35_start

df_anom.loc[mask_last_35, "status"] = "failed"
df_anom.loc[mask_last_35, "count"] = df_anom.loc[mask_last_35, "count"].clip(lower=50) * 3

# ============================
# 🔥 5. Salvar CSV anômalo
# ============================

df_anom.to_csv(OUTPUT_FILE, index=False)

print("🔥 Anomaly file generated focusing on the last 60 minutes.")
print(f"Last timestamp in dataset: {last_timestamp}")
print(f"File saved as: {OUTPUT_FILE}")