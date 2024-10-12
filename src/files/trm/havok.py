from typing import Any
from utils.formats import Format
from files.base import BaseFile

class HAVOK(BaseFile):
	type: Format = Format.VRAM

	user_tag: int
	version: int
	pointer_size: int
	little_endian: bool
	reuse_base_class_padding: bool
	empty_base_class_optimisation: bool
	num_chunks: int
	content_section_index: int
	content_section_offset: int
	content_class_name_section_index: int
	content_class_name_section_offset: int
	content_version: str
	flags: int
	max_predicate: int
	predicate_array_size_plus_padding: int
        
	
	def __init__(self, archive: Any, hash: int, offset: int = 0, size: int = 0) -> None:
		super().__init__(archive, hash, offset, size)

	def read_header(self) -> None:
		if not self._open or self._reader == None:
			return	
		
		reader_pos: int = self._reader.seek(self.offset)
		self.header = "W\xe0\xe0W"

		self.user_tag = self._reader.read_uint32()
		self.version = self._reader.read_uint32()
		assert self.version == 5, "Version should be 5."

		self.pointer_size = self._reader.read_uint8()
		self.little_endian = self._reader.read_uint8() > 0
		self.reuse_base_class_padding = self._reader.read_uint8() > 0
		self.empty_base_class_optimisation = self._reader.read_uint32() > 0
		
		self.num_chunks = self._reader.read_int32()
		self.content_section_index = self._reader.read_int32()
		self.content_section_offset = self._reader.read_int32()
		self.content_class_name_section_index = self._reader.read_int32()
		self.content_class_name_section_offset = self._reader.read_int32()

		self.content_version = self._reader.read_string(16)
		self.flags = self._reader.read_uint16()
		self.max_predicate = self._reader.read_int16()
		self.predicate_array_size_plus_padding = self._reader.read_int16()

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
			"user_tag": self.user_tag,
			"version": self.version,
			"num_chunks": self.num_chunks,
			"content_version": self.content_version,
			"flags": self.flags
		}
