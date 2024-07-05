from archives.archive import Archive
from binary_reader import BinaryReader
from files.base import BaseFile
from utils.formats import ArchiveType

class Entry:
	hash: int
	offset: int
	size: int
	name: str

	def __init__(self, hash: int, offset: int, size: int) -> None:
		self.hash = hash
		self.offset = offset
		self.size = size

class Wad(Archive):
	type = ArchiveType.WAD
	
	_entries: list[Entry]

	def __init__(self, root: str, path: str) -> None:
		super().__init__(root, path)

	def read_header(self) -> None:
		if not self._open or self._reader == None:
			return
		reader_pos: int = self._reader.tell()

		_sign = self._reader.read_string(4)
		self._num_files = self._reader.read_uint32()
		
		name_table_offset: int = 0
		self._entries = [None] * self._num_files # type: ignore

		for i in range(self._num_files):
			hash = self._reader.read_uint32()
			offset = self._reader.read_uint32()
			size = self._reader.read_uint32()
			name_table_offset = max(name_table_offset, offset + size)

			entry: Entry = Entry(hash, offset, size)
			self._entries[i] = entry

		self._reader.seek(name_table_offset, 0)
		
		for i in range(self._num_files):
			name: str = self._reader.read_sized_string(BinaryReader.UINT16)
			self._entries[i].name = name

		self._reader.seek(reader_pos, 0)

	def read_file_headers(self) -> None:
		if not self._open or self._reader == None:
			return

		self._files = [None] * self._num_files # type: ignore
		for i in range(self._num_files):
			entry: Entry = self._entries[i]
			file: BaseFile = Archive.create_file(self._reader, self, entry.hash, entry.offset, entry.size)
			file.set_name(entry.name)

			file.open(self._reader)
			file.read_header()
			
			self._files[i] = file
			self._file_hashes[entry.hash] = file
