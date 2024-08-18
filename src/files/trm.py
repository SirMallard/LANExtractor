from archives.archive import Archive
from files.vram import VRAM
from utils.dictionaries import FILE_NAME_HASHES
from utils.formats import Format
from files.base import BaseFile

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

class TRM(BaseFile):
	type: Format = Format.TRM
	contains_sub_files: bool = True

	size1: int
	size2: int
	num_files: int

	entries: list[Entry]
	files: list[BaseFile]
	content_size: int

	file_data: dict[str, Any]
	
	def __init__(self, archive: Any, hash: int, offset: int = 0, size: int = 0) -> None:
		super().__init__(archive, hash, offset, size)
		self.content_size = 0
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
			self.content_size += size
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

			if entry.offset % 16:
				assert entry.offset % 16 == 1, "Offset should be 1."

			file: BaseFile
			match entry.hash:
				# case 1181384334: #LowLODCollision
				# case 3890050462: #LowLODHierarchy

				# case 2672145205: #LowLodGraphicsMain
				case 1475192112: #LowLodGraphicsVRAM
					file = VRAM(self.archive, entry.hash, entry.offset, entry.size)

				# case 416037040: #MidLodGraphicsMain
				case 3496226485: #MidLodGraphicsVRAM
					file = VRAM(self.archive, entry.hash, entry.offset, entry.size)
				
				# case 710690163: #HighLodGraphicsMain
				case 3807662966: #HighLodGraphicsVRAM
					file = VRAM(self.archive, entry.hash, entry.offset, entry.size)
				
				# case 1188501517: #TextureMain
				case 2390691336: #TextureVRAM
					file = VRAM(self.archive, entry.hash, entry.offset, entry.size)
				
				# case 962647487: #UniqueTextureMain
				case 4056466362: #UniqueTextureVRAM
					file = VRAM(self.archive, entry.hash, entry.offset, entry.size)
				
				# case 4236854250: #GraphicsMain
				case 874599919: #GraphicsVRAM
					file = VRAM(self.archive, entry.hash, entry.offset, entry.size)
				
				# case 388805088: #BreakableGraphicsMain
				case 3750012901: #BreakableGraphicsVRAM
					file = VRAM(self.archive, entry.hash, entry.offset, entry.size)
				
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
					file = Archive.create_file(self._reader, self.archive, entry.hash, entry.offset, entry.size)

			

			file.parent_file = self
			file.open(self._reader)
			file.read_header()
			file.read_contents()
			self.files[i] = file
			self.file_data[entry.name] = file

		# for entry in self.entries:
		# 	if entry.hash == 962647487:
		# 		self._reader.seek(entry.offset + 4)
		# 		num_textures: int = self._reader.read_uint32()

		# 		texture_data: list[dict[str, int]] = [None] * num_textures # type: ignore

		# 		for i in range(num_textures):
		# 			offset: int = self._reader.read_uint32()
		# 			self._reader.read_pad(4)
		# 			hash: int = self._reader.read_uint32()

		# 			texture_data[i] = {
		# 				"offset": offset,
		# 				"hash": hash,
		# 			}

				
		# 		self.file_data["UniqueTextureMain"] = texture_data

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
				"start_offset": entry.offset,
				"size": entry.size,
				"end_offset": entry.offset + entry.size
			} for entry in sorted(self.entries, key = lambda entry: entry.offset)],
			"files": [file.dump_data() for file in self.files],
		}
