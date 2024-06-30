from os.path import dirname
# from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QGroupBox, QMainWindow

ROOT: str = dirname(__file__) + "\\.."

class FileView(QGroupBox):
	def __init__(self) -> None:
		super().__init__()

class Window(QMainWindow):

	def __init__(self) -> None:
		super().__init__()

		self.setWindowTitle("L.A. Noire Explorer")
		self.setWindowIcon(QIcon(f"{ROOT}\\assets\\LANoire.png"))
		self.resize(1280, 720)

	def add_file_list(self):
		pass
