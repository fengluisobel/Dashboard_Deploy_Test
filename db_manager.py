import duckdb
import pandas as pd
import os

DB_PATH = 'recruitment.db'
TABLE_NAME = 'recruitment_data'

class DBManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBManager, cls).__new__(cls)
            cls._instance.conn = duckdb.connect(DB_PATH)
        return cls._instance

    def _sanitize_df(self, df):
        """
        Convert object columns (which might contain numpy.str_) to standard strings
        to avoid DuckDB 'Unsupported string type' error.
        """
        # Create a copy to avoid modifying the original dataframe
        df_clean = df.copy()
        for col in df_clean.select_dtypes(include=['object']):
            df_clean[col] = df_clean[col].apply(str)
        return df_clean

    def init_db(self, df=None):
        """
        Initialize the database. 
        If table doesn't exist and df is provided, create and seed it.
        """
        # Check if table exists
        try:
            tables = self.conn.execute("SHOW TABLES").fetchall()
            table_exists = any(t[0] == TABLE_NAME for t in tables)
        except Exception:
            table_exists = False

        if not table_exists and df is not None:
            # Sanitize data first
            df_clean = self._sanitize_df(df)
            
            # Register dataframe and create table from it
            self.conn.register('temp_df', df_clean)
            self.conn.execute(f"CREATE TABLE {TABLE_NAME} AS SELECT * FROM temp_df")
            self.conn.unregister('temp_df')
            print(f"Database initialized and seeded with {len(df)} records.")
        elif not table_exists:
            print("Database not initialized. Please provide initial data.")

    def load_data_to_df(self):
        """
        Load all data from DuckDB to Pandas DataFrame.
        """
        try:
            return self.conn.execute(f"SELECT * FROM {TABLE_NAME}").df()
        except duckdb.CatalogException:
            return pd.DataFrame() # Return empty if table doesn't exist

    def import_data(self, df, mode='append'):
        """
        Import data from DataFrame.
        mode: 'append' or 'replace'
        """
        try:
            # Sanitize data first
            df_clean = self._sanitize_df(df)
            
            self.conn.register('upload_df', df_clean)
            if mode == 'replace':
                self.conn.execute(f"CREATE OR REPLACE TABLE {TABLE_NAME} AS SELECT * FROM upload_df")
            elif mode == 'append':
                self.conn.execute(f"INSERT INTO {TABLE_NAME} SELECT * FROM upload_df")
            self.conn.unregister('upload_df')
            return True, f"Successfully imported {len(df)} records ({mode})."
        except Exception as e:
            return False, str(e)

    def execute_query(self, query):
        """
        Execute arbitrary SQL query.
        """
        try:
            result = self.conn.execute(query).df()
            return True, result
        except Exception as e:
            return False, str(e)
            
    def close(self):
        self.conn.close()
