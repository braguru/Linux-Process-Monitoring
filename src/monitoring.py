import sys
import psutil
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget, QPushButton, QHBoxLayout, QMessageBox, QInputDialog
)
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon


class ProcessMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Linux Process Monitor")
        self.setGeometry(300, 300, 800, 400)

        # Set window icon
        self.setWindowIcon(QIcon(r"C:\Users\PrinceOforiAnkamah\Downloads\projects\DevOps Python\Process Monitoring\icons8-linux-50.png"))

        # Create main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Layout for buttons
        self.layout = QVBoxLayout()

        # Create Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["PID", "Process Name", "CPU Usage (%)", "Memory Usage (%)"])
        self.layout.addWidget(self.table)

        # Set row height and column width
        self.table.horizontalHeader().setDefaultSectionSize(150)  # Adjust column width
        # self.layout.addWidget(self.table)

        # Add control buttons
        button_layout = QHBoxLayout()

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.update_process_table)
        button_layout.addWidget(self.refresh_button)

        self.kill_button = QPushButton("Kill Process")
        self.kill_button.clicked.connect(self.kill_process)
        button_layout.addWidget(self.kill_button)

        self.start_button = QPushButton("Start Process")
        self.start_button.clicked.connect(self.start_process)
        button_layout.addWidget(self.start_button)

        self.restart_button = QPushButton("Restart Process")
        self.restart_button.clicked.connect(self.restart_process)
        button_layout.addWidget(self.restart_button)

        self.layout.addLayout(button_layout)
        main_widget.setLayout(self.layout)

        # Timer to refresh process list
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_process_table)
        self.timer.start(10000)  # refresh every 5 seconds

        # Initial load
        self.update_process_table()

    def update_process_table(self):
        """Retrieve and display process information."""
        self.table.setRowCount(0)  # Clear existing rows
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)
                self.table.setItem(row_position, 0, QTableWidgetItem(str(proc.pid)))
                self.table.setItem(row_position, 1, QTableWidgetItem(proc.name()))
                self.table.setItem(row_position, 2, QTableWidgetItem(f"{proc.cpu_percent():.2f}"))
                self.table.setItem(row_position, 3, QTableWidgetItem(f"{proc.memory_percent():.2f}"))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    def kill_process(self):
        """Kill the selected process."""
        selected = self.table.currentRow()
        if selected >= 0:
            pid = int(self.table.item(selected, 0).text())
            try:
                p = psutil.Process(pid)
                p.terminate()
                QMessageBox.information(self, "Success", f"Process {pid} terminated.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to terminate process {pid}: {e}")
            self.update_process_table()

    def start_process(self):
        """Start a new process."""
        process_name, ok = QInputDialog.getText(self, "Start Process", "Enter process name to start:")
        if ok and process_name:
            try:
                subprocess.Popen(process_name, shell=True)
                QMessageBox.information(self, "Success", f"Process '{process_name}' started.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to start process '{process_name}': {e}")
            self.update_process_table()

    def restart_process(self):
        """Restart the selected process."""
        selected = self.table.currentRow()
        if selected >= 0:
            pid = int(self.table.item(selected, 0).text())
            try:
                p = psutil.Process(pid)
                process_name = p.name()
                p.terminate()
                p.wait()  # Wait for termination
                subprocess.Popen(process_name, shell=True)
                QMessageBox.information(self, "Success", f"Process {pid} restarted.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to restart process {pid}: {e}")
            self.update_process_table()


# Run the application
app = QApplication(sys.argv)
window = ProcessMonitor()
window.show()
sys.exit(app.exec())
