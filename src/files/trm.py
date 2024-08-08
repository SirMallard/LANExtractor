from archives.archive import Archive
from utils.dictionaries import FILE_NAME_HASHES
from utils.formats import Format
from files.base import BaseFile

from typing import Any

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
	contains_sub_files: bool = True

	block_info_size: int
	block_offset: int
	block_size: int
	num_files: int

	entries: list[Entry]
	files: list[BaseFile]
	uncompressed_size: int

	file_data: dict[str, Any]
	
	def __init__(self, archive: Any, hash: int, offset: int = 0, size: int = 0) -> None:
		super().__init__(archive, hash, offset, size)
		self.uncompressed_size = 0
		self.file_data = {}

	def read_header(self) -> None:
		if not self._open or self._reader == None:
			return
		
		reader_pos: int = self._reader.seek(self.offset)

		self.header = self._reader.read_string(4)
		self.block_info_size = self._reader.read_uint32()
		self.block_offset = self._reader.read_uint32()
		self.block_size = self._reader.read_uint32()
		self._reader.read_pad(4)
		self.num_files = self._reader.read_uint32()

		self.entries = [None] * self.num_files # type: ignore

		for i in range(self.num_files):
			hash: int = self._reader.read_uint32()
			size: int = self._reader.read_uint32()
			offset: int = self._reader.read_uint32()
			if offset % 0x10:
				offset = self.block_offset + offset & 0xFFFFFFF0
			self.uncompressed_size += size
			entry: Entry = Entry(hash, offset, size)
			self.entries[i] = entry

		self._reader.seek(reader_pos)

	def read_contents(self) -> None:
		if not self._open or self._reader == None:
			return

		self.files = []
		
		reader_pos: int = self._reader.tell()

		self.files = [None] * self.num_files # type: ignore
		for i in range(self.num_files):
			entry: Entry = self.entries[i]

			if entry.offset > self.size:
				file: BaseFile = BaseFile(self.archive, entry.hash, entry.offset, entry.size)
				file.header = "NULL"
				self.files[i] = file
				continue

			file = Archive.create_file(self._reader, self.archive, entry.hash, entry.offset, entry.size)

			file.parent_file = self
			file.open(self._reader)
			file.read_header()
			file.read_contents()
			self.files[i] = file

		# for entry in self.entries:
		# 	if entry.hash == 962647487:
		# 		self._reader.seek(entry.offset + 4)
		# 		num_textures: int = self._reader.read_uint32()

		# 		texture_data: list[dict[str, int]] = [None] * num_textures # type: ignore

		# 		for i in range(num_textures):
		# 			offset: int = self._reader.read_uint32()
		# 			self._reader.read_pad(4)
		# 			hash: int = self._reader.read_uint32()

		# 			texture_data[i] = {
		# 				"offset": offset,
		# 				"hash": hash,
		# 			}

				
		# 		self.file_data["UniqueTextureMain"] = texture_data

		self._reader.seek(reader_pos)
		self._content_ready = True

	def dump_data(self) -> dict[str, Any]:
		if not self._content_ready:
			return super().dump_data()
		return super().dump_data() | {
			"version": self.block_info_size,
			"block_offset": self.block_offset,
			"block_size": self.block_size,
			"num_files": self.num_files,
			"uncompressed_size": self.uncompressed_size,

			"entries": [{
				"hash": entry.hash,
				"name": entry.name,
				"offset": entry.offset,
				"size": entry.size,
			} for entry in self.entries],
			"files": [file.dump_data() for file in self.files],
			"file_data": self.file_data
		}
