from typing import Any
from utils.formats import Format
from files.base import BaseFile

class PTM(BaseFile):
	type: Format = Format.PTM

	data_offset: int

	pointer_addresses: list[int]
	pointers: list[int]
	pointer_data_types: list[int]
	
	def __init__(self, archive: Any, hash: int, offset: int = 0, size: int = 0) -> None:
		super().__init__(archive, hash, offset, size)

	def read_header(self) -> None:
		if not self._open or self._reader == None:
			return
		
		reader_pos: int = self._reader.seek(self.offset)

		self.header = self._reader.read_string(4)
		assert self._reader.read_uint32() == 7, "Version should be 7."
		self.data_offset = self._reader.read_uint32()

		self.pointer_addresses = []
		self.pointers = []
		self.pointer_data_types = []

		pointer_address: int = 0
		data_type: int = 0

		while True:
			num_pointers: int = self._reader.read_uint16()

			for _ in range(num_pointers):
				value: int = self._reader.read_uint16()
				if value & 0x8000:
					self._reader.seek(-2, 1)
					data: int = self._reader.read_uint32()
					data_shift: int = (data & 0x80000000) | (data & 0x80000000 >> 16)
					pointer_address = data_shift ^ data
				else:
					pointer_address += 4 * value
				
				address: int = pointer_address + self.data_offset
				self.pointer_addresses.append(address)
				self.pointers.append(self._reader.read_uint32(self.offset + address) + self.data_offset)
				self.pointer_data_types.append(data_type)

			block_end: int = self._reader.tell() + self._reader.tell() & 2

			if block_end + 6 >= self.data_offset:
				break

			self._reader.read_pad(self._reader.tell() & 2)
			data_type = self._reader.read_uint32()			
			break		

		self._reader.seek(reader_pos)

	def read_contents(self) -> None:
		if not self._open or self._reader == None:
			return
		
		reader_pos: int = self._reader.tell()

		self._reader.seek(reader_pos)
		self._content_ready = True

	def dump_data(self) -> dict[str, Any]:
		if not self._content_ready:
			return super().dump_data()
		return super().dump_data() | {
			"data_offset": self.data_offset,
			"pointer_addresses": self.pointer_addresses,
			"pointers": self.pointers
		}
