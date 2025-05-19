# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 15:39:51 2024

@author: Audric
"""
import pandas as pd

def debet_kredit_process(combined_df):
    # Create new columns DEBET and KREDIT with initial value of 0
    combined_df['DEBET'] = 0
    combined_df['KREDIT'] = 0

    # Loop through each row and process the MUTASI column
    for idx, row in combined_df.iterrows():
        mutasi_value = row['MUTASI']
        saldo = row['SALDO']

        # Check if MUTASI value is valid (not NaN or None)
        if pd.isna(mutasi_value):
            continue
        if pd.notna(saldo):
            # Remove commas, strip spaces, and convert to float
            combined_df.at[idx, 'SALDO'] = float(str(saldo).replace(',', '').strip())
        
        mutasi_value = str(mutasi_value).strip()

        # Check if the value contains 'DB' (Debet) and process accordingly
        if 'DB' in mutasi_value:
            # Remove 'DB' and format the value as a number, then assign to DEBET
            value = float(mutasi_value.replace('DB', '').replace(',', '').strip())
            combined_df.at[idx, 'DEBET'] = value
        else:
            # Else, it should be a KREDIT value, so assign it to KREDIT
            try:
                value = float(mutasi_value.replace(',', '').strip())
                combined_df.at[idx, 'KREDIT'] = value
            except ValueError:
                # Handle any unexpected non-numeric values (e.g., '<NA>')
                combined_df.at[idx, 'KREDIT'] = 0
    return combined_df

def string_number_process(combined_df):
    # Loop through each row and process the Debet and Kredit columns
    for idx, row in combined_df.iterrows():
        Debet = row['Debet']
        Kredit = row['Kredit']
        Saldo = row['Saldo']

        # Convert Debet and Kredit values to float if they are not NaN or None
        if pd.notna(Debet):
            # Remove commas, strip spaces, and convert to float
            combined_df.at[idx, 'Debet'] = float(str(Debet).replace(',', '').strip())
        
        if pd.notna(Kredit):
            # Remove commas, strip spaces, and convert to float
            combined_df.at[idx, 'Kredit'] = float(str(Kredit).replace(',', '').strip())
        
        if pd.notna(Saldo):
            # Remove commas, strip spaces, and convert to float
            combined_df.at[idx, 'Saldo'] = float(str(Saldo).replace(',', '').strip())

    return combined_df

def clean_dataframe(df):
    """
    Cleans a DataFrame by:
    1. Removing rows that contain unwanted text like "Currency" or page-related information.
    2. Removing repeated header rows.
    3. Resetting the index.

    Parameters:
    df (pd.DataFrame): The input DataFrame.

    Returns:
    pd.DataFrame: The cleaned DataFrame.
    """
    # Step 1: Remove rows that contain unwanted text
    unwanted_phrases = [
        "Currency",
        "Halaman",  # Covers "Halaman X dari Y"
        "Page",     # Covers "Page X of Y"
        "Tanggal Transaksi",
        "Transaction Date"
    ]
    df = df[~df.apply(lambda row: row.astype(str).str.contains('|'.join(unwanted_phrases), case=False, na=False).any(), axis=1)]

    # Step 2: Reset the index
    df = df.reset_index(drop=True)

    return df

def reformat_dataframe(df):
    """
    Reformats a DataFrame by setting the row with 'TANGGAL' or 'TANGGAL TRANSAKSI' 
    (case-insensitive, ignoring spaces) as the column headers and extracting the table 
    data starting from the row below it. If no such row is found, returns the original DataFrame.

    Parameters:
    df (pd.DataFrame): The input DataFrame.

    Returns:
    pd.DataFrame: The reformatted DataFrame or original DataFrame if 'TANGGAL' or 
                  'TANGGAL TRANSAKSI' is not found.
    """
    # Normalize text by removing spaces and converting to lowercase
    def normalize_text(text):
        return "".join(text.split()).lower() if isinstance(text, str) else ""

    # Step 1: Find the row index where any cell matches 'TANGGAL' or 'TANGGAL TRANSAKSI' (ignoring spaces)
    tanggal_row_idx = df.apply(
        lambda row: row.apply(normalize_text).isin(["tanggal", "tanggaltransaksi"]).any(), axis=1
    ).idxmax()

    # Step 2: Check if the identified row actually contains 'TANGGAL' or 'TANGGAL TRANSAKSI'
    if df.iloc[tanggal_row_idx].apply(normalize_text).isin(["tanggal", "tanggaltransaksi"]).any():
        # Step 3: Set the identified row as the new column names
        df.columns = df.iloc[tanggal_row_idx].fillna("").apply(lambda x: "".join(x.split()).strip())

        # Ensure 'TANGGAL TRANSAKSI' is properly formatted
        df.columns = df.columns.to_series().replace({"TanggalTransaksi": "Tanggal Transaksi"})
        df.columns = df.columns.to_series().replace({"UraianTransaksi": "Uraian Transaksi"})

        # Step 4: Extract the rows below the header row
        df = df.iloc[tanggal_row_idx + 1:].reset_index(drop=True)

    # Step 5: Return the cleaned DataFrame
    return df

def combine_adjacent_columns(df, target_columns):
    """
    Combines unnamed adjacent columns into specified target columns in a DataFrame.

    Parameters:
    df (pd.DataFrame): The input DataFrame with possible empty columns adjacent to target columns.
    target_columns (list of str): List of column names to merge adjacent unnamed columns into.

    Returns:
    pd.DataFrame: The modified DataFrame with adjacent columns merged into the target columns.
    """
    # Step 1: Identify empty columns
    empty_columns = [col for col in df.columns if col.strip() == ""]

    # Step 2: Iterate through each target column and merge adjacent unnamed columns
    for target_col in target_columns:
        if target_col in df.columns:
            col_index = df.columns.get_loc(target_col)  # Index of the target column

            # Get adjacent columns (before and after)
            if col_index > 0 and df.columns[col_index - 1] in empty_columns:
                before_col = df.iloc[:, col_index - 1].fillna("").str.strip()
            else:
                before_col = ""
            if col_index > 0 and df.columns[col_index + 1] in empty_columns:
                after_col = df.iloc[:, min(len(df.columns) - 1, col_index + 1)].fillna("").str.strip()
            else:
                after_col = ""

            # Merge into the target column
            df[target_col] = (before_col + " " + df[target_col].fillna("").str.strip() + " " + after_col).str.strip()

    # Step 3: Remove unnecessary empty columns
    df = df.drop(columns=empty_columns)
    
    # Step 4: Rename 'KETERANGANCBG' to 'KETERANGAN' and add an empty 'CBG' column if applicable
    if "KETERANGANCBG" in df.columns:
        df = df.rename(columns={"KETERANGANCBG": "KETERANGAN"})
        df["CBG"] = ""

    # Step 4: Return the modified DataFrame
    return df

def postprocessing(tables):
    """
    Perform post-processing on the extracted tables and combine only those that have the specified columns.

    Args:
    - tables: List of extracted tables (can be raw Table objects or DataFrames).

    Returns:
    - combined_df: DataFrame with post-processed and combined tables.
    - other_tables: List of DataFrames with tables that do not meet the column requirements.
    """
    combined_df = pd.DataFrame()  # Initialize an empty DataFrame for the combined results
    required_columns_old = ["TANGGAL", "KETERANGAN", "CBG", "MUTASI", "SALDO"]
    required_columns_new = ["Tanggal Transaksi", "Uraian Transaksi", "Teller", "Debet", "Kredit", "Saldo"]
    other_tables = []  # List to store tables without the required columns

    def table_to_dataframe(table):
        """
        Convert a Table object to a pandas DataFrame if necessary.

        Args:
        - table: A raw table object (could be a DataFrame or a custom table object).

        Returns:
        - A pandas DataFrame.
        """
        if isinstance(table, pd.DataFrame):
            return table  # Already a DataFrame, no conversion needed

        # Handle common table object formats
        if hasattr(table, "df"):  # Camelot or similar
            return table.df  # Extract as a DataFrame directly

        if isinstance(table, list):  # Handle lists of lists (Tabula or similar)
            if all(isinstance(row, list) for row in table):
                return pd.DataFrame(table)  # Convert list of lists to DataFrame

        # If none of the above work, raise an error
        raise ValueError(f"Unsupported table format: {type(table)}")

    def combine_partial_rows(df, date_col='TANGGAL', cbg_col='CBG', mutasi_col='MUTASI', saldo_col='SALDO', keterangan_col='KETERANGAN'):
        """
        Combines rows with filled 'keterangan_col' but empty other columns
        into the nearest valid row above where other columns are filled.

        Parameters:
        df (pd.DataFrame): The input DataFrame.
        keterangan_col (str): The name of the 'KETERANGAN' column.

        Returns:
        pd.DataFrame: The modified DataFrame with combined 'keterangan_col' values.
        """
        # Replace all empty string values "" or " " with NaN
        df = df.replace(["", " "], pd.NA)

        # Get the list of columns to check for "empty" (all except keterangan_col)
        other_cols = [col for col in df.columns if col != keterangan_col]

        for i in range(len(df)):
            # Check if the row is empty except for 'keterangan_col'
            is_empty = all(pd.isna(df.loc[i, col]) for col in other_cols)

            if is_empty:
                # Find the nearest row with valid values in 'other_cols'
                nearest_idx = None

                # Search above for the nearest valid row
                for j in range(i - 1, -1, -1):
                    if all(pd.notna(df.loc[j, col]) for col in other_cols):
                        nearest_idx = j
                        break

                # If no valid row above, search below
                if nearest_idx is None:
                    for j in range(i + 1, len(df)):
                        if all(pd.notna(df.loc[j, col]) for col in other_cols):
                            nearest_idx = j
                            break

                # Combine 'keterangan_col' with the nearest valid row
                if nearest_idx is not None:
                    df.loc[nearest_idx, keterangan_col] = (
                        str(df.loc[nearest_idx, keterangan_col]).strip() + " " + str(df.loc[i, keterangan_col]).strip()
                    ).strip()
                    # Clear the current row's 'keterangan_col' as it has been merged
                    df.loc[i, keterangan_col] = None

        # Remove rows where the 'is_empty' condition is True
        df = df[~df.apply(lambda row: all(pd.isna(row[col]) for col in other_cols), axis=1)]

        # Reset index for cleanliness
        df = df.reset_index(drop=True)

        return df
    
    def fix_row(df):
        """
        Combines rows with filled 'keterangan_col' but empty other columns
        into the nearest valid row above where other columns are filled.

        Parameters:
        df (pd.DataFrame): The input DataFrame.
        keterangan_col (str): The name of the 'KETERANGAN' column.

        Returns:
        pd.DataFrame: The modified DataFrame with combined 'keterangan_col' values.
        """
        # Replace all empty string values "" or " " with NaN
        df = df.replace(["", " "], pd.NA)

        # Create a flag to identify rows where TANGGAL or CBG is present (actual rows)
        is_main_row = df['TANGGAL'].notna() | df['CBG'].notna() | df['SALDO'].notna()
        
        # Forward-fill the main rows to associate all subsequent sub-rows
        df['group'] = is_main_row.cumsum()
        
        # Group by the identified groups and merge KETERANGAN
        df.columns = [col.replace(" ", "") for col in df.columns]
        fixed_df = df.groupby('group', as_index=False).apply(lambda g: pd.Series({
            'TANGGAL': g['TANGGAL'].iloc[0],  # Keep the first TANGGAL
            'KETERANGAN': ' '.join(g['KETERANGAN'].dropna()).strip(),  # Merge KETERANGAN
            'CBG': g['CBG'].iloc[0],  # Keep the first CBG
            'MUTASI': g['MUTASI'].iloc[0],  # Keep the first DEBET
            'SALDO': g['SALDO'].iloc[0],  # Keep the first SALDO
        }))
        
        # Drop the temporary 'group' column
        fixed_df = fixed_df.drop(columns='group', errors='ignore')
        return fixed_df.reset_index(drop=True)

    # Process each table in the tables list
    for table in tables:
        # Convert Table object to DataFrame if necessary
        df = table_to_dataframe(table)
        check = reformat_dataframe(df)
        
        if isinstance(check.columns[0], str) and check.columns[0].strip().upper() == "TANGGAL":
            check.columns = [col.replace(" ", "") for col in check.columns]

        # Check for the required columns of the old format
        if all(col in check.columns for col in required_columns_old):
            df.columns = [col.replace(" ", "") for col in df.columns]
            # Apply reformatting and combination for the old table format
            df = reformat_dataframe(df)
            df = combine_adjacent_columns(df, ["KETERANGAN", "MUTASI"])
            df = fix_row(df)  # Combine partial rows

            # Ensure the columns are in the correct order
            df = df[required_columns_old]

            # Append the processed table to the combined DataFrame
            combined_df = pd.concat([combined_df, df], ignore_index=True)
            combined_df = debet_kredit_process(combined_df)

        # Check for the required columns of the new format
        elif all(col in check.columns for col in required_columns_new):
            # For the new table format, no reformatting, just append it as is
            df = df[required_columns_new]
            df = combine_partial_rows(df, keterangan_col='Uraian Transaksi')

            # Append the processed table to the combined DataFrame
            combined_df = pd.concat([combined_df, df], ignore_index=True)
            combined_df = clean_dataframe(combined_df)
            combined_df = string_number_process(combined_df)

        else:
            # Append unprocessed tables to other_tables
            other_tables.append(df)

    return combined_df, other_tables