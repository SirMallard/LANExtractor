from struct import pack
from io import IOBase
from typing import Any

class BinaryWriter():
	file: IOBase
	endian: str

	def __init__(self, file: IOBase) -> None:
		self.file = file
		self.endian = "@"

	def setendian(self, endian: str) -> None:
		self.endian = endian

	def tell(self) -> int:
		return self.file.tell()

	def write(self, format: str, data: Any) -> int | None:
		self.file.write(pack(f"{self.endian}{format}", ))

	def write_uint8(self, data: int) -> int | None:
		return self.write("B", data)
		
	def write_int8(self, data: int) -> int | None:
		return self.write("b", data)
		
	def write_uint16(self, data: int) -> int | None:
		return self.write("H", data)
		
	def write_int16(self, data: int) -> int | None:
		return self.write("h", data)

	def write_uint32(self, data: int) -> int | None:
		return self.write("I", data)
		
	def write_int32(self, data: int) -> int | None:
		return self.write("i", data)
		
	def write_uint64(self, data: int) -> int | None:
		return self.write("Q", data)
		
	def write_int64(self, data: int) -> int | None:
		return self.write("q", data)

	def write_float32(self, data: float) -> int | None:
		return self.write("f", data)
		
	def write_float64(self, data: float) -> int | None:
		return self.write("d", data)

	def write_string(self, data: str) -> int | None:
		self.write(f"{len(data)}s", data.encode())

	def write_chunk(self, data: Any) -> int | None:
		return self.file.write(data)
