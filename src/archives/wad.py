from pathlib import Path
from archives.archive import Archive, Entry
from binary_reader import BinaryReader
from files.base import BaseFile
from utils.formats import ArchiveType

class Wad(Archive):
	type = ArchiveType.WAD
	
	entries: list[Entry]

	def __init__(self, name: str, path: Path, full_path: Path) -> None:
		super().__init__(name, path, full_path)

	def read_header(self) -> None:
		if not self._open or self._reader == None:
			return
		reader_pos: int = self._reader.tell()

		self._reader.read_string(4)
		self.num_files = self._reader.read_uint32()
		self._reader.buffer_chunk(self.num_files * BinaryReader.UINT32 * 3)
		
		name_table_offset: int = 0
		self.entries = [None] * self.num_files # type: ignore

		for i in range(self.num_files):
			hash = self._reader.read_uint32()
			offset = self._reader.read_uint32()
			size = self._reader.read_uint32()
			name_table_offset = max(name_table_offset, offset + size)

			entry: Entry = Entry(hash, offset, size)
			self.entries[i] = entry

		self._reader.seek(name_table_offset, 0)
		self._reader.buffer_chunk(self.num_files * 56)
		
		for i in range(self.num_files):
			name: str = self._reader.read_sized_string(BinaryReader.UINT16)
			self.entries[i].name = name

		self._reader.seek(reader_pos, 0)

	def read_file_headers(self) -> None:
		if not self._open or self._reader == None:
			return

		self.files = [None] * self.num_files # type: ignore
		for i in range(self.num_files):
			entry: Entry = self.entries[i]
			file: BaseFile = Archive.create_file(self._reader, self, entry.hash, entry.offset, entry.size)
			file.path = Path(entry.name)
			file.full_path = self.full_path / file.path
			file.name = file.path.name

			file.open(self._reader)
			file.read_header()
			
			self.files[i] = file
