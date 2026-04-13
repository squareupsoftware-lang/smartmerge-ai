from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QWidget, QGridLayout, QTabWidget
)
from PyQt5.QtCore import Qt
import pyqtgraph as pg
import pandas as pd
import json
import tempfile
from reportlab.platypus import SimpleDocTemplate, Image


class ProDashboard(QDialog):
    def __init__(self, df, parent=None):
        super().__init__(parent)

        self.original_df = df.copy()
        self.df = df.copy()

        self.setWindowTitle("🚀 Enterprise Dashboard")
        self.resize(1200, 750)

        pg.setConfigOptions(antialias=True)

        main_layout = QVBoxLayout()

        # ================= TABS =================
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.main_tab = QWidget()
        self.tabs.addTab(self.main_tab, "Dashboard")

        self.layout_main = QVBoxLayout(self.main_tab)

        # ================= CONTROLS =================
        control_layout = QHBoxLayout()
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(["Dark", "Light", "Blue", "Corporate"])

        control_layout.addWidget(QLabel("Theme"))
        control_layout.addWidget(self.theme_selector)
        
        self.x_col = QComboBox()
        self.y_col = QComboBox()
        self.agg = QComboBox()
        self.agg.addItems(["Sum", "Count", "Average"])

        self.filter_col = QComboBox()
        self.filter_val = QComboBox()

        for col in df.columns:
            self.x_col.addItem(col)
            self.y_col.addItem(col)
            self.filter_col.addItem(col)

        numeric_cols = df.select_dtypes(include='number').columns
        if len(numeric_cols):
            self.y_col.setCurrentText(numeric_cols[0])

        # Buttons
        self.btn_update = QPushButton("🔄 Refresh")
        self.btn_reset = QPushButton("Reset")
        self.btn_save = QPushButton("💾 Save")
        self.btn_load = QPushButton("📂 Load")
        self.btn_pdf = QPushButton("📄 PDF")
        self.btn_ai = QPushButton("🧠 Insights")

        control_layout.addWidget(QLabel("X"))
        control_layout.addWidget(self.x_col)
        control_layout.addWidget(QLabel("Y"))
        control_layout.addWidget(self.y_col)
        control_layout.addWidget(self.agg)

        control_layout.addWidget(QLabel("Filter"))
        control_layout.addWidget(self.filter_col)
        control_layout.addWidget(self.filter_val)

        control_layout.addWidget(self.btn_update)
        control_layout.addWidget(self.btn_reset)
        control_layout.addWidget(self.btn_save)
        control_layout.addWidget(self.btn_load)
        control_layout.addWidget(self.btn_pdf)
        control_layout.addWidget(self.btn_ai)

        self.layout_main.addLayout(control_layout)

        # ================= KPI =================
        self.kpi_layout = QHBoxLayout()
        self.layout_main.addLayout(self.kpi_layout)

        # ================= GRID =================
        self.grid_widget = QWidget()
        self.grid = QGridLayout(self.grid_widget)
        self.layout_main.addWidget(self.grid_widget)

        self.setLayout(main_layout)

        # ================= EVENTS =================
        self.btn_update.clicked.connect(self.update_dashboard)
        self.btn_reset.clicked.connect(self.reset_dashboard)
        self.btn_save.clicked.connect(self.save_dashboard)
        self.btn_load.clicked.connect(self.load_dashboard)
        self.btn_pdf.clicked.connect(self.export_pdf)
        self.btn_ai.clicked.connect(self.run_insights)

        self.theme_selector.currentTextChanged.connect(self.apply_theme)
        self.filter_col.currentIndexChanged.connect(self.update_filter_values)

        self.update_filter_values()
        self.update_dashboard()

        # ================= THEME =================
        self.setStyleSheet("""
        QWidget { background-color: #0f172a; color: white; }
        QPushButton, QComboBox {
            background:#1e293b; padding:5px; border-radius:5px;
        }
        """)
        
    def apply_theme(self, theme):
        if theme == "Dark":
            self.setStyleSheet("""
            QWidget { background:#0f172a; color:white; }
            QPushButton, QComboBox { background:#1e293b; padding:5px; }
            """)

        elif theme == "Light":
            self.setStyleSheet("""
            QWidget { background:white; color:black; }
            QPushButton, QComboBox { background:#e5e7eb; }
            """)

        elif theme == "Blue":
            self.setStyleSheet("""
            QWidget { background:#0a192f; color:#64ffda; }
            QPushButton { background:#112240; }
            """)

        elif theme == "Corporate":
            self.setStyleSheet("""
            QWidget { background:#f4f6f9; color:#2c3e50; }
            QPushButton { background:#3498db; color:white; }
            """)

    # ================= KPI =================
    def create_kpi(self, title, value):
        box = QVBoxLayout()
        t = QLabel(title)
        v = QLabel(value)
        v.setStyleSheet("font-size:20px; font-weight:bold; color:#00ffcc;")
        box.addWidget(t)
        box.addWidget(v)

        w = QWidget()
        w.setLayout(box)
        w.setStyleSheet("background:#1e293b; padding:10px; border-radius:10px;")
        return w

    def update_kpis(self, df, y):
        for i in reversed(range(self.kpi_layout.count())):
            self.kpi_layout.itemAt(i).widget().setParent(None)

        self.kpi_layout.addWidget(self.create_kpi("Total", f"{df[y].sum():,.0f}"))
        self.kpi_layout.addWidget(self.create_kpi("Average", f"{df[y].mean():,.0f}"))
        self.kpi_layout.addWidget(self.create_kpi("Max", f"{df[y].max():,.0f}"))

    # ================= FILTER =================
    def update_filter_values(self):
        col = self.filter_col.currentText()
        self.filter_val.clear()

        if col in self.df.columns:
            vals = self.df[col].dropna().astype(str).unique()
            self.filter_val.addItem("All")
            self.filter_val.addItems(sorted(vals))

    def apply_filter(self, df):
        col = self.filter_col.currentText()
        val = self.filter_val.currentText()
        if val != "All":
            df = df[df[col].astype(str) == val]
        return df

    # ================= MAIN =================
    def update_dashboard(self):
        x = self.x_col.currentText()
        y = self.y_col.currentText()
        agg = self.agg.currentText()

        df = self.apply_filter(self.original_df.copy())
        df[y] = pd.to_numeric(df[y], errors='coerce')
        df = df.dropna(subset=[y])

        if df.empty:
            self.show_empty()
            return

        grouped = df.groupby(x)[y].agg({
            "Sum": "sum",
            "Average": "mean",
            "Count": "count"
        }[agg]).reset_index()

        grouped = grouped.sort_values(by=y, ascending=False).head(8)

        categories = grouped[x].astype(str).tolist()
        values = grouped[y].tolist()

        self.update_kpis(df, y)

        # Clear grid
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w:
                w.setParent(None)

        x_pos = list(range(len(values)))

        # ================= BAR =================
        bar = pg.PlotWidget(title="Bar Chart")
        bar.addItem(pg.BarGraphItem(x=x_pos, height=values, width=0.6))
        bar.getAxis('bottom').setTicks([list(zip(x_pos, categories))])
        self.grid.addWidget(bar, 0, 0)

        # ================= LINE =================
        line = pg.PlotWidget(title="Trend")
        line.plot(values, symbol='o')
        line.getAxis('bottom').setTicks([list(zip(x_pos, categories))])
        self.grid.addWidget(line, 0, 1)

        # ================= DISTRIBUTION =================
        dist = pg.PlotWidget(title="Distribution %")
        total = sum(values)
        perc = [(v/total)*100 if total else 0 for v in values]
        dist.plot(perc, symbol='o')
        dist.getAxis('bottom').setTicks([list(zip(x_pos, categories))])
        self.grid.addWidget(dist, 1, 0)

        # ================= HORIZONTAL =================
        h = pg.PlotWidget(title="Horizontal")
        for i, v in enumerate(values):
            h.plot([0, v], [i, i], pen=pg.mkPen(width=5))
        h.getAxis('left').setTicks([list(zip(x_pos, categories))])
        self.grid.addWidget(h, 1, 1)

    # ================= SAVE / LOAD =================
    def save_dashboard(self):
        state = {
            "x": self.x_col.currentText(),
            "y": self.y_col.currentText(),
            "agg": self.agg.currentText(),
            "filter_col": self.filter_col.currentText(),
            "filter_val": self.filter_val.currentText()
        }
        with open("dashboard_layout.json", "w") as f:
            json.dump(state, f)

    def load_dashboard(self):
        try:
            with open("dashboard_layout.json", "r") as f:
                s = json.load(f)

            self.x_col.setCurrentText(s["x"])
            self.y_col.setCurrentText(s["y"])
            self.agg.setCurrentText(s["agg"])
            self.filter_col.setCurrentText(s["filter_col"])
            self.filter_val.setCurrentText(s["filter_val"])

            self.update_dashboard()
        except Exception as e:
            print("Load error:", e)

    # ================= PDF =================
    def export_pdf(self):
        doc = SimpleDocTemplate("dashboard.pdf")
        elements = []

        for i in range(self.grid.count()):
            w = self.grid.itemAt(i).widget()
            if hasattr(w, "grab"):
                pix = w.grab()
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                pix.save(tmp.name)
                elements.append(Image(tmp.name, width=400, height=250))

        doc.build(elements)

    # ================= INSIGHTS =================
    def run_insights(self):
        df = self.original_df.copy()
        y = self.y_col.currentText()
        x = self.x_col.currentText()

        df[y] = pd.to_numeric(df[y], errors='coerce')
        df = df.dropna()

        top = df.sort_values(by=y, ascending=False).iloc[0]
        avg = df[y].mean()

        text = f"""
🏆 Top {x}: {top[x]} ({top[y]:,.0f})
📊 Average {y}: {avg:,.0f}
"""

        label = QLabel(text)
        label.setStyleSheet("color: yellow;")
        self.grid.addWidget(label, 2, 0, 1, 2)

    # ================= RESET =================
    def reset_dashboard(self):
        self.df = self.original_df.copy()
        self.filter_val.setCurrentText("All")
        self.update_dashboard()

    def show_empty(self):
        label = QLabel("No Data Available")
        label.setAlignment(Qt.AlignCenter)
        self.grid.addWidget(label, 0, 0)