from pathlib import Path
from archives.archive import Archive
from files.base import BaseFile
from files.sges import SGES
from utils.formats import ArchiveType, Format

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
	
	entries: list[Entry]

	def __init__(self, name: str, path: Path, full_path: Path) -> None:
		super().__init__(name, path, full_path)

	def read_header(self) -> None:
		if not self._open or self._reader == None:
			return

		reader_pos: int = self._reader.tell()

		self._reader.seek(-4, 2)
		table_offset: int = self._reader.read_uint32()
		self._reader.seek(-table_offset, 2)
		
		version: str = self._reader.read_string(4)
		if version != self.version:
			raise Exception(f"\033[91mInvalid \033[91;1mBIG\033[91m File version\033[0m: got \033[91m{version}\033[0m, expected \033[92m{self.version}\033[0m.")
		
		self.num_files = self._reader.read_uint32()

		self.entries = [None] * self.num_files # type: ignore

		for i in range(self.num_files):
			hash: int = self._reader.read_uint32()
			offset: int = self._reader.read_uint32() << 4
			size1: int = self._reader.read_uint32()
			size2: int = self._reader.read_uint32()
			size3: int = self._reader.read_uint32()

			entry: Entry = Entry(hash, offset, size1, size2, size3)
			self.entries[i] = entry

		self._reader.seek(reader_pos, 0)

	def read_file_headers(self) -> None:
		if not self._open or self._reader == None:
			return

		if len(self.entries) == 0:
			pass

		self.files = [None] * self.num_files # type: ignore
		for i in range(len(self.entries)):
			entry: Entry = self.entries[i]
			size: int = entry.size3
			if size == 0:
				size = entry.size1 + entry.size2
			file: BaseFile = Archive.create_file(self._reader, self, entry.hash, entry.offset, size)

			file.open(self._reader)
			file.read_header()
			if file.type == Format.SGES:
				sges: SGES = file # type: ignore
				sges.size1 = entry.size1
				sges.size2 = entry.size2
				sges.size3 = entry.size3

			self.files[i] = file
			self.file_hashes[entry.hash] = file
