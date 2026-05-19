import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyqtgraph as pg
from openpyxl import Workbook
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
)
from PySide6.QtCore import Qt

class SignalAnalyzer:
    """
    Contient la logique métier.
    Séparée de l'UI.
    """

    @staticmethod
    def detect_peaks(signal: np.ndarray, threshold: float = 1.0):
        """
        Détecte les valeurs supérieures à un seuil.
        """
        peaks = np.where(signal > threshold)[0]
        return peaks.tolist()

    @staticmethod
    def compute_statistics(signal: np.ndarray):
        """
        Retourne quelques statistiques simples.
        """
        return {
            "mean": float(np.mean(signal)),
            "max": float(np.max(signal)),
            "min": float(np.min(signal)),
            "std": float(np.std(signal)),
        }


class MainWindow(QMainWindow):
    """
    Fenêtre principale.
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Signal Viewer")
        self.resize(1200, 700)

        self.dataframe = None

        self.setup_ui()

    def setup_ui(self):
            """
            Construction de l'interface.
            """

            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            main_layout = QVBoxLayout()
            button_layout = QHBoxLayout()

            self.info_label = QLabel("Charge un fichier CSV")

            self.load_button = QPushButton("Load CSV")
            self.load_button.clicked.connect(self.load_csv)

            self.export_button = QPushButton("Export Excel")
            self.export_button.clicked.connect(self.export_excel)

            self.plot_widget = pg.PlotWidget()
            self.plot_widget.showGrid(x=True, y=True)
            self.plot_widget.addLegend()

            button_layout.addWidget(self.load_button)
            button_layout.addWidget(self.export_button)

            main_layout.addLayout(button_layout)
            main_layout.addWidget(self.info_label)
            main_layout.addWidget(self.plot_widget)

            central_widget.setLayout(main_layout)
    def load_csv(self):
        """
        Charge un fichier CSV.
        """

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            "",
            "CSV Files (*.csv)",
        )

        if not file_path:
            return

        try:
            self.dataframe = pd.read_csv(file_path)
            self.display_signals()
            self.info_label.setText(f"Loaded: {Path(file_path).name}")

        except Exception as error:
            QMessageBox.critical(self, "Error", str(error))
                
    def display_signals(self):
        """
        Affiche les signaux dans le graphique.
        """
        colors = ["r", "b"]

        for index, column in enumerate(self.dataframe.columns):
            if column == "Time":
                continue

            signal = self.dataframe[column]
            time = self.dataframe["Time"]

            color = colors[index % len(colors)]

            # Courbe principale
            self.plot_widget.plot(
                time,
                signal,
                pen=pg.mkPen(color=color, width=2),
                name=column,
            )

            # Régression linéaire
            coefficients = np.polyfit(time, signal, 1)
            regression_line = np.polyval(coefficients, time)

            self.plot_widget.plot(
                time,
                regression_line,
                pen=pg.mkPen(color=color, style=Qt.DashLine),
                name=f"{column} Regression",
            )

    def export_excel(self):
        """
        Exporte les statistiques dans Excel.
        """

        if self.dataframe is None:
            QMessageBox.warning(self, "Warning", "No data loaded")
            return

        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "Statistics"

        worksheet.append(["Signal", "Mean", "Max", "Min", "Std"])

        for column in self.dataframe.columns:
            if column == "Time":
                continue

            stats = SignalAnalyzer.compute_statistics(
                self.dataframe[column].to_numpy()
            )

            worksheet.append([
                column,
                stats["mean"],
                stats["max"],
                stats["min"],
                stats["std"],
            ])

        output_path = "signal_statistics.xlsx"
        workbook.save(output_path)

        QMessageBox.information(
            self,
            "Success",
            f"Excel exported: {output_path}",
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())