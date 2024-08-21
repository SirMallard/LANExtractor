from struct import unpack
from io import BufferedIOBase, BytesIO
from typing import Any

class BinaryReader():
	file: BufferedIOBase
	endian: str
	size: int

	buffer: BytesIO

	INT8: int = 1
	UINT8: int = 1
	INT16: int = 2
	UINT16: int = 2
	INT32: int = 4
	UINT32: int = 4
	INT64: int = 8
	UINT64: int = 8
	FLOAT: int = 4
	DOUBLE: int = 8

	BYTE: int = 1
	WORD: int = 2
	DWORD: int = 4
	QWORD: int = 8

	BOOLEAN: int = 1
	CHAR: int = 1
	SHORT: int = 2
	INT: int = 4
	LONG: int = 8

	def __init__(self, file: BufferedIOBase) -> None:
		self.file = file
		self.file.seek(0, 2)

		self.size = self.file.tell()
		self.file.seek(0)

		self.endian = "@"
		self.buffer = BytesIO()

	def setendian(self, endian: str) -> None:
		self.endian = endian

	def tell(self) -> int:
		return self.file.tell()

	def seek(self, offset: int, end: int = 0) -> int:
		pos: int = self.tell()
		self.file.seek(offset, end)
		self.buffer.flush()
		return pos

	def read(self, format: str, length: int, offset: int = -1) -> Any:
		data: bytes
		if offset >= 0:
			self.buffer.flush()
			pos: int = self.seek(offset)
			data = self.file.read(length)
			self.seek(pos)
		elif self.buffer.getbuffer().nbytes >= length:
			self.file.seek(length, 1)
			data = self.buffer.read(length)
		else:
			self.buffer.flush()
			data = self.file.read(length)
		return unpack(f"{self.endian}{format}", data)[0]
		

	def read_uint8(self, offset: int = -1) -> int:
		return self.read("B", self.UINT8, offset)
		
	def read_int8(self, offset: int = -1) -> int:
		return self.read("b", self.INT8, offset)
		
	def read_uint16(self, offset: int = -1) -> int:
		return self.read("H", self.UINT16, offset)
		
	def read_int16(self, offset: int = -1) -> int:
		return self.read("h", self.INT16, offset)

	def read_uint32(self, offset: int = -1) -> int:
		return self.read("I", self.UINT32, offset)
		
	def read_int32(self, offset: int = -1) -> int:
		return self.read("i", self.INT32, offset)
		
	def read_uint64(self, offset: int = -1) -> int:
		return self.read("Q", self.UINT64, offset)
		
	def read_int64(self, offset: int = -1) -> int:
		return self.read("q", self.INT64, offset)

	def read_float32(self, offset: int = -1) -> float:
		return self.read("f", self.FLOAT, offset)
		
	def read_float64(self, offset: int = -1) -> float:
		return self.read("d", self.DOUBLE, offset)

	def read_string(self, length: int) -> str:
		s: bytes = self.read(f"{length}s", length)
		try:
			return s.decode("utf-8")
		except:
			return s.hex()

	def read_sized_string(self, size: int) -> str:
		match size:
			case BinaryReader.BYTE:
				return self.read_string(self.read_uint8())
			case BinaryReader.WORD:
				return self.read_string(self.read_uint16())
			case BinaryReader.DWORD:
				return self.read_string(self.read_uint32())
			case BinaryReader.QWORD:
				return self.read_string(self.read_uint64())
			case _:
				return ""

	def read_bytes(self, length: int) -> bytes:
		return self.read(f"{length}s", length)

	def read_pad(self, length: int) -> None:
		self.read_chunk(length)

	def read_chunk(self, length: int) -> bytes:
		return self.file.read(length)

	def read_file(self) -> bytes:
		self.seek(0, 0)
		return self.file.read()

	def buffer_chunk(self, length: int) -> None:
		self.file.readinto(self.buffer.getbuffer())
