from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QWidget, QGridLayout
)
from PyQt5.QtCore import Qt
import pyqtgraph as pg
import pandas as pd


class GraphDashboard(QDialog):
    def __init__(self, df, parent=None):
        super().__init__(parent)

        self.df = df.copy()

        self.setWindowTitle("⚡ Fast Dashboard (PyQtGraph)")
        self.resize(1100, 700)

        main_layout = QVBoxLayout()

        # ================= CONTROLS =================
        control_layout = QHBoxLayout()

        self.x_col = QComboBox()
        self.y_col = QComboBox()
        self.agg = QComboBox()
        self.agg.addItems(["Sum", "Count", "Average"])

        for col in df.columns:
            self.x_col.addItem(str(col))
            self.y_col.addItem(str(col))

        # Auto numeric Y
        numeric_cols = df.select_dtypes(include='number').columns
        if len(numeric_cols) > 0:
            self.y_col.setCurrentText(numeric_cols[0])

        self.btn_update = QPushButton("🔄 Refresh")

        control_layout.addWidget(QLabel("X"))
        control_layout.addWidget(self.x_col)
        control_layout.addWidget(QLabel("Y"))
        control_layout.addWidget(self.y_col)
        control_layout.addWidget(self.agg)
        control_layout.addWidget(self.btn_update)

        main_layout.addLayout(control_layout)

        # ================= GRID =================
        self.grid_widget = QWidget()
        self.grid = QGridLayout(self.grid_widget)
        main_layout.addWidget(self.grid_widget)

        self.setLayout(main_layout)

        self.btn_update.clicked.connect(self.update_dashboard)

        # Style
        pg.setConfigOptions(antialias=True)

        self.update_dashboard()

    # ================= UPDATE =================
    def update_dashboard(self):
        print("⚡ Updating PyQtGraph Dashboard...")

        x = self.x_col.currentText()
        y = self.y_col.currentText()
        agg = self.agg.currentText()

        df = self.df.copy()

        # Safe numeric
        df[y] = pd.to_numeric(df[y], errors='coerce')
        df = df.dropna(subset=[y])

        if df.empty:
            self.show_empty()
            return

        # Aggregation
        agg_map = {
            "Sum": "sum",
            "Average": "mean",
            "Count": "count"
        }

        grouped = df.groupby(x)[y].agg(agg_map.get(agg)).reset_index()

        grouped = grouped.sort_values(by=y, ascending=False).head(8)

        categories = grouped[x].astype(str).tolist()
        values = grouped[y].tolist()

        # Clear old charts
        for i in reversed(range(self.grid.count())):
            widget = self.grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # ================= BAR CHART =================
        bar_plot = pg.PlotWidget(title="Bar Chart")
        x_pos = list(range(len(values)))

        bar_item = pg.BarGraphItem(x=x_pos, height=values, width=0.6)
        bar_plot.addItem(bar_item)

        bar_plot.getAxis('bottom').setTicks([list(zip(x_pos, categories))])

        self.grid.addWidget(bar_plot, 0, 0)

        # ================= LINE CHART =================
        line_plot = pg.PlotWidget(title="Line Chart")
        line_plot.plot(values, symbol='o')
        line_plot.getAxis('bottom').setTicks([list(zip(x_pos, categories))])

        self.grid.addWidget(line_plot, 0, 1)

        # ================= PIE (FAKE USING BAR %) =================
        pie_plot = pg.PlotWidget(title="Distribution (%)")

        total = sum(values)
        if total == 0:
            percents = [0]*len(values)
        else:
            percents = [(v/total)*100 for v in values]

        pie_plot.plot(percents, symbol='o')
        pie_plot.getAxis('bottom').setTicks([list(zip(x_pos, categories))])

        self.grid.addWidget(pie_plot, 1, 0)

        # ================= HORIZONTAL =================
        hbar_plot = pg.PlotWidget(title="Horizontal View")

        for i, val in enumerate(values):
            hbar_plot.plot([0, val], [i, i], pen=pg.mkPen(width=5))

        hbar_plot.getAxis('left').setTicks([list(zip(x_pos, categories))])

        self.grid.addWidget(hbar_plot, 1, 1)

    # ================= EMPTY =================
    def show_empty(self):
        label = QLabel("No Data Available")
        label.setAlignment(Qt.AlignCenter)

        for i in reversed(range(self.grid.count())):
            widget = self.grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        self.grid.addWidget(label, 0, 0)