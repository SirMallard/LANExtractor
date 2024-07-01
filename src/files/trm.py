from typing import Any
from archives.archive import Archive
from utils.dictionaries import FILE_NAME_HASHES
from utils.formats import Format
from binary_reader import BinaryReader
from files.base import BaseFile

class Entry():
	hash: int
	name: str
	offset: int
	size: int

	def __init__(self, hash: int, offset: int, size: int) -> None:
		self.hash = hash
		self.name = FILE_NAME_HASHES.get(str(self.hash), "UNKNOWN")
		self.offset = offset
		self.size = size

class TRM(BaseFile):
	type: Format = Format.TRM
	version: int
	size1: int
	size2: int
	num_files: int

	entries: list[Entry]
	files: list[BaseFile]
	uncompressed_size: int = 0
	
	def __init__(self, archive: Any, hash: int, offset: int = 0, size: int = 0) -> None:
		super().__init__(archive, hash, offset, size)

	def read_header(self, reader: BinaryReader) -> None:
		reader_pos: int = reader.tell()
		reader.seek(self._offset, 0)

		self._header = reader.read_string(4)
		self.version = reader.read_uint32()
		self.size1 = reader.read_uint32()
		self.size2 = reader.read_uint32()
		reader.read_pad(4)
		self.num_files = reader.read_uint32()

		self.entries = [None] * self.num_files # type: ignore

		for i in range(self.num_files):
			hash: int = reader.read_uint32()
			size: int = reader.read_uint32()
			offset: int = reader.read_uint32()
			if offset % 2 == 1:
				offset += self.size1
			self.uncompressed_size += size
			entry: Entry = Entry(hash, offset, size)
			self.entries[i] = entry

		reader.seek(reader_pos, 0)

	def read_contents(self, reader: BinaryReader) -> None:
		reader_pos: int = reader.tell()

		self.files = [None] * self.num_files # type: ignore

		for i in range(self.num_files):
			entry: Entry = self.entries[i]
			if entry.offset % 2 == 1:
				entry.offset = 4
			reader.seek(entry.offset, 0)

			file: BaseFile = Archive.create_file(reader, self._archive, entry.hash, entry.offset, entry.size)
			file.read_header(reader)
			file.read_contents(reader)
			self.files[i] = file

		reader.seek(reader_pos, 0)

	def dump_data(self) -> Any:
		return super().dump_data() | {
			"version": self.version,
			"size1": self.size1,
			"size2": self.size2,
			"num_files": self.num_files,
			"uncompressed_size": self.uncompressed_size,
			"sizes": self.size1 + self.size2,

			"entries": [{
				"hash": entry.hash,
				"name": entry.name,
				"offset": entry.offset,
				"size": entry.size,
			} for entry in self.entries],
			"files": [file.dump_data() for file in self.files]
		}
