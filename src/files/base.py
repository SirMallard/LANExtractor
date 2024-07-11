from pathlib import Path
from utils.dictionaries import FILE_NAME_HASHES
from utils.formats import Format
from binary_reader import BinaryReader

from typing import Any


class BaseFile:
	type: Format = Format.UNKNOWN

	archive: Any
	parent_file: Any | None
	hash: int
	offset: int
	size: int

	name: str
	path: Path
	full_path: Path

	_open: bool
	_reader: BinaryReader | None
	_content_ready: bool
	
	header: str

	def __init__(self, archive: Any, hash: int, offset: int = 0, size: int = 0) -> None:
		self.archive = archive
		self.parent_file = None
		self.hash = hash
		self.offset = offset
		self.size = size

		self._open = False
		self._file = None
		self._reader = None
		self._content_ready = False

		self.path = Path(FILE_NAME_HASHES.get(str(self.hash), f"unknown/{hex(self.hash)}.{Format.formatToExtension(self.type)}"))
		self.name = self.path.name
		self.full_path = self.archive.full_path / self.path

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
		self._reader.seek(self.offset, 0)

		self.header = self._reader.read_string(4)

		self._reader.seek(reader_pos, 0)

	def read_contents(self) -> None:
		...

	def get_type(self) -> str:
		if self.type == Format.SGES:
			return f"{self.type.name}[{self.files[0].get_type()}]" # type: ignore
		elif self.type != Format.UNKNOWN:
			return self.type.name
		return self.header

	def get_full_name(self) -> str:
		if self.parent_file == None:
			return self.name

		return str(Path(self.parent_file.get_full_name(), self.name))

	def output_file(self) -> list[tuple[int, int, str, BinaryReader]]:
		if not self._open or self._reader == None:
			return []
		
		return [(self.offset, self.size, self.get_full_name(), self._reader)]

	def dump_data(self) -> dict[str, Any]:
		return {
			"hash": self.hash,
			"offset": self.offset,
			"size": self.size,
			"header": self.header,
			"name": self.name,
			"type": self.type.name
		}

class BaseArchiveFile(BaseFile):
	files: list[BaseFile]
	file_hashes: dict[int, BaseFile]

	def __init__(self, archive: Any, hash: int, offset: int = 0, size: int = 0) -> None:
		super().__init__(archive, hash, offset, size)

		self.files = []

	def scan_file(self):
		pass

	def getfiles(self) -> list[BaseFile]:
		if not self._content_ready:
			return []
		return self.files

	def get_file_byhash(self, hash: int) -> BaseFile | None:
		if not self._content_ready:
			return None
		return self.file_hashes.get(hash)

	def close(self) -> None:
		if self._content_ready:
			for file in self.files:
				file.close()
		super().close()
