import pandas as pd


def read_excel_file(filepath: str) -> pd.DataFrame:
    df = pd.read_excel(filepath, index_col=False)
    return df
