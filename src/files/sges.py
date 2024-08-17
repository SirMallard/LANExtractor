from io import BufferedIOBase, BytesIO
from typing import Any
from zlib import decompress

from archives.archive import Archive
from utils.formats import Format
from binary_reader import BinaryReader
from files.base import BaseArchiveFile, BaseFile

# Rounds up to the nearest block, usually 16
def align(offset: int, block: int) -> int:
	return (offset + (block - 1)) & ~(block - 1)

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
	num_chunks: int
	num_objects: int
	data_offset: int
	chunks: list[Chunk]
	objects: list[int]
	compressed_size: int = 0
	uncompressed_size: int = 0

	_file_file: BufferedIOBase
	_file_reader: BinaryReader
	
	def __init__(self, archive: Any, hash: int, offset: int = 0, size: int = 0) -> None:
		super().__init__(archive, hash, offset, size)

	def read_header(self) -> None:
		if not self._open or self._reader == None:
			return
		
		reader_pos: int = self._reader.seek(self.offset)

		self.header = self._reader.read_string(4)
		assert self._reader.read_uint16() == 7, "Version should be 7, not."
		self.num_chunks = self._reader.read_uint16()
		self.num_objects = self._reader.read_uint32()

		self.data_offset = align(self.offset + 12 + (4 * self.num_chunks), 16)

		self._reader.seek(reader_pos)

	def read_contents(self) -> None:
		if not self._open or self._reader == None:
			return
		
		reader_pos: int = self._reader.seek(self.offset + 4 + (2 * self._reader.UINT16) + (4 * self._reader.UINT8))
		
		self.objects = [self._reader.read_uint32() for _ in range(self.num_objects)]
		
		self.chunks = [None] * self.num_chunks # type: ignore
		for i in range(self.num_chunks):
			size: int = self._reader.read_uint16()
			flags: int = self._reader.read_uint8()
			assert flags == 0x00 or flags == 0x10 or flags == 0x11, f"Flags should be 0x00, 0x10 or 0x11, not {flags}."
			size_coeff: int = self._reader.read_uint8()

			chunk: Chunk = Chunk(self.data_offset, size, size_coeff, flags)
			self.data_offset += chunk.size
			self.chunks[i] = chunk

		self._file_file = BytesIO()

		for i in range(self.num_chunks):
			chunk = self.chunks[i]
			self._reader.seek(chunk.offset)
			
			if chunk.flags & 0x10:
				self._file_file.write(decompress(self._reader.read_chunk(chunk.size), -15))
				self.compressed_size += chunk.size
			else:
				self._file_file.write(self._reader.read_chunk(self.size1))

		self.uncompressed_size = self._file_file.__sizeof__()

		self._file_reader = BinaryReader(self._file_file)
		file: BaseFile = Archive.create_file(self._file_reader, self, self.hash, 0, self.uncompressed_size)
		file.parent_file = self
		file.open(self._file_reader)
		file.read_header()
		file.read_contents()

		self.files = [file]

		self._reader.seek(reader_pos)
		self._content_ready = True

	def close(self) -> None:
		if self._content_ready:
			self._file_file.close()
		super().close()

	def get_attributes(self) -> list[str]:
		return super().get_attributes() + ["Compressed"]

	def dump_data(self) -> dict[str, Any]:
		if not self._content_ready:
			return super().dump_data()
		return super().dump_data() | {
			# "data_offset": self.data_offset,
			"size1": self.size1,
			"size2": self.size2,
			"size3": self.size3,
			"compressed": self.compressed_size,
			"num_chunks": self.num_chunks,
			"chunks": [{
				"offset": chunk.offset,
				"size": chunk.size,
				"flags": hex(chunk.flags),
				# "compressed": bool(chunk.flags & 0x10),
				# "size_coeff": chunk.size_coeff,
			} for chunk in self.chunks],
			"file": self.files[0].dump_data()
		}
