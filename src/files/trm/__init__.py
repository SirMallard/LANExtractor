from archives.archive import Archive
from files.trm.main_texture import UniqueTexture
from files.trm.vram import VRAM
from utils.dictionaries import FILE_NAME_HASHES
from utils.formats import Format
from files.base import BaseArchiveFile, BaseFile

from typing import Any

class Entry():
	hash: int
	name: str
	offset: int
	size: int

	def __init__(self, hash: int, offset: int, size: int) -> None:
		self.hash = hash
		self.name = FILE_NAME_HASHES.get(str(self.hash), "UNKNOWN")
		self.offset = offset
		self.size = size

class TRM(BaseArchiveFile):
	type: Format = Format.TRM
	contains_sub_files: bool = True

	size1: int
	size2: int
	num_files: int

	entries: list[Entry]

	file_data: dict[str, BaseFile]
	
	def __init__(self, archive: Any, hash: int, offset: int = 0, size: int = 0) -> None:
		super().__init__(archive, hash, offset, size)
		self.file_data = {}

	def read_header(self) -> None:
		if not self._open or self._reader == None:
			return
		
		reader_pos: int = self._reader.seek(self.offset)

		self.header = self._reader.read_string(4)
		assert self._reader.read_uint32() == 1, "Version should be 1."
		self.size1 = self._reader.read_uint32()
		self.size2 = self._reader.read_uint32()
		assert self._reader.read_uint32() == 0, "Padding should be 0."
		self.num_files = self._reader.read_uint32()

		self.entries = [None] * self.num_files # type: ignore
		for i in range(self.num_files):
			hash: int = self._reader.read_uint32()
			size: int = self._reader.read_uint32()
			offset: int = self._reader.read_uint32()
			if offset % 0x10:
				offset = self.size1 + offset & 0xFFFFFFF0
			offset += self.offset
			entry: Entry = Entry(hash, offset, size)
			self.entries[i] = entry

		self._reader.seek(reader_pos)

	def read_contents(self) -> None:
		if not self._open or self._reader == None:
			return
		
		reader_pos: int = self._reader.tell()

		self.files = [None] * self.num_files # type: ignore
		for i in range(self.num_files):
			entry: Entry = self.entries[i]

			file: BaseFile | None = None
			match entry.hash:
				# case 1181384334: #LowLODCollision
				# case 3890050462: #LowLODHierarchy

				# case 2672145205: #LowLodGraphicsMain
				# case 416037040: #MidLodGraphicsMain				
				# case 710690163: #HighLodGraphicsMain				

				# case 1188501517: #TextureMain				
				# case 962647487: #UniqueTextureMain				
				# case 4236854250: #GraphicsMain				
				# case 388805088: #BreakableGraphicsMain
				
				# case 1540170686: #Collision
				# case 2306622947: #BreakableCollision
				
				# case 4202309806: #Hierarchy
				# case 684412659: #BreakableHierarchy
				
				# case 3228098164: #Skeletons
				# case 2755868908: #BaseSkeletons
				
				# case 2370995420: #animation
				# case 3087893650: #AnimationSet
				# case 704566783: #SDKAnimSet
				
				# case 586247102: #cloth
				# case 2381493261: #UNKNOWN
				case _:
					if entry.name.endswith("VRAM"):
						file = VRAM(self.archive, entry.hash, entry.offset, entry.size)

			if file == None:
				continue

			file.parent_file = self
			file.open(self._reader)
			file.read_header()
			self.files[i] = file
			self.file_data[file.name] = file

		for i in range(self.num_files):
			if self.files[i] == None: # type: ignore
				entry = self.entries[i]

				file = None
				match entry.hash:
					case 962647487: #UniqueTextureMain
						file = UniqueTexture(self.archive, entry.hash, self.file_data.get("UniqueTextureVRAM"), entry.offset, entry.size) # type: ignore
					case _:
						file = Archive.create_file(self._reader, self.archive, entry.hash, entry.offset, entry.size)

				if file == None: # type: ignore
					continue

				file.parent_file = self
				file.open(self._reader)
				file.read_header()
				file.read_contents()
				self.files[i] = file
				self.file_data[file.name] = file


		self._reader.seek(reader_pos)
		self._content_ready = True

	def dump_data(self) -> dict[str, Any]:
		if not self._content_ready:
			return super().dump_data()
		return super().dump_data() | {
			"size1": self.size1,
			"size2": self.size2,
			"num_files": self.num_files,

			"entries": [{
				"hash": entry.hash,
				"name": entry.name,
				"offset": entry.offset,
				"size": entry.size,
			} for entry in sorted(self.entries, key = lambda entry: entry.offset)],
			"files": [file.dump_data() for file in self.files],
		}
