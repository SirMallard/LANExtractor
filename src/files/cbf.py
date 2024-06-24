from typing import Any
from utils.formats import Format
from binary_reader import BinaryReader
from files.base import BaseFile

class CBF(BaseFile):
	type: Format = Format.OGG

	num_containers: int
	containers: list[dict[str, Any]]
	
	def __init__(self, archive: Any, hash: int, offset: int = 0, size: int = 0) -> None:
		super().__init__(archive, hash, offset, size)

	def read_header(self, reader: BinaryReader) -> None:
		reader_pos: int = reader.tell()
		reader.seek(self._offset, 0)

		self._header = reader.read_string(4)
		self.num_containers = reader.read_uint16()
		self.containers = [None] * self.num_containers # type: ignore

		reader.seek(reader_pos, 0)

	def read_contents(self, reader: BinaryReader) -> None:
		reader_pos: int = reader.tell()

		reader.seek(self._offset + 4 + reader.UINT32, 0)
		for i in range(self.num_containers):
			name_len: int = reader.read_uint16()
			name: str = reader.read_string(name_len)
			num_strings: int = reader.read_uint32()

			container: dict[str, Any] = {
				"name_len": name_len,
				"name": name,
				"num_strings": num_strings,
				"strings": []
			}

			for _ in range(num_strings):
				str_len: int = reader.read_uint16()
				container["strings"].append(reader.read_string(str_len))

			self.containers[i] = container

		reader.seek(reader_pos, 0)

	def dump_data(self) -> Any:
		return super().dump_data() | {
			"num_containers": self.num_containers,
			"containers": self.containers
		}
