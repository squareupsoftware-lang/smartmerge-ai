import requests
import pandas as pd
from core.config import settings

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QHBoxLayout, QListWidget, QTableWidget,
    QTableWidgetItem, QLabel, QMessageBox
)


API_MATCH = "http://127.0.0.1:8000/api/v1/merge/match"


class MergeUI(QWidget):
    def __init__(self, token):
        super().__init__()

        self.token = token
        self.setWindowTitle("AI Smart Merge")
        self.resize(1000, 600)

        self.layout = QVBoxLayout()

        # 🔹 Upload buttons
        btn_layout = QHBoxLayout()

        self.upload_a = QPushButton("Upload File A")
        self.upload_b = QPushButton("Upload File B")

        self.upload_a.clicked.connect(lambda: self.load_file("A"))
        self.upload_b.clicked.connect(lambda: self.load_file("B"))

        btn_layout.addWidget(self.upload_a)
        btn_layout.addWidget(self.upload_b)

        # 🔹 Column lists
        list_layout = QHBoxLayout()

        self.list_a = QListWidget()
        self.list_b = QListWidget()
        self.list_a.setDragEnabled(True)
        self.list_b.setDragEnabled(True)

        list_layout.addWidget(self.list_a)
        list_layout.addWidget(self.list_b)

        # 🔹 Mapping table
        self.mapping_table = QTableWidget()
        self.mapping_table.setColumnCount(2)
        self.mapping_table.setHorizontalHeaderLabels(["File A", "File B"])
        self.mapping_table.setAcceptDrops(True)
        self.mapping_table.setDragDropMode(QTableWidget.InternalMove)

        # 🔹 Buttons
        self.match_btn = QPushButton("AI Match Columns")
        self.merge_btn = QPushButton("Merge Files")

        self.match_btn.clicked.connect(self.match_columns)
        self.merge_btn.clicked.connect(self.merge_files)

        # Layout
        self.layout.addLayout(btn_layout)
        self.layout.addLayout(list_layout)
        self.layout.addWidget(QLabel("Column Mapping"))
        self.layout.addWidget(self.mapping_table)
        self.layout.addWidget(self.match_btn)
        self.layout.addWidget(self.merge_btn)
        
        # 🔹 Merge key selector
        self.key_dropdown = QComboBox()
        self.layout.addWidget(QLabel("Select Merge Key"))
        self.layout.addWidget(self.key_dropdown)

        # 🔹 Preview table
        self.preview_table = QTableWidget()
        self.layout.addWidget(QLabel("Merge Preview"))
        self.layout.addWidget(self.preview_table)

        # 🔹 Export button
        self.export_btn = QPushButton("Export Merged File")
        self.export_btn.clicked.connect(self.export_merged)
        self.layout.addWidget(self.export_btn)

        self.setLayout(self.layout)
        
        self.mapping_table.setColumnCount(3)
        self.mapping_table.setHorizontalHeaderLabels(["File A", "File B", "Confidence"])

    # 📂 Load file
    def load_file(self, file_type):
        path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "Excel (*.xlsx)")

        if not path:
            return

        df = pd.read_excel(path)

        if file_type == "A":
            self.df_a = df
            self.list_a.clear()
            self.list_a.addItems(df.columns)
        else:
            self.df_b = df
            self.list_b.clear()
            self.list_b.addItems(df.columns)

    # 🧠 AI Matching
    def match_columns(self):
        cols1 = [self.list_a.item(i).text() for i in range(self.list_a.count())]
        cols2 = [self.list_b.item(i).text() for i in range(self.list_b.count())]

        try:
            res = requests.post(
                API_MATCH,
                json={"cols1": cols1, "cols2": cols2},
                headers={"Authorization": f"Bearer {self.token}"}
            )
            mapping = res.json()

            self.populate_mapping(mapping)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # 📋 Show mapping
    def populate_mapping(self, mapping):
        self.mapping_table.setRowCount(len(mapping))
        self.key_dropdown.clear()

        for i, (k, v) in enumerate(mapping.items()):
            self.mapping_table.setItem(i, 0, QTableWidgetItem(k))
            self.mapping_table.setItem(i, 1, QTableWidgetItem(v["match"]))
            self.mapping_table.setItem(i, 2, QTableWidgetItem(f"{v['confidence']}%"))

            self.key_dropdown.addItem(k)

    # 🔗 Merge files
    def merge_files(self):
        if not hasattr(self, "df_a") or not hasattr(self, "df_b"):
            QMessageBox.warning(self, "Error", "Upload both files")
            return

        mappings = {}

        for row in range(self.mapping_table.rowCount()):
            item_a = self.mapping_table.item(row, 0)
            item_b = self.mapping_table.item(row, 1)

            if not item_a or not item_b:
                continue

            mappings[item_a.text()] = item_b.text()

        if not mappings:
            QMessageBox.warning(self, "Error", "No mappings found")
            return

        try:
            df_b_renamed = self.df_b.rename(columns={v: k for k, v in mappings.items()})

            # ✅ Use selected key instead of first column
            key = self.key_dropdown.currentText()

            if key not in self.df_a.columns:
                QMessageBox.warning(self, "Error", "Invalid merge key")
                return

            merged = pd.merge(self.df_a, df_b_renamed, on=key, how="inner")

            self.merged_df = merged  # ✅ store for export

            self.show_preview(merged)
            
            merged.to_excel(settings.MERGED_FILE_PATH, index=False)

            QMessageBox.information(self, "Success", "Files merged successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Merge Error", str(e))
            
            
    def show_preview(self, df):
        data = df.head(20).to_dict(orient="records")

        if not data:
            return

        columns = list(data[0].keys())

        self.preview_table.setColumnCount(len(columns))
        self.preview_table.setHorizontalHeaderLabels(columns)
        self.preview_table.setRowCount(len(data))

        for row_idx, row in enumerate(data):
            for col_idx, col in enumerate(columns):
                self.preview_table.setItem(row_idx, col_idx, QTableWidgetItem(str(row[col])))

        self.preview_table.resizeColumnsToContents()
        
        
        
    def export_merged(self):
        if not hasattr(self, "merged_df"):
            QMessageBox.warning(self, "Error", "No merged data to export")
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            "merged_output.xlsx",
            "Excel Files (*.xlsx)"
        )

        if not path:
            return

        try:
            self.merged_df.to_excel(path, index=False)
            QMessageBox.information(self, "Success", "File exported successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))