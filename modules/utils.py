def save_csv(df,name_file,path):
    """
    Save a dataframe in a csv file.
    """
    df.to_csv(f'{path}{name_file}.csv',index=False)