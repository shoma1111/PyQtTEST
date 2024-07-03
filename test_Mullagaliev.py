import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QPushButton, QComboBox, QFileDialog
from PyQt5.QtGui import QColor
import pyqtgraph as pg
from scipy.special import expit
import h5py


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle('test')
        self.setGeometry(350, 25, 600, 700)
        self.data = np.round((np.random.rand(6, 6) - 0.5) *16, 3)

        print(self.data)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout(main_widget)

        titls = ['селектор', 'result', 'expit(x)', '4ст', '5ст', '6ст']
        self.table = QTableWidget(self.data.shape[0], self.data.shape[1])
        self.table.setHorizontalHeaderLabels(titls)
        layout.addWidget(self.table)

        self.graphWidget = pg.PlotWidget()
        layout.addWidget(self.graphWidget)

        self.clear_button = QPushButton("очистить график и выбрать новые столбцы")
        layout.addWidget(self.clear_button)
        self.clear_button.clicked.connect(self.clear_plot)

        self.save_button = QPushButton("сохранить таблицу")
        layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save)

        self.load_button = QPushButton("загрузить таблицу")
        layout.addWidget(self.load_button)
        self.load_button.clicked.connect(self.load)

        self.selected_columns = []

        self.table.cellChanged.connect(self.new_value)
        self.table.horizontalHeader().sectionClicked.connect(self.handle_header_click)

        self.update_table()

    def update_table(self):
        for row in range(self.data.shape[0]):
            for col in range(self.data.shape[1]):
                if col == 0:
                    selector = QComboBox()
                    selector.addItems([str(i) for i in range(1, 6)])
                    selector.setCurrentText(str(int(self.data[row, col])))
                    selector.currentTextChanged.connect(lambda text, r=row, c=col: self.selector_changed(r, c, int(text)))
                    self.table.setCellWidget(row, col, selector)
                else:
                    item = QTableWidgetItem(str(self.data[row, col]))
                    self.table.setItem(row, col, item)
                    self.new_color(row, col)

    def new_color(self, row, col):
        item = self.table.item(row, col)
        if col == 3:
            value = self.data[row, col]
            if value < 0:
                item.setBackground(QColor(255, 0, 0))
            elif value > 0:
                item.setBackground(QColor(0, 255, 0))

    def handle_header_click(self, index):
        if len(self.selected_columns) < 2:
            self.selected_columns.append(index)

        if len(self.selected_columns) == 2:
            self.update_plot()

    def update_plot(self):
        if len(self.selected_columns) < 2:
            return

        x_col, y_col = self.selected_columns
        x = self.data[:, x_col]
        y = self.data[:, y_col]

        sorted_indices = np.argsort(x)
        x = x[sorted_indices]
        y = y[sorted_indices]

        self.graphWidget.clear()
        self.graphWidget.plot(x, y)

    def new_value(self, row, col):
        if col != 0:
            new = self.table.item(row, col).text()
            self.data[row, col] = float(new)

        if col == 2:
            new_inputval = float(self.table.item(row, col).text())
            calculated_val = expit(new_inputval) * 10
            self.data[row, 1] = np.round(calculated_val, 3)
            self.table.item(row, 1).setText(str(np.round(calculated_val, 3)))

        if col == 3:
            self.new_color(row, col)

        if len(self.selected_columns) == 2:
            self.update_plot()

    def selector_changed(self, row, col, value):
        self.data[row, col] = value
        if len(self.selected_columns) == 2:
            self.update_plot()

    def clear_plot(self):
        self.graphWidget.clear()
        self.selected_columns = []

    def save(self):
        filename, _ = QFileDialog.getSaveFileName(self, "сохранить", "", "HDF5 Files (*.h5)")
        if filename:
            self.save_to_hdf5(filename)

    def load(self):
        filename, _ = QFileDialog.getOpenFileName(self, "загрузить", "", "HDF5 Files (*.h5)")
        if filename:
            self.load_from_hdf5(filename)
            self.update_table()
            self.update_plot()

    def save_to_hdf5(self, filename):
        with h5py.File(filename, 'w') as f:
            f.create_dataset('data', data=self.data)

    def load_from_hdf5(self, filename):
        with h5py.File(filename, 'r') as f:
            self.data = f['data'][:]
            self.update_table()
            self.update_plot()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
