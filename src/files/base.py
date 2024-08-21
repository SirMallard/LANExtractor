from json import dump
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

		self.path = Path(FILE_NAME_HASHES.get(str(self.hash), f"unknown/{hex(self.hash)}{Format.formatToExtension(self.type)}"))
		self.name = self.path.name
		self.full_path = self.archive.full_path / self.path

	def open(self, reader: BinaryReader) -> None:
		if self._open:
			return

		self._reader = reader
		self._open = True

	def close(self) -> None:
		if not self._open:
			return

		self._reader = None
		self._open = False

	def read_header(self) -> None:
		if not self._open or self._reader == None:
			return
		
		reader_pos: int = self._reader.seek(self.offset)

		self.header = self._reader.read_string(4)

		self._reader.seek(reader_pos)

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
		
		return [(self.offset, self.size, str(self.path), self._reader)]

	def export_raw_file(self, directory: Path) -> None:
		if not self._open or self._reader == None:
			return

		reader_pos: int = self._reader.seek(self.offset)

		path: Path = directory / self.name
		path.parent.mkdir(parents = True, exist_ok = True)
		path.write_bytes(self._reader.read_chunk(self.size))

		self._reader.seek(reader_pos)

	def export_file(self, directory: Path) -> None:
		if not self._open or self._reader == None:
			return

		reader_pos: int = self._reader.seek(self.offset)

		path: Path = (directory / self.name).with_suffix(Format.formatToExtension(self.type))
		path.parent.mkdir(parents = True, exist_ok = True)
		path.write_bytes(self._reader.read_chunk(self.size))

		self._reader.seek(reader_pos)

	def export_contents(self, directory: Path) -> None:
		return self.export_file(directory)

	def get_attributes(self) -> list[str]:
		return []

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

	def __init__(self, archive: Any, hash: int, offset: int = 0, size: int = 0) -> None:
		super().__init__(archive, hash, offset, size)

		self.files = []

	def scan_file(self) -> None:
		pass

	def get_files(self) -> list[BaseFile]:
		if not self._content_ready:
			return []
		return self.files

	def export_file(self, directory: Path) -> None:
		for file in self.files:
			file.export_raw_file((directory / self.name).with_suffix(""))

	def export_contents(self, directory: Path, name: str | None = None) -> None:
		if not self._open or self._reader == None:
			return

		reader_pos: int = self._reader.seek(self.offset)
		
		path: Path = (directory / (name or self.name)).with_suffix("") / f"{name or self.name}.{Format.formatToExtension(self.type)}.json" 
		path.parent.mkdir(parents = True, exist_ok = True)
		with open(path, "w") as file:
			dump(self.dump_data(), file, indent="\t")

		for file in self.files:
			file.export_contents((directory / (name or self.name)).with_suffix(""))
		
		self._reader.seek(reader_pos)

	def close(self) -> None:
		if self._content_ready:
			for file in self.files:
				file.close()
		super().close()

class BaseAudioFile(BaseFile):
	type: Format = Format.WAV

	length: float
	sample_length: int
	frequency: int

	def __init__(self, archive: Any, hash: int, offset: int = 0, size: int = 0) -> None:
		super().__init__(archive, hash, offset, size)
