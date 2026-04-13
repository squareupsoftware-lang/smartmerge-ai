import os

last_modified = 0

class FileLoader:
    def __init__(self):
        self.folder_path = ""
        self.allowed_extensions = [".csv", ".xlsx"]

    def set_folder(self, folder_path):
        self.folder_path = folder_path

    def set_extensions(self, extensions):
        self.allowed_extensions = extensions

    def get_files(self):
        if not self.folder_path:
            return []

        files = []
        for file in os.listdir(self.folder_path):
            for ext in self.allowed_extensions:
                if file.lower().endswith(ext):
                    files.append(file)
                    break

        return files
        
    def load_data():
        global last_modified

        current_modified = os.path.getmtime(FILE_PATH)

        if current_modified != last_modified:
            load_data.cache_clear()
            last_modified = current_modified

        return pd.read_excel(FILE_PATH)
        
        
    def get_kpis():
        df = load_data()

        return {
            "total_rows": len(df),
            "total_sales": df.select_dtypes(include='number').sum().sum()
        }