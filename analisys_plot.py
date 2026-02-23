import pandas as pd
import matplotlib.pyplot as plt

def generate_plot(file_path, output_name, title):
    df = pd.read_csv(file_path)

    plt.figure()

    plt.plot(df["time"], df["today"], label="Today")
    plt.plot(df["time"], df["yesterday"], label="Yesterday")
    plt.plot(df["time"], df["same_day_last_week"], label="Same Day Last Week")
    plt.plot(df["time"], df["avg_last_week"], label="Avg Last Week")
    plt.plot(df["time"], df["avg_last_month"], label="Avg Last Month")

    plt.xlabel("Hour")
    plt.ylabel("Sales Volume")
    plt.title(title)
    plt.legend()
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig(output_name)
    plt.close()

# =========================
# GENERATE BOTH GRAPHS
# =========================

generate_plot(
    "data/checkout_1.csv",
    "checkout_1_analysis.png",
    "Checkout 1 - Hourly Sales Comparison"
)

generate_plot(
    "data/checkout_2.csv",
    "checkout_2_analysis.png",
    "Checkout 2 - Hourly Sales Comparison"
)

print("Graphs generated successfully.")