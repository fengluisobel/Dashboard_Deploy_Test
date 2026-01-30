import pandas as pd
import duckdb
from data_generator_complete import generate_complete_recruitment_data
import db_manager
import os

# Monkeypatch DB_PATH to avoid lock
db_manager.DB_PATH = 'recruitment_debug.db'
if os.path.exists(db_manager.DB_PATH):
    try:
        os.remove(db_manager.DB_PATH)
    except:
        pass

from db_manager import DBManager

try:
    print("Generating data...")
    df = generate_complete_recruitment_data(months=12, recruiters=5, departments=5)
    print("Data generated.")
    
    print("\nAttempting DB Init via DBManager (with sanitization)...")
    db = DBManager()
    
    # Force new connection to debug db
    db.conn = duckdb.connect(db_manager.DB_PATH)
    
    db.init_db(df)
    
    print("Success! Data loaded into", db_manager.DB_PATH)
    print(db.load_data_to_df().head())

except Exception as e:
    print(f"Caught error: {e}")
    import traceback
    traceback.print_exc()
