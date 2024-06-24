from binary_reader import BinaryReader
from archives.archive import Archive
from files.base import BaseFile
from utils.formats import ArchiveType

class Wad(Archive):
	type = ArchiveType.WAD

	def __init__(self, root: str, path: str) -> None:
		super().__init__(root, path)

	def read_header(self, reader: BinaryReader) -> None:
		reader_pos: int = reader.tell()

		_sign = reader.read_string(4)
		self._num_files = reader.read_uint32()
		
		name_table_offset: int = 0
		self._files = [None] * self._num_files # type: ignore

		for i in range(self._num_files):
			name_crc = reader.read_uint32()
			offset = reader.read_uint32()
			size = reader.read_uint32()
			name_table_offset = max(name_table_offset, offset + size)

			file: BaseFile = self.create_file(reader, self, name_crc, offset, size)
			self._files[i] = file

		reader.seek(name_table_offset, 0)
		
		for i in range(self._num_files):
			name_len: int = reader.read_uint16()
			name: str = reader.read_string(name_len)
			self._files[i].set_name(name)

		reader.seek(reader_pos, 0)

	def read_files(self, reader: BinaryReader) -> None:
		for i in range(self._num_files):
			file: BaseFile = self._files[i]
			file.read_header(reader)
