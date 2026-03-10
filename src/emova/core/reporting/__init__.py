import pandas as pd

def generate_report():

    df = pd.read_csv("outputs/emotions.csv")

    summary = df.value_counts()

    print(summary)