from binary_reader import BinaryReader
from archives.archive import Archive
from files.base import BaseFile
from utils.formats import ArchiveType

class Entry:
		hash: int
		offset: int
		size1: int # decompressed block 1 size
		size2: int # decompressed block 2 size
		size3: int # compressed size - for segs

		def __init__(self, hash: int, offset: int, size1: int, size2: int, size3: int):
			self.hash = hash
			self.offset = offset
			self.size1 = size1
			self.size2 = size2
			self.size3 = size3

class Big(Archive):
	type = ArchiveType.BIG
	version: str = "\x03\x00\x00\x00"
	
	_entries: list[Entry]

	def __init__(self, root: str, path: str) -> None:
		super().__init__(root, path)

	def read_header(self, reader: BinaryReader) -> None:
		reader_pos: int = reader.tell()

		reader.seek(-4, 2)
		table_offset: int = reader.read_uint32()
		reader.seek(-table_offset, 2)
		
		version: str = reader.read_string(4)
		if version != self.version:
			raise Exception(f"\033[91mInvalid \033[91;1mBIG\033[91m File version\033[0m: got \033[91m{version}\033[0m, expected \033[92m{self.version}\033[0m.")
		
		self._num_files = reader.read_uint32()

		self._entries = [None] * self._num_files # type: ignore

		for i in range(self._num_files):
			hash: int = reader.read_uint32()
			offset: int = reader.read_uint32() << 4
			size1: int = reader.read_uint32()
			size2: int = reader.read_uint32()
			size3: int = reader.read_uint32()

			entry: Entry = Entry(hash, offset, size1, size2, size3)
			self._entries[i] = entry

		reader.seek(reader_pos, 0)

	def read_files(self, reader: BinaryReader) -> None:
		if len(self._entries) == 0:
			pass

		self._files = [None] * self._num_files # type: ignore
		for i in range(len(self._entries)):
			entry: Entry = self._entries[i]
			size: int = entry.size3
			if size == 0:
				size = entry.size1 + entry.size2
			file: BaseFile = self.create_file(reader, self, entry.hash, entry.offset, size)
			file.read_header(reader)
			self._files[i] = file
