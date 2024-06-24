from typing import Any
from utils.formats import Format
from binary_reader import BinaryReader
from files.base import BaseFile

class ATB(BaseFile):
	type: Format = Format.ATB

	num_containers: int
	
	def __init__(self, archive: Any, name_crc: int, offset: int = 0, size: int = 0) -> None:
		super().__init__(archive, name_crc, offset, size)

	def read_header(self, reader: BinaryReader) -> None:
		reader_pos: int = reader.tell()
		reader.seek(self._offset, 0)

		self._header = reader.read_string(4)
		self.num_containers = reader.read_uint16()

		reader.seek(reader_pos, 0)

	def read_contents(self, reader: BinaryReader) -> None:
		reader_pos: int = reader.tell()

		reader.seek(self._offset + 4 + reader.UINT16, 0)

		reader.seek(reader_pos, 0)

	def read_object(self, reader: BinaryReader) -> Any:
		hash: int = reader.read_uint32()
		name: str = reader.read_sized_string(BinaryReader.BYTE)

		return

	def dump_data(self) -> Any:
		return super().dump_data() | {
			"num_containers": self.num_containers
		}
