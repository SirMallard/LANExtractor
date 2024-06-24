from typing import Any
from enum import IntFlag
from utils.formats import Format
from binary_reader import BinaryReader
from files.base import BaseFile

class HeaderFlags(IntFlag):
	ALPHA_PLANE = 0x14
	GRAYSCALE = 0x11

class BINK(BaseFile):
	type: Format = Format.BINK

	data_size: int
	num_frames: int
	largest_frame: int
	width: int
	height: int
	frame_dividend: int
	frame_divider: int
	flags: HeaderFlags
	num_audio_tracks: int
	
	def __init__(self, archive: Any, hash: int, offset: int = 0, size: int = 0) -> None:
		super().__init__(archive, hash, offset, size)

	def read_header(self, reader: BinaryReader) -> None:
		reader_pos: int = reader.tell()
		reader.seek(self._offset, 0)

		self._header = reader.read_string(4)
		self.data_size = reader.read_uint32()
		self.num_frames = reader.read_uint32()
		self.largest_frame = reader.read_uint32()
		reader.read_pad(4)

		self.width = reader.read_uint32()
		self.height = reader.read_uint32()
		self.frame_dividend = reader.read_uint32()
		self.frame_divider = reader.read_uint32()

		self.flags = HeaderFlags(reader.read_uint32())
		self.num_audio_tracks = reader.read_uint32()

		reader.seek(reader_pos, 0)

	def read_contents(self, reader: BinaryReader) -> None:
		reader_pos: int = reader.tell()

		reader.seek(reader_pos, 0)

	def dump_data(self) -> Any:
		return super().dump_data() | {
			"num_frames": self.num_frames,
			"largest_frame": self.largest_frame,
			"width": self.width,
			"height": self.height,
			"frame_dividend": self.frame_dividend,
			"frame_divider": self.frame_divider,
			"flags": bin(self.flags),
			"num_audio_tracks": self.num_audio_tracks,
		}
