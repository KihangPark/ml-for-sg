

def add_appendix_to_text_dataframe(df_x_text_full):
    new_columns = []
    for column in df_x_text_full.columns:
        new_columns.append('text__'+column)
    df_x_text_full.columns = new_columns
    return df_x_text_full
