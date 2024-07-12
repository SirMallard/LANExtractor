from files.base import BaseFile


class BaseFileWindow:
	file: BaseFile

	def __init__(self, file: BaseFile) -> None:
		self.file = file
