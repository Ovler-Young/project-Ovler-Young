def normalize_list_columns(df):
    normalized_cols = []
    for col in df.columns:
        # Sample values to check types (more efficient than checking all)
        sample = df[col].dropna().head(1000)
        
        # Check if column contains mix of lists and single values
        has_list = any(isinstance(x, list) for x in sample)
        has_single = any(isinstance(x, (str, int, float)) for x in sample)
        
        if has_list and has_single:
            df[col] = df[col].apply(
                lambda x: [x] if isinstance(x, (str, int, float)) else 
                         x if isinstance(x, list) else None
            )
            normalized_cols.append(col)
    
    if normalized_cols:
        print(f"Normalized mixed single/list values in columns: {normalized_cols}")
    return df