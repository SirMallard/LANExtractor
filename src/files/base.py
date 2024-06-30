from utils.dictionaries import FILE_NAME_HASHES
from utils.formats import Format
from binary_reader import BinaryReader

from typing import Any, Callable, Optional

class BaseFile:
	type: Format = Format.UNKNOWN
	_archive: Any
	_hash: int
	_offset: int
	_size: int
	_name: str = ""
	
	_header: str

	def __init__(self, archive: Any, hash: int, offset: int = 0, size: int = 0) -> None:
		self._archive = archive
		self._hash = hash
		self._offset = offset
		self._size = size

		self._name = FILE_NAME_HASHES.get(str(self._hash), "unknown")

	def read_header(self, reader: BinaryReader) -> None:
		reader_pos: int = reader.tell()
		reader.seek(self._offset, 0)

		self._header = reader.read_string(4)

		reader.seek(reader_pos, 0)

	def read_contents(self, reader: BinaryReader) -> None:
		pass

	def set_name(self, name: str) -> None:
		self._name = name

	def get_header(self) -> str:
		return self._header

	def get_type(self) -> str:
		if self.type == Format.SGES:
			return f"{self.type.name}[{self.file.get_type()}]" # type: ignore
		elif self.type != Format.UNKNOWN:
			return self.type.name
		return self._header
	
	def output_file(self) -> list[tuple[int, int, str, Optional[Callable[[BinaryReader], bytes]]]]:
		return [(self._offset, self._size, self._name if len(self._name) > 0 else f"{self._hash}.{Format.formatToExtension(self.type)}", None)]
	
	def dump_data(self) -> Any:
		return {
			"hash": self._hash,
			"offset": self._offset,
			"size": self._size,
			"header": self._header,
			"name": self._name,
			"type": self.type.name
		}
