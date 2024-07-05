from io import BytesIO, IOBase
from typing import Any
from zlib import decompress
from archives.archive import Archive
from utils.formats import Format
from binary_reader import BinaryReader
from files.base import BaseArchiveFile, BaseFile

def align(x: int, a: int) -> int:
	return (x + (a - 1)) & ~(a - 1)

class Chunk():
	offset: int
	size: int
	size_coeff: int
	flags: int

	def __init__(self, offset: int, size: int, size_coeff: int, flags: int) -> None:
		self.offset = offset
		self.size = size
		self.size_coeff = size_coeff
		self.size += 0x10000 * self.size_coeff
		self.flags = flags


class SGES(BaseArchiveFile):
	type: Format = Format.SGES
	contains_sub_files: bool = True

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
	compressed_size: int = 0
	uncompressed_size: int = 0

	_file_file: IOBase
	_file_reader: BinaryReader
	
	def __init__(self, archive: Any, hash: int, offset: int = 0, size: int = 0) -> None:
		super().__init__(archive, hash, offset, size)

	def read_header(self) -> None:
		if not self._open or self._reader == None:
			return
		
		reader_pos: int = self._reader.tell()
		self._reader.seek(self._offset, 0)

		self._header = self._reader.read_string(4)
		self.version = self._reader.read_uint16()
		self.num_chunks = self._reader.read_uint16()
		self.u0 = self._reader.read_uint8()
		self.u1 = self._reader.read_uint8()
		self.u2 = self._reader.read_uint8()
		self.u3 = self._reader.read_uint8()

		self.data_offset = align(self._offset + 12 + (4 * self.u0) + (2 * self._reader.UINT16 * self.num_chunks), 16)

		self._reader.seek(reader_pos, 0)

	def read_contents(self) -> None:
		if not self._open or self._reader == None:
			return
		
		reader_pos: int = self._reader.tell()

		self._reader.seek(self._offset + 4 + (2 * self._reader.UINT16) + (4 * self._reader.UINT8), 0)
		
		self.uobjects = [self._reader.read_uint32() for _ in range(self.u0)]
		
		self.chunks = [None] * self.num_chunks # type: ignore
		for i in range(self.num_chunks):
			size: int = self._reader.read_uint16()
			flags: int = self._reader.read_uint8()
			size_coeff: int = self._reader.read_uint8()

			chunk: Chunk = Chunk(self.data_offset, size, size_coeff, flags)
			self.data_offset += chunk.size
			self.chunks[i] = chunk

		self._file_file = BytesIO()

		for i in range(self.num_chunks):
			chunk = self.chunks[i]
			self._reader.seek(chunk.offset, 0)
			
			if chunk.flags & 0x10:
				self._file_file.write(decompress(self._reader.read_chunk(chunk.size), -15))
				self.compressed_size += chunk.size
			else:
				self._file_file.write(self._reader.read_chunk(self.size1))

		self.uncompressed_size = self._file_file.__sizeof__()

		self._file_reader = BinaryReader(self._file_file)
		file: BaseFile = Archive.create_file(self._file_reader, self, self._hash, 0, self.uncompressed_size)
		file.set_parent_file(self)
		file.open(self._file_reader)
		file.read_header()
		file.read_contents()

		self._files = [file]
		self._file_hashes = {
			self._hash: file
		}

		self._reader.seek(reader_pos, 0)

	def output_file(self) -> list[tuple[int, int, str, BinaryReader]]:
		return self._files[0].output_file()

	def close(self) -> None:
		self._file_file.close()
		super().close()

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
				"compressed": bool(chunk.flags & 0x10),
				"size_coeff": chunk.size_coeff,
			} for chunk in self.chunks],
			"file": self._files[0].dump_data()
		}
