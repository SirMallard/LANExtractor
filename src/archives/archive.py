from pathlib import Path
from binary_reader import BinaryReader
from files.base import BaseArchiveFile, BaseFile
from utils.formats import Format, ArchiveType

from io import BufferedReader
from os.path import getsize
from enum import Enum
from typing import Any
from collections import Counter

class Entry:
	hash: int
	offset: int
	size: int
	name: str

	def __init__(self, hash: int, offset: int, size: int) -> None:
		self.hash = hash
		self.offset = offset
		self.size = size
		self.name = ""

class Archive:
	type: ArchiveType
	
	size: int

	name: str
	path: Path
	full_path: Path
	file_name: str

	_open: bool
	_file: BufferedReader | None
	_reader: BinaryReader | None

	entries: list[Entry]
	num_files: int
	files: list[BaseFile]

	def __init__(self, name: str, path: Path, full_path: Path) -> None:
		self.name = name
		self.path = path
		self.full_path = full_path

		self._open = False
		self._file = None
		self._reader = None

		self.size = getsize(self.full_path)

	def open(self):
		if self._open:
			return

		file: BufferedReader = open(self.full_path, "br") # type: ignore
		self._file = file
		self._reader = BinaryReader(self._file)
		self._open = True

	def close(self):
		if not self._open:
			return

		if self._file != None:
			self._file.close()
		self._file = None
		self._reader = None

		for file in self.files:
			file.close()
			
		self._open = False

	def scan_archive(self):
		self.read_header()
		self.read_file_headers()

		for file in self.files:
			if isinstance(file, BaseArchiveFile):
				file.scan_file()

	def read_header(self) -> None:
		...

	def read_file_headers(self) -> None:
		...
		
	def read_file_contents(self) -> None:
		if not self._open or self._reader == None:
			return

		for file in self.files:
			file.read_contents()

	def open_file(self, file: BaseFile):
		if not self._open or self._reader == None:
			return
		
		file.open(self._reader)

	@staticmethod
	def create_file(reader: BinaryReader, archive: Any, hash: int, offset: int, size: int) -> BaseFile:
		file = BaseFile(archive, hash, offset, size)
		
		file.open(reader)
		file.read_header()
		file.close()

		format: Enum = Format.headerToFormat(file.header)
		newClass = Format.formatToClass(format)
		args = (archive, hash, offset, size)
		newFile: BaseFile = newClass(*args)

		return newFile

	def dump_data(self) -> Any:
		return {
			"name": self.name,
			"path": self.path,
			"full_path": self.full_path,
			"size": self.size,
			"num_files": self.num_files,
			"headers": Counter([file.get_type() for file in self.files]),
			"files": [file.dump_data() for file in self.files]
		}
