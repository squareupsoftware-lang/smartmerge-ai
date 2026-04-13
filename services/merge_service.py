def merge_files(df1, df2, on_col):
    return df1.merge(df2, on=on_col, how="inner")