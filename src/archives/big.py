from pathlib import Path
from archives.archive import Archive, Entry
from files.base import BaseFile
from files.sges import SGES
from utils.formats import ArchiveType, Format

class BigEntry(Entry):
	size1: int # decompressed block 1 size
	size2: int # decompressed block 2 size
	size3: int # compressed size - for segs

	def __init__(self, hash: int, offset: int, size1: int, size2: int, size3: int):
		super().__init__(hash, offset, -1)
		self.size1 = size1
		self.size2 = size2
		self.size3 = size3

class Big(Archive):
	type = ArchiveType.BIG
	version: str = "\x03\x00\x00\x00"

	entries: list[BigEntry]
	
	def __init__(self, name: str, path: Path, full_path: Path) -> None:
		super().__init__(name, path, full_path)

	def read_header(self) -> None:
		if not self._open or self._reader == None:
			return

		reader_pos: int = self._reader.tell()

		self._reader.seek(-4, 2)
		table_offset: int = self._reader.read_uint32()
		self._reader.seek(-table_offset, 2)
		self._reader.buffer_chunk(table_offset)
		
		assert self._reader.read_uint32() == 3, "Version should be 3."
		
		self.num_files = self._reader.read_uint32()

		self.entries = [None] * self.num_files # type: ignore

		for i in range(self.num_files):
			hash: int = self._reader.read_uint32()
			offset: int = self._reader.read_uint32() << 4
			size1: int = self._reader.read_uint32()
			size2: int = self._reader.read_uint32()
			size3: int = self._reader.read_uint32()

			entry: Entry = BigEntry(hash, offset, size1, size2, size3)
			self.entries[i] = entry

		self._reader.seek(reader_pos)

	def read_file_headers(self) -> None:
		if not self._open or self._reader == None:
			return

		if len(self.entries) == 0:
			pass

		self.files = [None] * self.num_files # type: ignore
		for i in range(len(self.entries)):
			entry: BigEntry = self.entries[i]
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
