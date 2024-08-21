from pathlib import Path
from typing import Any

from files.trm.vram import VRAM
from files.dds import DDS
from utils.formats import Format
from files.base import BaseArchiveFile

class UniqueTexture(BaseArchiveFile):
	type: Format = Format.TRM

	vram: VRAM
	num_files: int
	
	def __init__(self, archive: Any, hash: int, vram: VRAM, offset: int = 0, size: int = 0) -> None:
		super().__init__(archive, hash, offset, size)
		self.vram = vram
		self.vram.parent_file = self

	def read_header(self) -> None:
		if not self._open or self._reader == None:
			return
		
		reader_pos: int = self._reader.seek(self.offset)

		self.header = "UTM#"
		assert self._reader.read_string(4), "Header should be 0."
		self.num_files = self._reader.read_uint32()

		self._reader.seek(reader_pos)

	def read_contents(self) -> None:
		if not self._open or self._reader == None:
			return
		
		if not self.vram._open or self.vram._reader == None:
			return
		
		reader_pos: int = self._reader.seek(self.offset + 8)

		self.files = [None] * self.num_files # type: ignore
		for i in range(self.num_files):
			offset: int = self._reader.read_uint32() + self.vram.offset
			assert self._reader.read_uint32() == 0, "Padding should be 0."
			hash: int = self._reader.read_uint32()

			dds: DDS = DDS(self.archive, hash, offset, 0)
			self.files[i] = dds
			if i > 0:
				self.files[i - 1].size = offset - self.files[i - 1].offset
		self.files[-1].size = self.vram.size - self.files[-1].offset + self.vram.offset

		for i in range(self.num_files):
			dds = self.files[i] # type: ignore
			dds.parent_file = self
			dds.open(self.vram._reader)
			dds.read_header()
			dds.read_contents()

		self._reader.seek(reader_pos)
		self._content_ready = True

	def export_contents(self, directory: Path, name: str | None = None) -> None:
		return super().export_contents(directory, self.name.rstrip("Main"))

	def dump_data(self) -> dict[str, Any]:
		if not self._content_ready:
			return super().dump_data()
		return super().dump_data() | {
			"num_files": self.num_files,
			"vram": self.vram.dump_data(),
			"files": [file.dump_data() for file in self.files]
		}
