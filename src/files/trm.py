from typing import Any
from utils.formats import Format
from binary_reader import BinaryReader
from files.base import BaseFile

class Container():
	hash: int
	size: int
	unk1: int
	offset: int
	unk2: int

	def __init__(self, hash: int, size: int, unk1: int, offset: int, unk2: int) -> None:
		self.hash = hash
		self.size = size
		self.unk1 = unk1
		self.offset = offset
		self.unk2 = unk2

class TRM(BaseFile):
	type: Format = Format.TRM
	version: int
	unk1: int
	unk2: int
	unk3: int
	unk4: int
	unk5: int
	num_containers: int

	containers: list[Container]
	
	def __init__(self, archive: Any, hash: int, offset: int = 0, size: int = 0) -> None:
		super().__init__(archive, hash, offset, size)

	def read_header(self, reader: BinaryReader) -> None:
		reader_pos: int = reader.tell()
		reader.seek(self._offset, 0)

		self._header = reader.read_string(4)
		self.version = reader.read_uint32()
		self.unk1 = reader.read_uint16()
		self.unk2 = reader.read_uint16()
		self.unk3 = reader.read_uint16()
		self.unk4 = reader.read_uint16()
		self.unk5 = reader.read_uint32()
		self.num_containers = reader.read_uint32()

		self.containers = [None] * self.num_containers # type: ignore

		for i in range(self.num_containers):
			hash: int = reader.read_uint32()
			size: int = reader.read_uint16()
			unk1: int = reader.read_uint16()
			offset: int = reader.read_uint16()
			unk2: int = reader.read_uint16()
			container: Container = Container(hash, size, unk1, offset, unk2)
			self.containers[i] = container

		reader.seek(reader_pos, 0)

	def read_contents(self, reader: BinaryReader) -> None:
		reader_pos: int = reader.tell()

		reader.seek(reader_pos, 0)

	def dump_data(self) -> Any:
		return super().dump_data() | {
			"version": self.version,
			"unk1": self.unk1,
			"unk2": self.unk2,
			"unk3": self.unk3,
			"unk4": self.unk4,
			"unk5": self.unk5,
			"num_containers": self.num_containers,

			"containers": [{
				"hash": container.hash,
				"size": container.size,
				"unk1": container.unk1,
				"offset": container.offset,
				"unk2": container.unk2
			} for container in self.containers]
		}
