import requests
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout,
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem
)
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet
from PyQt5.QtCore import QTimer

API_BASE = "http://127.0.0.1:8000/api/v1"


class Dashboard(QWidget):
    def __init__(self, token):
        super().__init__()
        self.token = token
        self.setWindowTitle("SmartMerge AI Dashboard")
        self.resize(1000, 650)

        self.layout = QVBoxLayout()

        # 🔹 FILTERS
        self.filter_layout = QHBoxLayout()

        self.x_dropdown = QComboBox()
        self.y_dropdown = QComboBox()
        self.agg_dropdown = QComboBox()

        self.agg_dropdown.addItems(["sum", "avg", "count"])

        self.filter_layout.addWidget(QLabel("Group By:"))
        self.filter_layout.addWidget(self.x_dropdown)

        self.filter_layout.addWidget(QLabel("Value:"))
        self.filter_layout.addWidget(self.y_dropdown)

        self.filter_layout.addWidget(QLabel("Aggregation:"))
        self.filter_layout.addWidget(self.agg_dropdown)

        # 🔹 KPI
        self.kpi_layout = QHBoxLayout()
        self.kpi_total = QLabel("Total: 0")
        self.kpi_avg = QLabel("Average: 0")

        self.kpi_layout.addWidget(self.kpi_total)
        self.kpi_layout.addWidget(self.kpi_avg)

        # 🔹 Chart
        self.chart_view = QChartView()

        # 🔹 Button
        self.refresh_btn = QPushButton("Apply Filters")
        self.refresh_btn.clicked.connect(self.load_data)

        # Layout setup
        self.layout.addLayout(self.filter_layout)
        self.layout.addLayout(self.kpi_layout)
        self.layout.addWidget(self.chart_view)
        self.layout.addWidget(self.refresh_btn)
        
        # 🔹 Table View
        self.table = QTableWidget()
        self.table.setSortingEnabled(True)  # ✅ Enable sorting

        self.layout.addWidget(self.table)

        self.setLayout(self.layout)
        
        self.export_btn = QPushButton("Export to Excel")
        self.export_btn.clicked.connect(self.export_to_excel)

        self.layout.addWidget(self.export_btn)
        
        
        self.chart_type_dropdown = QComboBox()
        self.chart_type_dropdown.addItems(["Bar", "Pie", "Line"])

        self.filter_layout.addWidget(QLabel("Chart Type:"))
        self.filter_layout.addWidget(self.chart_type_dropdown)
        
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search in table...")
        self.search_box.textChanged.connect(self.apply_search)

        self.layout.addWidget(self.search_box)
        
        self.upload_btn = QPushButton("Upload File")
        self.upload_btn.clicked.connect(self.upload_file)
        self.layout.addWidget(self.upload_btn)
        
        self.preview_table = QTableWidget()
        self.preview_table.setMaximumHeight(150)  # small preview

        self.layout.addWidget(self.preview_table)

        # 🔄 Auto refresh
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_data)
        self.timer.start(5000)

        # Load columns first
        self.load_columns()

    # 🔹 Get columns dynamically
    def load_columns(self):
        url = f"{API_BASE}/data"
        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            res = requests.get(url, headers=headers)
            data = res.json()

            if isinstance(data, list) and len(data) > 0:
                columns = list(data[0].keys())

                self.x_dropdown.addItems(columns)
                self.y_dropdown.addItems(columns)

                # Set default selections
                if "Region" in columns:
                    self.x_dropdown.setCurrentText("Region")
                if "Sales" in columns:
                    self.y_dropdown.setCurrentText("Sales")

                self.load_data()

        except Exception as e:
            print("Error loading columns:", e)

    # 🔹 Fetch filtered data
    def fetch_data(self):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        params = {
            "x": self.x_dropdown.currentText(),
            "y": self.y_dropdown.currentText(),
            "agg": self.agg_dropdown.currentText()
        }

        try:
            res = requests.get(f"{API_BASE}/data/aggregate", headers=headers, params=params)
            return res.json()
        except Exception as e:
            print("API Error:", e)
            return []

    # 🔹 Chart
    def create_chart(self, data):
        chart_type = self.chart_type_dropdown.currentText()

        if chart_type == "Bar":
            self.create_bar_chart(data)
        elif chart_type == "Pie":
            self.create_pie_chart(data)
        elif chart_type == "Line":
            self.create_line_chart(data)
            
        series = QBarSeries()
        bar_set = QBarSet(self.agg_dropdown.currentText())

        categories = []
        total = 0

        for row in data:
            values = list(row.values())
            categories.append(str(values[0]))
            value = values[1]

            bar_set << value
            total += value

        series.append(bar_set)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Dynamic Data Chart")

        self.chart_view.setChart(chart)

        # KPI
        avg = total / len(data) if data else 0

        self.kpi_total.setText(f"Total: {round(total, 2)}")
        self.kpi_avg.setText(f"Average: {round(avg, 2)}")

    # 🔹 Load data
    def load_data(self):
        data = self.fetch_data()

        if isinstance(data, dict) and "error" in data:
            print("Error:", data["error"])
            return

        self.create_chart(data)
        
        
    def populate_table(self, data):
        if not data:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return

        columns = list(data[0].keys())

        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.setRowCount(len(data))

        for row_idx, row in enumerate(data):
            for col_idx, col in enumerate(columns):
                item = QTableWidgetItem(str(row[col]))
                self.table.setItem(row_idx, col_idx, item)

        self.table.resizeColumnsToContents()
        
        
        
    def load_data(self):
        data = self.fetch_data()

        if isinstance(data, dict) and "error" in data:
            print("Error:", data["error"])
            return

        self.current_data = data
        self.search_box.clear()   # ✅ Reset search


        self.create_chart(data)
        self.populate_table(data)
        
        
    def export_to_excel(self):
        if not hasattr(self, "current_data") or not self.current_data:
            QMessageBox.warning(self, "No Data", "No data to export")
            return

        # Save dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            "dashboard_export.xlsx",
            "Excel Files (*.xlsx)"
        )

        if not file_path:
            return

        try:
            df = pd.DataFrame(self.current_data)
            df.to_excel(file_path, index=False)

            QMessageBox.information(self, "Success", "File exported successfully")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            
            
    def create_bar_chart(self, data):
        series = QBarSeries()
        bar_set = QBarSet(self.agg_dropdown.currentText())

        total = 0

        for row in data:
            value = list(row.values())[1]
            bar_set << value
            total += value

        series.append(bar_set)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Bar Chart")

        self.chart_view.setChart(chart)
        self.update_kpi(data, total)
        
        
        
    def create_pie_chart(self, data):
        series = QPieSeries()

        total = 0

        for row in data:
            key = list(row.values())[0]
            value = list(row.values())[1]

            series.append(str(key), value)
            total += value

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Pie Chart")

        self.chart_view.setChart(chart)
        self.update_kpi(data, total)
        
        
    def create_line_chart(self, data):
        series = QLineSeries()

        total = 0

        for i, row in enumerate(data):
            value = list(row.values())[1]
            series.append(i, value)
            total += value

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Line Chart")

        self.chart_view.setChart(chart)
        self.update_kpi(data, total)
        
        
    def update_kpi(self, data, total):
        avg = total / len(data) if data else 0

        self.kpi_total.setText(f"Total: {round(total, 2)}")
        self.kpi_avg.setText(f"Average: {round(avg, 2)}")
        
        
    def apply_search(self):
        if not hasattr(self, "current_data"):
            return

        text = self.search_box.text().lower()

        if not text:
            filtered_data = self.current_data
        else:
            filtered_data = []

            for row in self.current_data:
                for value in row.values():
                    if text in str(value).lower():
                        filtered_data.append(row)
                        break

        # Update UI
        self.populate_table(filtered_data)
        self.create_chart(filtered_data)
        
        
    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File",
            "",
            "Excel Files (*.xlsx *.xls)"
        )

        if not file_path:
            return

        url = "http://127.0.0.1:8000/api/v1/upload/"

        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        try:
            with open(file_path, "rb") as f:
                files = {"file": f}
                res = requests.post(url, headers=headers, files=files)

            data = res.json()

            if "preview" in data:
                self.show_preview(data["preview"])
                QMessageBox.information(self, "Success", "File uploaded successfully")

                # 🔄 Refresh dashboard
                self.load_columns()

            else:
                QMessageBox.warning(self, "Error", "Invalid file")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            
            
    def show_preview(self, data):
        if not data:
            return

        columns = list(data[0].keys())

        self.preview_table.setColumnCount(len(columns))
        self.preview_table.setHorizontalHeaderLabels(columns)
        self.preview_table.setRowCount(len(data))

        for row_idx, row in enumerate(data):
            for col_idx, col in enumerate(columns):
                item = QTableWidgetItem(str(row[col]))
                self.preview_table.setItem(row_idx, col_idx, item)

        self.preview_table.resizeColumnsToContents()