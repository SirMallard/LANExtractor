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

	contents: BufferedIOBase
	_content_reader: BinaryReader
	
	def __init__(self, archive: Any, hash: int, offset: int = 0, size: int = 0) -> None:
		super().__init__(archive, hash, offset, size)

		self.size1 = 0
		self.size2 = 0
		self.size3 = 0

	def read_header(self) -> None:
		if not self._open or self._reader == None:
			return
		
		reader_pos: int = self._reader.seek(self.offset)

		self.header = self._reader.read_string(4)
		assert self._reader.read_uint16() == 7, "Version should be 7, not."
		self.num_chunks = self._reader.read_uint16()
		self.num_objects = self._reader.read_uint32()

		self.data_offset = align(self.offset + 12 + (4 * self.num_objects) + (4 * self.num_chunks), 16)

		self._reader.seek(reader_pos)

	def read_contents(self) -> None:
		if not self._open or self._reader == None:
			return
		
		reader_pos: int = self._reader.seek(self.offset + 12)
		
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

		self.contents = BytesIO()

		for i in range(self.num_chunks):
			chunk = self.chunks[i]
			self._reader.seek(chunk.offset)
			
			if chunk.flags & 0x10:
				self.contents.write(decompress(self._reader.read_chunk(chunk.size), -15))
				self.compressed_size += chunk.size
			else:
				self.contents.write(self._reader.read_chunk(self.size1))
				self.compressed_size += self.size1

		# there is too much extra space, so we look for another sges file
		calculated_size: int = align(12 + (4 * self.num_objects) + (4 * self.num_chunks), 16) + self.compressed_size
		if self.size - calculated_size > 64:
			offset: int = align(self.chunks[-1].offset + self.chunks[-1].size, 16)
			remaining: int = align(self.offset + self.size, 16) - offset
			self._reader.seek(offset)

			other: int = -1
			for _ in range(remaining // 16):
				if self._reader.read_bytes(4) == b"sges":
					other = self._reader.tell() - 4
					break

				self._reader.seek(12, 1)

			assert other > 0, "Should have found another `sges` file."
			extra_file = SGES(self.archive, 0, other, self.size - (other - self.offset))
			extra_file.parent_file = self
			extra_file.open(self._reader)
			extra_file.read_header()
			extra_file.read_contents()

			self.num_objects += extra_file.num_objects
			self.objects.extend(extra_file.objects)
			self.num_chunks += extra_file.num_chunks
			self.chunks.extend(extra_file.chunks)
			self.contents.write(extra_file.contents.read())
			self.compressed_size += extra_file.compressed_size
			
			extra_file.close()
		
		self.uncompressed_size = self.contents.getbuffer().nbytes
		self.contents.seek(0)

		self._content_reader = BinaryReader(self.contents)
		file: BaseFile = Archive.create_file(self._content_reader, self, self.hash, 0, self.uncompressed_size)
		file.parent_file = self
		file.open(self._content_reader)
		file.read_header()
		file.read_contents()

		self.files = [file]

		self._reader.seek(reader_pos)
		self._content_ready = True

	def close(self) -> None:
		if self._content_ready:
			self.contents.close()
		super().close()

	def get_attributes(self) -> list[str]:
		return super().get_attributes() + ["Compressed"]

	def dump_data(self) -> dict[str, Any]:
		if not self._content_ready:
			return super().dump_data()
		return super().dump_data() | {
			"size1": self.size1,
			"size2": self.size2,
			"size3": self.size3,
			"num_objects": self.num_objects,
			"objects": [f"{object:08x}" for object in self.objects],
			"compressed": self.compressed_size,
			"num_chunks": self.num_chunks,
			"chunks": [{
				"offset": chunk.offset,
				"size": chunk.size,
				"flags": hex(chunk.flags),
			} for chunk in self.chunks],
			"file": self.files[0].dump_data(),
		}
