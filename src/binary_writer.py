from struct import pack
from io import IOBase
from typing import Any

class BinaryWriter():
	_file: IOBase
	_endian: str

	def __init__(self, file: IOBase) -> None:
		self._file = file
		self._endian = "@"

	def set_endian(self, endian: str) -> None:
		self._endian = endian

	def tell(self) -> int:
		return self._file.tell()

	def write(self, format: str, data: Any) -> int | None:
		self._file.write(pack(f"{self._endian}{format}", ))

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
		return self._file.write(data)
