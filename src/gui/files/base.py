from typing import Callable
from files.base import BaseFile

class BaseFileWindow:
	file: BaseFile
	terminate: Callable[[], None]

	def __init__(self, file: BaseFile, terminate: Callable[[], None]) -> None:
		self.file = file
		self.terminate = terminate

	def render(self) -> None:
		pass
