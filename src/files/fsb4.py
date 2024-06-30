from typing import Any, Callable, Optional
from utils.formats import Format
from binary_reader import BinaryReader
from files.base import BaseFile

from os.path import join

class Sample():
	_file: Any
	_offset: int
	_size: int

	header_len: int
	name: str

	length: int
	compressed_length: int
	loop_start: int
	loop_end: int

	mode: int
	def_freq: int
	def_vol: int
	def_pan: int
	def_pri: int
	num_channels: int

	min_dist: float
	max_dist: float
	var_freq: int
	var_vol: int
	var_pan: int

	def __init__(self, file: Any, offset: int = 0) -> None:
		self._file = file
		self._offset = offset

	def read_header(self, reader: BinaryReader) -> None:
		reader_pos: int = reader.tell()

		self.header_len = reader.read_uint16()
		self.name = reader.read_string(30).rstrip("\x00")

		self.length = reader.read_uint32()
		self.compressed_length = reader.read_uint32()
		self._size = self.compressed_length
		self.loop_start = reader.read_uint32()
		self.loop_end = reader.read_uint32()

		self.mode = reader.read_uint32()
		self.def_freq = reader.read_int32()
		self.def_vol = reader.read_uint16()
		self.def_pan = reader.read_int16()
		self.def_pri= reader.read_uint16()
		self.num_channels = reader.read_uint16()

		self.min_dist = reader.read_float32()
		self.max_dist = reader.read_float32()
		self.var_freq = reader.read_int32()
		self.var_vol = reader.read_uint16()
		self.var_pan = reader.read_int16()

		reader.seek(reader_pos, 0)

	def output_file(self) -> tuple[int, int, str]:
		return (self._offset, self._size, self.name)

	def dump_data(self) -> Any:
		return {
			"name": self.name,
			"length": self.length,
			"compressed_length": self.compressed_length
		}

class FSB4(BaseFile):
	type: Format = Format.FSB4

	num_samples: int
	shdr_size: int
	data_size: int

	version: int
	flags: int
	hash: int
	guid: Any

	samples: list[Sample]

	def __init__(self, archive: Any, hash: int, offset: int = 0, size: int = 0) -> None:
		super().__init__(archive, hash, offset, size)

	def read_header(self, reader: BinaryReader) -> None:
		reader_pos: int = reader.tell()
		reader.seek(self._offset, 0)

		self._header = reader.read_string(4)
		self.num_samples = reader.read_int32()

		self.shdr_size = reader.read_int32()
		self.data_size = reader.read_int32()

		self.version = reader.read_uint32()
		self.flags = reader.read_uint32()
		self.hash = reader.read_uint64()
		self.guid = reader.read_chunk(16)

		self.samples = [None] * self.num_samples # type: ignore

		reader.seek(reader_pos, 0)

	def read_contents(self, reader: BinaryReader) -> None:
		reader_pos: int = reader.tell()

		reader.seek(self._offset + 48, 0)
		for i in range(self.num_samples):
			sample: Sample = Sample(self, reader.tell())
			sample.read_header(reader)
			self.samples[i] = sample
			# reader.seek(sample.compressed_length, 1)

		reader.seek(reader_pos, 0)

	def output_file(self) -> list[tuple[int, int, str, Optional[Callable[[BinaryReader], bytes]]]]:
		return list(map(lambda file : (file[0], file[1], join(self._name, f"{file[2]}.{Format.formatToExtension(self.type)}"), None), [sample.output_file() for sample in self.samples]))

	def dump_data(self) -> Any:
		return super().dump_data() | {
			"num_samples": self.num_samples,
			"version": self.version,
			"flags": self.flags,
			
			"samples": [sample.dump_data() for sample in self.samples]
		}
