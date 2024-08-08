from typing import Any
from utils.formats import Format
from files.base import BaseFile

class CBF(BaseFile):
	type: Format = Format.CBF1

	num_containers: int
	containers: list[dict[str, Any]]
	
	def __init__(self, archive: Any, hash: int, offset: int = 0, size: int = 0) -> None:
		super().__init__(archive, hash, offset, size)

	def read_header(self) -> None:
		if not self._open or self._reader == None:
			return
		
		reader_pos: int = self._reader.seek(self.offset)

		self.header = self._reader.read_string(4)
		self.num_containers = self._reader.read_uint16()
		self.containers = [None] * self.num_containers # type: ignore

		self._reader.seek(reader_pos)

	def read_contents(self) -> None:
		if not self._open or self._reader == None:
			return
		
		reader_pos: int = self._reader.seek(self.offset + 4 + self._reader.UINT32)

		for i in range(self.num_containers):
			name_len: int = self._reader.read_uint16()
			name: str = self._reader.read_string(name_len)
			num_strings: int = self._reader.read_uint32()

			container: dict[str, Any] = {
				"name_len": name_len,
				"name": name,
				"num_strings": num_strings,
				"strings": []
			}

			for _ in range(num_strings):
				str_len: int = self._reader.read_uint16()
				container["strings"].append(self._reader.read_string(str_len))

			self.containers[i] = container

		self._reader.seek(reader_pos)
		self._content_ready = True

	def dump_data(self) -> dict[str, Any]:
		if not self._content_ready:
			return super().dump_data()
		return super().dump_data() | {
			"num_containers": self.num_containers,
			"containers": self.containers
		}
