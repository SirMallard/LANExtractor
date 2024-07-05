from pathlib import Path
from utils.dictionaries import FILE_NAME_HASHES
from utils.formats import Format
from binary_reader import BinaryReader

from typing import Any


class BaseFile:
	type: Format = Format.UNKNOWN

	_archive: Any
	_parent_file: Any | None
	_hash: int
	_offset: int
	_size: int
	_name: str = ""
	_file_name: str = ""

	_open: bool
	_reader: BinaryReader | None
	_content_ready: bool
	
	_header: str

	def __init__(self, archive: Any, hash: int, offset: int = 0, size: int = 0) -> None:
		self._archive = archive
		self._parent_file = None
		self._hash = hash
		self._offset = offset
		self._size = size

		self._open = False
		self._file = None
		self._reader = None
		self._content_ready = False

		self._file_name = FILE_NAME_HASHES.get(str(self._hash), "")
		if self._file_name != "":
			self._name = self._file_name
		else:
			self._name = f"{hex(self._hash)}.{Format.formatToExtension(self.type)}"

	def open(self, reader: BinaryReader):
		if self._open:
			return

		self._reader = reader
		self._open = True

	def close(self):
		if not self._open:
			return

		self._reader = None
		self._open = False

	def read_header(self) -> None:
		if not self._open or self._reader == None:
			return
		
		reader_pos: int = self._reader.tell()
		self._reader.seek(self._offset, 0)

		self._header = self._reader.read_string(4)

		self._reader.seek(reader_pos, 0)

	def read_contents(self) -> None:
		...


	def set_name(self, name: str) -> None:
		self._name = name

	def set_parent_file(self, parent_file: Any):
		self._parent_file = parent_file


	def get_header(self) -> str:
		return self._header

	def get_type(self) -> str:
		if self.type == Format.SGES:
			return f"{self.type.name}[{self._files[0].get_type()}]" # type: ignore
		elif self.type != Format.UNKNOWN:
			return self.type.name
		return self._header
	
	def get_hash(self) -> int:
		return self._hash

	def get_name(self) -> str:
		return self._name

	def get_full_name(self) -> str:
		if self._parent_file == None:
			return self.get_name()

		return str(Path(self._parent_file.get_full_name(), self.get_name()))

	def get_size(self) -> int:
		return self._size

	def get_archive(self) -> Any:
		return self._archive


	def output_file(self) -> list[tuple[int, int, str, BinaryReader]]:
		if not self._open or self._reader == None:
			return []
		
		return [(self._offset, self._size, self.get_full_name(), self._reader)]

	def dump_data(self) -> dict[str, Any]:
		return {
			"hash": self._hash,
			"offset": self._offset,
			"size": self._size,
			"header": self._header,
			"name": self._name,
			"type": self.type.name
		}

class BaseArchiveFile(BaseFile):
	_files: list[BaseFile]
	_file_hashes: dict[int, BaseFile]

	def __init__(self, archive: Any, hash: int, offset: int = 0, size: int = 0) -> None:
		super().__init__(archive, hash, offset, size)

		self._files = []

	def get_files(self) -> list[BaseFile]:
		if not self._content_ready:
			return []
		return self._files

	def get_file_by_hash(self, hash: int) -> BaseFile | None:
		if not self._content_ready:
			return None
		return self._file_hashes.get(hash)

	def close(self) -> None:
		if self._content_ready:
			for file in self._files:
				file.close()
		super().close()
