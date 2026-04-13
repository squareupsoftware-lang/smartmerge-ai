from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QFileDialog, QListWidget, QListWidgetItem, QTableView,
    QLineEdit, QTableWidget, QTableWidgetItem, QComboBox,
    QMessageBox, QSizePolicy, QHeaderView, QDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis

import pandas as pd

from logic.file_loader import FileLoader
from logic.data_cleaner import DataCleaner
from ui.mapping_canvas import MappingCanvas
#from ui.graph_dashboard import GraphDashboard
from ui.pro_dashboard import ProDashboard
from rapidfuzz import fuzz
from ui.dashboard import Dashboard

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CleanMerge Studio")
        self.setGeometry(200, 200, 900, 600)

        self.file_loader = FileLoader()
        self.data_cleaner = DataCleaner()

        self.filters = []
        self.current_df = None
        self.final_df = None

        self.init_ui()

    # ================= UI =================
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.setStyleSheet("""
        QMainWindow {
            background-color: #fc9b3a;
            color: white;
        }
        
        QPushButton {
        color: #333;
        border: 2px solid #555;
        border-radius: 11px;
        padding: 5px;
        font-size: 12px;
        padding-left: 10px;
        padding-right: 10px;
        font: bold;
        background: qradialgradient(cx: 0.3, cy: -0.4,
        fx: 0.3, fy: -0.4,
        radius: 1.35, stop: 0 #fff, stop: 1 #888);
        }
        
        QPushButton:hover {
        background: qradialgradient(cx: 0.3, cy: -0.4,
        fx: 0.3, fy: -0.4,
        radius: 1.35, stop: 0 #fff, stop: 1 #bbb);
        }
        
        QPushButton:pressed {
        background: qradialgradient(cx: 0.4, cy: -0.1,
        fx: 0.4, fy: -0.1,
        radius: 1.35, stop: 0 #fff, stop: 1 #ddd);
        }
        
        QPushButton:focus{
        border: 2px solid rgb(255, 85, 0);
        background: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0.011, stop:0.602273 rgba(255, 119, 0, 248));
        }
        """)
        layout = QVBoxLayout()

        # -------- Extensions
        self.ext_list = QListWidget()
        for ext in [".csv", ".xlsx", ".xls", ".txt"]:
            item = QListWidgetItem(ext)
            item.setCheckState(Qt.Checked)
            self.ext_list.addItem(item)
        self.ext_list.setFixedHeight(125)
        self.ext_list.itemChanged.connect(self.refresh_file_list)

        # -------- File Section
        self.label = QLabel("Select Folder")
        self.btn_browse = QPushButton("Browse Folder")
        self.file_list = QListWidget()        
        self.file_list.setFixedHeight(155)
        self.file_list.setSelectionMode(QListWidget.MultiSelection)

        # -------- Column Section
        self.col_list = QListWidget()
        self.col_list.setFixedHeight(155)

        # -------- Mapping Table
        self.mapping_table = QTableWidget()
        self.mapping_table.setColumnCount(2)
        self.mapping_table.setHorizontalHeaderLabels(["Target Column", "Map From"])

        # -------- Data Table
        self.table = QTableView()    
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.resizeRowsToContents()

        # -------- Filters
        self.filter_col = QComboBox()
        self.filter_col.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.filter_op = QComboBox()
        self.filter_op.addItems(["=", "!=", ">", "<", ">=", "<=", "contains"])
        self.filter_value = QLineEdit()

        self.btn_apply_filter = QPushButton("Apply Filter")
        self.btn_add_filter = QPushButton("Add Filter")
        self.btn_clear_filter = QPushButton("Clear Filter")
        self.btn_process = QPushButton("Merge & Apply Filters")
        self.btn_export = QPushButton("Export")

        self.mapping_canvas = MappingCanvas()
        self.mapping_canvas.setAcceptDrops(True)
        self.mapping_canvas.setDragDropMode(QListWidget.InternalMove)
        
        self.filter_list = QListWidget()        
        self.filter_list.setFixedHeight(80)
        
        # -------- Modern Sidebar (Navigation Panel)
        self.sidebar = QVBoxLayout()

        self.btn_dashboard = QPushButton("📊 Dashboard")
        self.btn_data = QPushButton("📁 Data")
        self.btn_transform = QPushButton("⚙ Transform")
        self.btn_visual = QPushButton("📈 Visualize")
        self.btn_export = QPushButton("⬇ Export")
        
        for btn in [self.btn_dashboard, self.btn_data, self.btn_transform, self.btn_visual, self.btn_export]:
            btn.setFixedHeight(40)
            btn.setStyleSheet("text-align:left; padding-left:10px;")
        
        self.sidebar.addWidget(self.btn_dashboard)
        self.sidebar.addWidget(self.btn_data)
        self.sidebar.addWidget(self.btn_transform)
        self.sidebar.addWidget(self.btn_visual)
        self.sidebar.addWidget(self.btn_export)
        self.sidebar.addStretch()

        # -------- Top Toolbar (Like Power BI Ribbon)
        toolbar = QHBoxLayout()

        self.btn_upload = QPushButton("Upload")
        self.btn_refresh = QPushButton("Refresh")
        self.btn_ai_map = QPushButton("🤖 Auto Map")
        
        toolbar.addWidget(self.btn_upload)
        toolbar.addWidget(self.btn_refresh)
        toolbar.addWidget(self.btn_ai_map)
        toolbar.addStretch()

        self.x_axis_col = QComboBox()
        self.y_axis_col = QComboBox()
        self.btn_dashboard = QPushButton("🚀 Open Pro Dashboard")

        # -------- Layouts
        left = QVBoxLayout()
        left.addWidget(QLabel("Extensions"))
        left.addWidget(self.ext_list)
        left.addWidget(self.btn_browse)

        center1 = QVBoxLayout()
        center1.addWidget(self.label)
        center1.addWidget(self.file_list)

        center2 = QVBoxLayout()
        center2.addWidget(QLabel("Columns"))
        center2.addWidget(self.col_list)
        
        center3 = QVBoxLayout()        
        center3.addWidget(QLabel("Applied Filters"))
        center3.addWidget(self.filter_list)
        center3.addWidget(self.filter_col)
        center3.addWidget(self.filter_op)
        center3.addWidget(self.filter_value)
        
        right = QVBoxLayout()
        right.addWidget(self.btn_add_filter)
        right.addWidget(self.btn_apply_filter)
        right.addWidget(self.btn_clear_filter)              
        right.addWidget(self.btn_process)
        right.addWidget(self.btn_export)
        
        chart_controls = QVBoxLayout()
        chart_controls.addWidget(QLabel("X-Axis"))
        chart_controls.addWidget(self.x_axis_col)
        chart_controls.addWidget(QLabel("Y-Axis"))
        chart_controls.addWidget(self.y_axis_col)
        chart_controls.addWidget(self.btn_dashboard)

        top_layout = QHBoxLayout()
        top_layout.addLayout(left, 1)
        top_layout.addLayout(center1, 2)
        top_layout.addLayout(center2, 2)
        top_layout.addLayout(center3, 2)
        top_layout.addLayout(right, 1)
        top_layout.addLayout(chart_controls, 1)

        layout.addLayout(top_layout)
        layout.addWidget(QLabel("Column Mapping"))
        layout.addWidget(self.mapping_table, 1)
        layout.addWidget(self.table, 4)        
        self.chart_container = QVBoxLayout()
        layout.addLayout(self.chart_container)

        #filter_layout = QHBoxLayout()        
        #filter_layout.addWidget(self.btn_process)
        #filter_layout.addWidget(self.btn_export)

        #layout.addLayout(filter_layout)

        central_widget.setLayout(layout)

        self.status_bar = self.statusBar()

        # -------- Events
        self.btn_browse.clicked.connect(self.select_folder)
        self.file_list.itemChanged.connect(self.handle_file_selection)

        self.btn_apply_filter.clicked.connect(self.apply_filter)
        self.btn_add_filter.clicked.connect(self.add_filter)
        self.btn_clear_filter.clicked.connect(self.clear_filters)
        self.filter_list.itemChanged.connect(self.on_filter_toggle)
        self.btn_process.clicked.connect(self.process_all_files)
        self.btn_export.clicked.connect(self.export_data)
        self.btn_ai_map.clicked.connect(self.run_auto_mapping)
        #self.x_axis_col.currentIndexChanged.connect(self.update_chart)
        #self.y_axis_col.currentIndexChanged.connect(self.update_chart)
        try:
            self.btn_dashboard.clicked.disconnect()
        except:
            pass

        self.btn_dashboard.clicked.connect(self.show_dashboard)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
        QTableView {
             selection-background-color: rgb(236, 68, 1);            
         }
        
        QTableView QTableCornerButton::section {
             background: blue;
             border: 2px outset blue;
         }
        
        QHeaderView {
        	background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 #a6a6a6, stop: 0.08 #7f7f7f,
            stop: 0.39999 #717171, stop: 0.4 #626262,
            stop: 0.9 #4c4c4c, stop: 1 #333333);
            font-weight:bold;
        }
        """)

        self.col_list.setDragEnabled(True)
        self.mapping_table.setDragEnabled(True)
        self.mapping_table.setAcceptDrops(True)

    # ================= File Handling =================
    def get_selected_extensions(self):
        return [
            self.ext_list.item(i).text()
            for i in range(self.ext_list.count())
            if self.ext_list.item(i).checkState() == Qt.Checked
        ]

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")

        if folder:
            self.file_loader.set_folder(folder)
            self.file_loader.set_extensions(self.get_selected_extensions())

            files = self.file_loader.get_files()

            self.file_list.clear()
            for file in files:
                item = QListWidgetItem(file)
                item.setCheckState(Qt.Unchecked)   # ✅ checkbox added
                self.file_list.addItem(item)

            self.label.setText(f"Loaded: {folder}")

    def refresh_file_list(self):
        if not self.file_loader.folder_path:
            return

        self.file_loader.set_extensions(self.get_selected_extensions())
        files = self.file_loader.get_files()

        self.file_list.clear()
        for file in files:
            item = QListWidgetItem(file)
            item.setCheckState(Qt.Unchecked)   # ✅ checkbox added
            self.file_list.addItem(item)

    def get_selected_files(self):
        selected_files = []
    
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if item.checkState() == Qt.Checked:
                selected_files.append(item.text())
    
        return selected_files

    # ================= Column Handling =================
    def analyze_columns(self, selected_files):
        folder = self.file_loader.folder_path

        file_columns = {}
        all_cols = set()

        for file in selected_files:
            cols = self.data_cleaner.get_columns(folder, file)
            file_columns[file] = set(cols)
            all_cols.update(cols)

        common_cols = set.intersection(*file_columns.values()) if file_columns else set()

        missing_info = {
            file: all_cols - cols
            for file, cols in file_columns.items()
            if all_cols - cols
        }

        return list(common_cols), missing_info, list(all_cols)

    def handle_file_selection(self):
        print("STEP 1: handle_file_selection triggered")
    
        self.file_list.blockSignals(True)
    
        try:
            selected_files = self.get_selected_files()
            print("STEP 2: selected_files =", selected_files)
    
            if not selected_files:
                print("STEP 3: no files selected")
                return
    
            folder = self.file_loader.folder_path
            print("STEP 4: folder =", folder)
    
            # ================= SINGLE FILE =================
            if len(selected_files) == 1:
                print("STEP 5: single file mode")

                file = selected_files[0]
                df = self.data_cleaner.load_file(folder, file)

                print("STEP 6: df loaded =", type(df))

                if df is None:
                    print("STEP 7: df is None")
                    return

                self.current_df = df

                cols = list(df.columns)
                print("STEP 9: columns =", cols)

                # ✅ UI FIRST
                self.col_list.clear()
                self.filter_col.clear()

                for col in cols:
                    item = QListWidgetItem(str(col))
                    item.setCheckState(Qt.Checked)
                    self.col_list.addItem(item)
                    self.filter_col.addItem(str(col))

                print("STEP 10: mapping setup")
                self.setup_single_file_mapping(cols)

                # ✅ DISPLAY LAST
                self.display_data(df)
    
            # ================= MULTI FILE =================
            else:
                print("STEP 11: multi-file mode")

                common_cols, missing_info, all_cols = self.analyze_columns(selected_files)

                print("STEP 12: common_cols =", common_cols)

                self.col_list.clear()
                self.filter_col.clear()

                for col in common_cols:
                    item = QListWidgetItem(str(col))
                    item.setCheckState(Qt.Checked)
                    self.col_list.addItem(item)
                    self.filter_col.addItem(str(col))

                print("STEP 13: setup mapping")
                self.setup_multi_file_mapping(selected_files)

                df = self.data_cleaner.load_file(folder, selected_files[0])

                print("STEP 14: preview df =", type(df))

                if df is not None:
                    self.current_df = df

                    # ✅ DISPLAY LAST
                    self.display_data(df)
    
            print("STEP 16: UI update")
            self.table.viewport().update()
    
        except Exception as e:
            import traceback
            print("CRASH HERE:", e)
            traceback.print_exc()
    
        finally:
            self.file_list.blockSignals(False)
            print("STEP 17: done")
        # 🔥 Re-enable signals
        self.file_list.blockSignals(False)

    def setup_single_file_mapping(self, cols):
        self.mapping_table.setRowCount(len(cols))
    
        for i, col in enumerate(cols):
            self.mapping_table.setItem(i, 0, QTableWidgetItem(col))
    
            combo = QComboBox()
            combo.addItem(col)
            combo.setCurrentText(col)
    
            self.mapping_table.setCellWidget(i, 1, combo)

    def setup_multi_file_mapping(self, selected_files):
        folder = self.file_loader.folder_path
    
        row = 0
        self.mapping_table.setRowCount(0)
    
        for file in selected_files:
            cols = self.data_cleaner.get_columns(folder, file)
    
            for col in cols:
                self.mapping_table.insertRow(row)
    
                # Target column (editable)
                target_item = QTableWidgetItem(col)
                self.mapping_table.setItem(row, 0, target_item)
    
                # Source (show file + column)
                combo = QComboBox()
                combo.addItem(f"{file} -> {col}")
    
                self.mapping_table.setCellWidget(row, 1, combo)
    
                row += 1

    def setup_mapping_ui(self, all_cols):
        self.mapping_table.setRowCount(len(all_cols))

        for i, col in enumerate(all_cols):
            self.mapping_table.setItem(i, 0, QTableWidgetItem(col))

            combo = QComboBox()
            combo.addItem("")
            combo.addItems(all_cols)

            combo.setCurrentText(col)
            self.mapping_table.setCellWidget(i, 1, combo)

    def get_selected_columns(self):
        return [
            self.col_list.item(i).text()
            for i in range(self.col_list.count())
            if self.col_list.item(i).checkState() == Qt.Checked
        ]

    def get_column_mapping(self):
        mapping = {}
    
        for row in range(self.mapping_table.rowCount()):
            target_item = self.mapping_table.item(row, 0)
            combo = self.mapping_table.cellWidget(row, 1)
    
            if target_item and combo:
                source_text = combo.currentText()
    
                if "->" in source_text:
                    col = source_text.split("->")[1].strip()
                    mapping[col] = target_item.text()
    
        return mapping

    # ================= Preview =================
    def preview_file(self, item):
        folder = self.file_loader.folder_path
        df = self.data_cleaner.load_file(folder, item.text())

        if df is not None:
            self.current_df = df
            self.display_data(df)

    def display_data(self, df):
        if df is None or df.empty:
            return

        model = QStandardItemModel()
        headers = [str(col) for col in df.columns]
        model.setHorizontalHeaderLabels(headers)

        for row in df.values:
            items = [QStandardItem(str(cell)) for cell in row]
            model.appendRow(items)

        self.table.setModel(model)

        # ✅ Prevent duplicate signal connections
        try:
            self.table.selectionModel().selectionChanged.disconnect()
        except:
            pass

        self.table.selectionModel().selectionChanged.connect(self.update_summary)

        # ✅ Update X/Y dropdown
        self.x_axis_col.blockSignals(True)
        self.y_axis_col.blockSignals(True)

        self.x_axis_col.clear()
        self.y_axis_col.clear()

        for col in df.columns:
            self.x_axis_col.addItem(str(col))
            self.y_axis_col.addItem(str(col))

        if self.x_axis_col.count() > 0:
            self.x_axis_col.setCurrentIndex(0)

        if self.y_axis_col.count() > 1:
            self.y_axis_col.setCurrentIndex(1)

        self.x_axis_col.blockSignals(False)
        self.y_axis_col.blockSignals(False)

    # ================= Filters =================
    def apply_filter(self):
        if self.current_df is None:
            return

        col = self.filter_col.currentText()
        op = self.filter_op.currentText()
        val = self.filter_value.text()

        df = self.current_df.copy()

        try:
            if op == "=":
                df = df[df[col] == val]
            elif op == "contains":
                df = df[df[col].astype(str).str.contains(val, case=False)]

            self.display_data(df)
        except Exception as e:
            print("Filter error:", e)

    def add_filter(self):
        col = self.filter_col.currentText()
        op = self.filter_op.currentText()
        val = self.filter_value.text()

        if not col or not val:
            return

        # Store filter
        self.filters.append((col, op, val))

        # ✅ Add to UI list with checkbox
        item_text = f"{col} {op} {val}"
        item = QListWidgetItem(item_text)
        item.setCheckState(Qt.Checked)
        self.filter_list.addItem(item)

        # Apply filters
        if self.current_df is not None:
            filtered_df = self.apply_all_filters(self.current_df.copy())
            self.display_data(filtered_df)

    def apply_all_filters(self, df):
        if df is None or df.empty:
            return df

        filtered_df = df.copy()   # ✅ always work on copy

        for i in range(self.filter_list.count()):
            item = self.filter_list.item(i)

            # Apply only checked filters
            if item.checkState() != Qt.Checked:
                continue

            if i >= len(self.filters):
                continue

            col, op, val = self.filters[i]

            if col not in filtered_df.columns:
                continue

            try:
                temp_col = filtered_df[col]

                # 🔥 Handle numeric filters safely
                if op in [">", "<", ">=", "<="]:
                    temp_col = temp_col.astype(str).str.replace(",", "")
                    temp_col = pd.to_numeric(temp_col, errors='coerce')

                    val_cast = pd.to_numeric(val, errors='coerce')

                    if pd.isna(val_cast):
                        continue

                    if op == ">":
                        filtered_df = filtered_df[temp_col > val_cast]

                    elif op == "<":
                        filtered_df = filtered_df[temp_col < val_cast]

                    elif op == ">=":
                        filtered_df = filtered_df[temp_col >= val_cast]

                    elif op == "<=":
                        filtered_df = filtered_df[temp_col <= val_cast]

                elif op == "=":
                    filtered_df = filtered_df[
                        filtered_df[col].astype(str) == str(val)
                    ]

                elif op == "!=":
                    filtered_df = filtered_df[
                        filtered_df[col].astype(str) != str(val)
                    ]

                elif op == "contains":
                    filtered_df = filtered_df[
                        filtered_df[col].astype(str).str.contains(val, case=False, na=False)
                    ]

            except Exception as e:
                print(f"Filter error on {col}:", e)

        return filtered_df
        
    def on_filter_toggle(self):
        if self.current_df is not None:
            filtered_df = self.apply_all_filters(self.current_df.copy())
            self.display_data(filtered_df)

    # ================= Processing =================
    def process_all_files(self):
        files = self.get_selected_files()
        cols = self.get_selected_columns()
        mapping = self.get_column_mapping()

        folder = self.file_loader.folder_path
        final_df = pd.DataFrame()

        for file in files:
            df = self.data_cleaner.load_file(folder, file)

            if df is not None:
                df = df.rename(columns=mapping)
                df = df[cols]
                df = self.apply_all_filters(df)

                final_df = pd.concat([final_df, df], ignore_index=True)

        self.final_df = final_df
        self.display_data(final_df)
        
    def clear_filters(self):
        self.filters = []
        if self.current_df is not None:
            self.display_data(self.current_df)
        self.filter_list.clear()

    # ================= Export =================
    def export_data(self):
        if self.final_df is None:
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Save File", "", "CSV (*.csv);;Excel (*.xlsx)"
        )

        if path:
            if path.endswith(".csv"):
                self.final_df.to_csv(path, index=False)
            else:
                self.final_df.to_excel(path, index=False)

    # ================= Summary =================
    def update_summary(self):
        indexes = self.table.selectionModel().selectedIndexes()
    
        values = []
    
        for index in indexes:
            try:
                values.append(float(index.data()))
            except:
                pass
    
        if values:
            total = sum(values)
            count = len(values)
            avg = total / count
    
            self.status_bar.showMessage(
                f"Count: {count} | Sum: {total:.2f} | Avg: {avg:.2f}"
            )

    # ================= UI =================
    def show_column_summary(self, common_cols, missing_info):
        msg = "Common Columns:\n"
        msg += ", ".join(common_cols) if common_cols else "None"

        msg += "\n\nMissing Columns:\n"
        for file, cols in missing_info.items():
            msg += f"\n{file}: {', '.join(cols)}"

        QMessageBox.information(self, "Column Analysis", msg)

    def auto_map_columns(self, cols1, cols2):
        mapping = {}
    
        for col1 in cols1:
            best_match = None
            best_score = 0
    
            for col2 in cols2:
                score = fuzz.ratio(col1.lower(), col2.lower())
    
                if score > best_score:
                    best_score = score
                    best_match = col2
    
            if best_score > 60 and best_match:
                mapping[best_match] = col1
    
        return mapping

    def create_kpi_card(title, value):
        box = QVBoxLayout()
        label_title = QLabel(title)
        label_value = QLabel(value)
    
        label_value.setStyleSheet("font-size:20px; font-weight:bold;")
    
        box.addWidget(label_title)
        box.addWidget(label_value)
    
        widget = QWidget()
        widget.setLayout(box)
        widget.setStyleSheet("background:#2c94f5; padding:10px; border-radius:8px;")
        return widget

    def create_bar_chart(self, df):
        if df is None or df.empty:
            return None

        try:
            x_col = self.x_axis_col.currentText()
            y_col = self.y_axis_col.currentText()

            # ✅ VALIDATION FIRST
            if not x_col or not y_col:
                return None

            if x_col not in df.columns or y_col not in df.columns:
                return None

            temp_df = df.copy()

            # ✅ SAFE numeric conversion
            temp_df[y_col] = pd.to_numeric(temp_df[y_col], errors='coerce')

            if temp_df[y_col].isna().all():
                return None

            temp_df = temp_df.dropna(subset=[y_col])

            if temp_df.empty:
                return None

            data = temp_df[[x_col, y_col]].head(10)

            y_values = data[y_col]
            if isinstance(y_values, pd.DataFrame):
                y_values = y_values.iloc[:, 0]

            y_list = [float(v) for v in y_values.tolist()]
            x_labels = data[x_col].astype(str).tolist()

            # ✅ Chart
            bar_set = QBarSet(y_col)
            bar_set.append(y_list)

            series = QBarSeries()
            series.append(bar_set)

            chart = QChart()
            chart.addSeries(series)
            chart.setTitle(f"{y_col} by {x_col}")

            # ✅ X Axis
            axis_x = QBarCategoryAxis()
            axis_x.append(x_labels)

            chart.addAxis(axis_x, Qt.AlignBottom)
            series.attachAxis(axis_x)

            # ✅ Y Axis (VERY IMPORTANT)
            chart.createDefaultAxes()

            chart_view = QChartView(chart)
            chart_view.setRenderHint(QPainter.Antialiasing)
            chart_view.setMinimumHeight(300)
            chart_view.setMinimumWidth(400)

            return chart_view

        except Exception as e:
            print("Chart Error:", e)
            return None

    def run_auto_mapping(self):
        files = self.get_selected_files()
    
        if len(files) < 2:
            return
    
        folder = self.file_loader.folder_path
    
        cols1 = self.data_cleaner.get_columns(folder, files[0])
        cols2 = self.data_cleaner.get_columns(folder, files[1])
    
        mapping = self.auto_map_columns(cols1, cols2)
    
        print("AI Mapping:", mapping)

    def update_chart(self):
        try:
            df = self.current_df

            if df is None or df.empty:
                return

            x_col = self.x_axis_col.currentText()
            y_col = self.y_axis_col.currentText()

            if not x_col or not y_col:
                return

            if x_col not in df.columns or y_col not in df.columns:
                return

            # Clear old chart
            for i in reversed(range(self.chart_container.count())):
                widget = self.chart_container.itemAt(i).widget()
                if widget:
                    widget.setParent(None)

            chart_view = self.create_bar_chart(df)
            self.show_chart_popup(chart_view)

        except Exception as e:
            print("Update Chart Crash:", e)
            
    def show_dashboard(self):
        try:
            if self.current_df is None or self.current_df.empty:
                QMessageBox.warning(self, "Error", "No data available")
                return

            print("Opening dashboard...")
            print(self.current_df.head())

            #self.dashboard = GraphDashboard(self.current_df, self)
            #self.dashboard.setModal(False)
            #self.dashboard.show()
            dlg = ProDashboard(self.current_df, self)
            dlg.exec_()

        except Exception as e:
            print("Dashboard Error:", e)
            
            
    def open_dashboard(token):
        self.dashboard = Dashboard(token)
        self.dashboard.show()