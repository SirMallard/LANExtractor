from binary_reader import BinaryReader
from files.base import BaseFile
from utils.formats import Format, ArchiveType

from io import IOBase
from os.path import getsize, splitext, join
from enum import Enum
from typing import Any
from collections import Counter

class Archive:
	type: ArchiveType

	name: str
	file_name: str
	file_path: str
	out_path: str
	out_json_path: str

	_open: bool
	_file: IOBase | None
	_reader: BinaryReader | None

	_size: int
	_num_files: int
	_files: list[BaseFile]
	_file_hashes: dict[int, BaseFile]

	def __init__(self, file_path: str, file_name: str) -> None:
		self.file_name = file_name
		self.file_path = file_path

		self._open = False
		self._file = None
		self._reader = None
		
		(name, _) = splitext(splitext(file_name)[0])
		self.name = name
		from __main__ import OUT_DIRECTORY
		self.out_path = join(OUT_DIRECTORY, *name.replace("_", ".").split("."))
		self.out_json_path = join(self.out_path, f"{self.file_name}.json")
		self.out_path = join(self.out_path, "files")

		self._size = getsize(self.file_path)
		self._file_hashes = {}

	def open(self):
		if self._open:
			return

		self._file = open(self.file_path, "rb")
		self._reader = BinaryReader(self._file)
		self._open = True

	def close(self):
		if not self._open:
			return

		if self._file != None:
			self._file.close()
		self._file = None
		self._reader = None

		for file in self._files:
			file.close()
			
		self._open = False

	def read_header(self) -> None:
		...

	def read_file_headers(self) -> None:
		...
		
	def read_file_contents(self) -> None:
		if not self._open or self._reader == None:
			return

		for file in self._files:
			file.read_contents()
	
	def get_files(self) -> list[BaseFile]:
		return self._files
	
	def get_file_by_hash(self, hash: int) -> BaseFile | None:
		return self._file_hashes.get(hash)

	@staticmethod
	def create_file(reader: BinaryReader, archive: Any, hash: int, offset: int, size: int) -> BaseFile:
		file = BaseFile(archive, hash, offset, size)
		
		file.open(reader)
		file.read_header()
		header: str = file.get_header()
		file.close()

		format: Enum = Format.headerToFormat(header)
		newClass = Format.formatToClass(format)
		args = (archive, hash, offset, size)
		newFile: BaseFile = newClass(*args)

		return newFile

	def dump_data(self) -> Any:
		return {
			"name": self.name,
			"file_name": self.file_name,
			"file_path": self.file_path,
			"out_path": self.out_path,
			"out_json_path": self.out_json_path,
			"size": self._size,
			"num_files": self._num_files,
			"headers": Counter([file.get_type() for file in self._files]),
			"files": [file.dump_data() for file in self._files]
		}
