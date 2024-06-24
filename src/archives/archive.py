from enum import Enum
from typing import Any
from binary_reader import BinaryReader
from files.base import BaseFile
from utils.formats import Format, ArchiveType

from os.path import getsize, splitext, join

class Archive:
	type: ArchiveType

	name: str
	file_name: str
	file_path: str
	out_path: str
	out_json_path: str

	_size: int
	_num_files: int
	_files: list[BaseFile]

	def __init__(self, file_path: str, file_name: str) -> None:
		self.file_name = file_name
		self.file_path = file_path

		(name, _) = splitext(splitext(file_name)[0])
		self.name = name
		from __main__ import OUT_DIRECTORY
		self.out_path = join(OUT_DIRECTORY, *name.replace("_", ".").split("."))
		self.out_json_path = join(self.out_path, f"{self.file_name}.json")
		self.out_path = join(self.out_path, "files")

		self._size = getsize(self.file_path)

	def read_header(self, reader: BinaryReader) -> None:
		pass

	def read_files(self, reader: BinaryReader) -> None:
		pass

	def read_contents(self, reader: BinaryReader) -> None:
		for file in self._files:
			file.read_contents(reader)

	def dump_data(self) -> Any:
		return {
			"name": self.name,
			"file_name": self.file_name,
			"file_path": self.file_path,
			"out_path": self.out_path,
			"out_json_path": self.out_json_path,
			"size": self._size,
			"num_files": self._num_files,
			"headers": list({file.get_header() for file in self._files}),
			"files": [file.dump_data() for file in self._files]
		}
	
	def get_files(self) -> list[BaseFile]:
		return self._files
	
	def create_file(self, reader: BinaryReader, archive: Any, hash: int, offset: int, size: int) -> BaseFile:
		file = BaseFile(archive, hash, offset, size)
		
		file.read_header(reader)
		header: str = file.get_header()

		format: Enum = Format.headerToFormat(header)
		newClass = Format.formatToClass(format)
		args = (archive, hash, offset, size)
		newFile: BaseFile = newClass(*args)

		return newFile
