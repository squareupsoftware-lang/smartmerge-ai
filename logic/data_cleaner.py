import pandas as pd
import os

class DataCleaner:
    def load_file(self, folder_path, file_name):
        file_path = os.path.join(folder_path, file_name)

        try:
            if file_name.lower().endswith(".csv"):
                return pd.read_csv(file_path)

            elif file_name.lower().endswith(".xlsx"):
                return pd.read_excel(file_path, engine="openpyxl")  # ✅ FIX

            elif file_name.lower().endswith(".xls"):
                return pd.read_excel(file_path, engine="xlrd")  # ✅ FIX

        except Exception as e:
            print(f"Primary load failed: {e}")
            # 🔁 fallback
            try:
                return pd.read_csv(file_path)
            except:
                print(f"Failed completely: {file_name}")
                return None

    def get_columns(self, folder_path, file_name):
        df = self.load_file(folder_path, file_name)
        
        if df is not None and not df.empty:
            return list(df.columns)
        
        return []
        
        
    def remove_nulls(self, df): ...
    def normalize_columns(self, df): ...
    def fix_types(self, df): ...

    def run(self, df):
        df = self.remove_nulls(df)
        df = self.normalize_columns(df)
        return df