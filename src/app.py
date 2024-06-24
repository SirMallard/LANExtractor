from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QIcon

app: QApplication = QApplication([])

icon: QIcon = QIcon("./assets/LANoire.ico")

window: QMainWindow = QMainWindow()
window.setWindowTitle("L.A. Noire Explorer")
window.setWindowIcon(icon)
window.show()

print(app.exec())
