from typing import Any
from utils.formats import Format
from binary_reader import BinaryReader
from files.base import BaseFile

def align(x: int, a: int) -> int:
	return (x + (a - 1)) & ~(a - 1)

class SGES(BaseFile):
	type: Format = Format.SGES
	version: int
	num_chunks: int
	u0: int
	u1: int
	u2: int
	u3: int
	data_offset: int
	uobjects: list[int]
	
	def __init__(self, archive: Any, hash: int, offset: int = 0, size: int = 0) -> None:
		super().__init__(archive, hash, offset, size)

	def read_header(self, reader: BinaryReader) -> None:
		reader_pos: int = reader.tell()
		reader.seek(self._offset, 0)

		self._header = reader.read_string(4)
		self.version = reader.read_uint16()
		self.num_chunks = reader.read_uint16()
		self.u0 = reader.read_uint8()
		self.u1 = reader.read_uint8()
		self.u2 = reader.read_uint8()
		self.u3 = reader.read_uint8()

		self.data_offset = align(self._offset + 12 + (4 * self.u0) + (2 * reader.UINT16 * self.num_chunks), 16)

		self.uobjects = [reader.read_uint32() for _ in range(self.u0)]

		reader.seek(reader_pos, 0)

	def read_contents(self, reader: BinaryReader) -> None:
		reader_pos: int = reader.tell()

		reader.seek(reader_pos, 0)

	def dump_data(self) -> Any:
		return super().dump_data() | {
			"version": self.version,
			"num_chunks": self.num_chunks,
			"u0": self.u0,
			"u1": self.u1,
			"u2": self.u2,
			"u3": self.u3,
			"data_offset": self.data_offset,
			"uobjects": self.uobjects
		}
