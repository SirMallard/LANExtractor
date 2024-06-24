from typing import Any
from utils.formats import Format
from binary_reader import BinaryReader
from files.base import BaseFile

class OGG(BaseFile):
	type: Format = Format.OGG
	version: int
	header_type: int
	
	def __init__(self, archive: Any, hash: int, offset: int = 0, size: int = 0) -> None:
		super().__init__(archive, hash, offset, size)

	def read_header(self, reader: BinaryReader) -> None:
		reader_pos: int = reader.tell()
		reader.seek(self._offset, 0)

		self._header = reader.read_string(4)
		self.version = reader.read_uint8()
		self.header_type = reader.read_uint8()

		reader.seek(reader_pos, 0)

	def read_contents(self, reader: BinaryReader) -> None:
		reader_pos: int = reader.tell()

		reader.seek(reader_pos, 0)

	def dump_data(self) -> Any:
		return super().dump_data() | {
			"version": self.version,
			"header_type": self.header_type
		}
