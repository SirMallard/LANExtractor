from typing import Any
from zlib import decompress
from utils.formats import Format
from binary_reader import BinaryReader
from files.base import BaseFile

def align(x: int, a: int) -> int:
	return (x + (a - 1)) & ~(a - 1)

class Chunk():
	offset: int
	size: int
	size_coeff: int
	flags: int
	data: bytes

	def __init__(self, offset: int, size: int, size_coeff: int, flags: int) -> None:
		self.offset = offset
		self.size = size
		self.size_coeff = size_coeff
		self.size += 0x10000 * self.size_coeff
		self.flags = flags


class SGES(BaseFile):
	type: Format = Format.SGES
	size1: int
	size2: int
	size3: int
	version: int
	num_chunks: int
	u0: int
	u1: int
	u2: int
	u3: int
	data_offset: int
	uobjects: list[int]
	chunks: list[Chunk]
	
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

		reader.seek(reader_pos, 0)

	def read_contents(self, reader: BinaryReader) -> None:
		reader_pos: int = reader.tell()

		reader.seek(self._offset + 4 + (2 * reader.UINT16) + (4 * reader.UINT8), 0)
		
		self.uobjects = [reader.read_uint32() for _ in range(self.u0)]
		
		self.chunks = [None] * self.num_chunks # type: ignore
		for i in range(self.num_chunks):
			size: int = reader.read_uint16()
			flags: int = reader.read_uint8()
			size_coeff: int = reader.read_uint8()

			chunk: Chunk = Chunk(self.data_offset, size, size_coeff, flags)
			self.data_offset += chunk.size
			self.chunks[i] = chunk

		for i in range(self.num_chunks):
			chunk = self.chunks[i]
			reader.seek(chunk.offset, 0)
			
			if chunk.flags & 0x10:
				chunk.data = b"NOT_READING" or decompress(reader.read_chunk(chunk.size), -15)
			else:
				chunk.data = b"NOT_READING" or reader.read_chunk(self.size1)

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
			"uobjects": self.uobjects,
			"size1": self.size1,
			"size2": self.size2,
			"size3": self.size3,
			"chunks": [{
				"offset": chunk.offset,
				"size": chunk.size,
				"flags": hex(chunk.flags),
				"size_coeff": chunk.size_coeff,
				"data_len": len(chunk.data)
			} for chunk in self.chunks]
		}
