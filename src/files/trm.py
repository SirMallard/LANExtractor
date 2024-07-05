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

	version: int
	size1: int
	size2: int
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
		
		reader_pos: int = self._reader.tell()
		self._reader.seek(self._offset, 0)

		self._header = self._reader.read_string(4)
		self.version = self._reader.read_uint32()
		self.size1 = self._reader.read_uint32()
		self.size2 = self._reader.read_uint32()
		self._reader.read_pad(4)
		self.num_files = self._reader.read_uint32()

		self.entries = [None] * self.num_files # type: ignore

		for i in range(self.num_files):
			hash: int = self._reader.read_uint32()
			size: int = self._reader.read_uint32()
			offset: int = self._reader.read_uint32()
			if offset % 2 == 1:
				offset += self.size1
			self.uncompressed_size += size
			entry: Entry = Entry(hash, offset, size)
			self.entries[i] = entry

		self._reader.seek(reader_pos, 0)

	def read_contents(self) -> None:
		if not self._open or self._reader == None:
			return
		
		reader_pos: int = self._reader.tell()

		self.files = [None] * self.num_files # type: ignore

		for i in range(self.num_files):
			entry: Entry = self.entries[i]

			file: BaseFile
			if entry.offset % 2 == 1:
				file = Archive.create_file(self._reader, self._archive, entry.hash, 4, entry.size)
			else:
				self._reader.seek(entry.offset, 0)
				file = Archive.create_file(self._reader, self._archive, entry.hash, entry.offset, entry.size)

			file.open(self._reader)
			file.read_header()
			file.read_contents()
			self.files[i] = file

		# for entry in self.entries:
		# 	if entry.hash == 962647487:
		# 		self._reader.seek(entry.offset + 4, 0)
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

		self._reader.seek(reader_pos, 0)

	def get_sub_files(self) -> list['BaseFile']:
		return self.files

	def dump_data(self) -> dict[str, Any]:
		if not self._content_ready:
			return super().dump_data()
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
			"files": [file.dump_data() for file in self.files],
			"file_data": self.file_data
		}