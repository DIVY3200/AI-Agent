import pandas as pd

def load_data(file):
    return pd.read_csv(file)

def save_results(data, filename):
    data.to_csv(filename, index=False)