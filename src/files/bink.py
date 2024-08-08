from typing import Any
from enum import IntFlag
from utils.formats import Format
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

	def read_header(self) -> None:
		if not self._open or self._reader == None:
			return
		
		reader_pos: int = self._reader.seek(self.offset)

		self.header = self._reader.read_string(4)
		self.data_size = self._reader.read_uint32()
		self.num_frames = self._reader.read_uint32()
		self.largest_frame = self._reader.read_uint32()
		self._reader.read_pad(4)

		self.width = self._reader.read_uint32()
		self.height = self._reader.read_uint32()
		self.frame_dividend = self._reader.read_uint32()
		self.frame_divider = self._reader.read_uint32()

		self.flags = HeaderFlags(self._reader.read_uint32())
		self.num_audio_tracks = self._reader.read_uint32()

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
			"num_frames": self.num_frames,
			"largest_frame": self.largest_frame,
			"width": self.width,
			"height": self.height,
			"frame_dividend": self.frame_dividend,
			"frame_divider": self.frame_divider,
			"flags": bin(self.flags),
			"num_audio_tracks": self.num_audio_tracks,
		}
