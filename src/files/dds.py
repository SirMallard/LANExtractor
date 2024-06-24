from typing import Any
from enum import IntFlag
from utils.formats import Format
from binary_reader import BinaryReader
from files.base import BaseFile

class HeaderFlags(IntFlag):
	CAPS = 0x1
	HEIGHT = 0x2
	WIDTH = 0x3
	PITCH = 0x8
	PIXELFORMAT = 0x1000
	MIPMAPCOUNT = 0x20000
	LINEARSIZE = 0x80000
	DEPTH = 0x800000

class PixelFormatFlags(IntFlag):
	ALPHAPIXELS = 0x1
	ALPHA = 0x2
	FOURCC = 0x4
	RGB = 0x40
	YUV = 0x200
	LUMINANCE = 0x20000

class PixelFormat():
	structure_size: int
	flags: PixelFormatFlags
	code: int
	rgb_bit_count: int
	red_bit_mask: int
	green_bit_mask: int
	blue_bit_mask: int
	alpha_bit_mask: int

class SurfaceComplexity(IntFlag):
	COMPLEX = 0x8
	MIPMAP = 0x400000
	TEXTURE = 0x1000

class SurfaceComplexity2(IntFlag):
	CUBEMAP = 0x200
	CUBEMAP_POSITIVEX = 0x400
	CUBEMAP_NEGATIVEX = 0x800
	CUBEMAP_POSITIVEY = 0x1000
	CUBEMAP_NEGATIVEY = 0x2000
	CUBEMAP_POSITIVEZ = 0x4000
	CUBEMAP_NEGATIVEZ = 0x8000
	VOLUME = 0x200000

class DDS(BaseFile):
	type: Format = Format.DDS

	structure_size: int
	flags: HeaderFlags
	height: int
	width: int
	pitch_size: int
	depth: int
	mip_map_count: int
	pixel_format: PixelFormat = PixelFormat()
	surface_complexity = SurfaceComplexity,
	surface_complexity2 = SurfaceComplexity2,

	def __init__(self, archive: Any, hash: int, offset: int = 0, size: int = 0) -> None:
		super().__init__(archive, hash, offset, size)

	def read_header(self, reader: BinaryReader) -> None:
		reader_pos: int = reader.tell()
		reader.seek(self._offset, 0)

		self._header = reader.read_string(4)
		self.structure_size = reader.read_uint32()
		self.flags = HeaderFlags(reader.read_uint32())
		self.height = reader.read_uint32()
		self.width = reader.read_uint32()
		self.pitch_size = reader.read_uint32()
		self.depth = reader.read_uint32()
		self.mip_map_count = reader.read_uint32()

		reader.read_chunk(44)

		self.pixel_format.structure_size = reader.read_uint32()
		self.pixel_format.flags = PixelFormatFlags(reader.read_uint32())
		self.pixel_format.code = reader.read_uint32()
		self.pixel_format.rgb_bit_count = reader.read_uint32()
		self.pixel_format.red_bit_mask = reader.read_uint32()
		self.pixel_format.green_bit_mask = reader.read_uint32()
		self.pixel_format.blue_bit_mask = reader.read_uint32()
		self.pixel_format.alpha_bit_mask = reader.read_uint32()

		self.surface_complexity = SurfaceComplexity(reader.read_uint32())
		self.surface_complexity2 = SurfaceComplexity2(reader.read_uint32())

		reader.read_chunk(12)

		reader.seek(reader_pos, 0)

	def read_contents(self, reader: BinaryReader) -> None:
		reader_pos: int = reader.tell()

		reader.seek(reader_pos, 0)

	def dump_data(self) -> Any:
		return super().dump_data() | {
			"flags": bin(self.flags),
			"height": self.height,
			"width": self.width,
			"pitch_size": self.pitch_size,
			"depth": self.depth,
			"mip_map_count": self.mip_map_count,
		}
