from typing import Any
from utils.formats import Format
from files.base import BaseFile

class PTM(BaseFile):
	type: Format = Format.PTM
	version: int
	header_size: int
	num_files: int
	
	def __init__(self, archive: Any, hash: int, offset: int = 0, size: int = 0) -> None:
		super().__init__(archive, hash, offset, size)

	def read_header(self) -> None:
		if not self._open or self._reader == None:
			return
		
		reader_pos: int = self._reader.tell()
		self._reader.seek(self.offset, 0)

		self.header = self._reader.read_string(4)
		self.version = self._reader.read_uint8()
		self.header_size = self._reader.read_uint32()
		self.num_files = self._reader.read_uint32()

		self._reader.seek(reader_pos, 0)

	def read_contents(self) -> None:
		if not self._open or self._reader == None:
			return
		
		reader_pos: int = self._reader.tell()

		self._reader.seek(reader_pos, 0)
		self._content_ready = True

	def dump_data(self) -> dict[str, Any]:
		if not self._content_ready:
			return super().dump_data()
		return super().dump_data() | {
			"version": self.version,
			"header_size": self.header_size,
			"num_files": self.num_files
		}
