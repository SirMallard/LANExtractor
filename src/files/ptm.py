from typing import Any
from utils.formats import Format
from binary_reader import BinaryReader
from files.base import BaseFile

class PTM(BaseFile):
	type: Format = Format.PTM
	version: int
	header_size: int
	num_files: int
	
	def __init__(self, archive: Any, hash: int, offset: int = 0, size: int = 0) -> None:
		super().__init__(archive, hash, offset, size)

	def read_header(self, reader: BinaryReader) -> None:
		reader_pos: int = reader.tell()
		reader.seek(self._offset, 0)

		self._header = reader.read_string(4)
		self.version = reader.read_uint8()
		self.header_size = reader.read_uint32()
		self.num_files = reader.read_uint32()

		reader.seek(reader_pos, 0)

	def read_contents(self, reader: BinaryReader) -> None:
		reader_pos: int = reader.tell()

		reader.seek(reader_pos, 0)

	def dump_data(self) -> Any:
		return super().dump_data() | {
			"version": self.version,
			"header_size": self.header_size,
			"num_files": self.num_files
		}
