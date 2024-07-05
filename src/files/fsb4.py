from utils.formats import Format
from files.base import BaseArchiveFile, BaseFile

from typing import Any

class Sample(BaseFile):
	header_len: int
	_name: str

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
		super().__init__(file.get_archive(), 0, offset, 0)
		self._offset = offset
		self._parent_file = file

	def read_header(self) -> None:
		if not self._open or self._reader == None:
			return
		
		reader_pos: int = self._reader.tell()

		self.header_len = self._reader.read_uint16()
		self._name = self._reader.read_string(30).rstrip("\x00")

		self.length = self._reader.read_uint32()
		self.compressed_length = self._reader.read_uint32()
		self._size = self.compressed_length
		self.loop_start = self._reader.read_uint32()
		self.loop_end = self._reader.read_uint32()

		self.mode = self._reader.read_uint32()
		self.def_freq = self._reader.read_int32()
		self.def_vol = self._reader.read_uint16()
		self.def_pan = self._reader.read_int16()
		self.def_pri= self._reader.read_uint16()
		self.num_channels = self._reader.read_uint16()

		self.min_dist = self._reader.read_float32()
		self.max_dist = self._reader.read_float32()
		self.var_freq = self._reader.read_int32()
		self.var_vol = self._reader.read_uint16()
		self.var_pan = self._reader.read_int16()

		self._reader.seek(reader_pos, 0)

	def dump_data(self) -> Any:
		return {
			"name": self._name,
			"length": self.length,
			"compressed_length": self.compressed_length
		}

class FSB4(BaseArchiveFile):
	type: Format = Format.FSB4
	contains_sub_files: bool = True

	num_samples: int
	shdr_size: int
	data_size: int

	version: int
	flags: int
	hash: int
	guid: Any

	def __init__(self, archive: Any, hash: int, offset: int = 0, size: int = 0) -> None:
		super().__init__(archive, hash, offset, size)

	def read_header(self) -> None:
		if not self._open or self._reader == None:
			return
		
		reader_pos: int = self._reader.tell()
		self._reader.seek(self._offset, 0)

		self._header = self._reader.read_string(4)
		self.num_samples = self._reader.read_int32()

		self.shdr_size = self._reader.read_int32()
		self.data_size = self._reader.read_int32()

		self.version = self._reader.read_uint32()
		self.flags = self._reader.read_uint32()
		self.hash = self._reader.read_uint64()
		self.guid = self._reader.read_chunk(16)

		self._reader.seek(reader_pos, 0)

	def read_contents(self) -> None:
		if not self._open or self._reader == None:
			return
		
		reader_pos: int = self._reader.tell()

		self._reader.seek(self._offset + 48, 0)

		self._files = [None] * self.num_samples # type: ignore
		self._file_hashes = {}
		for i in range(self.num_samples):
			sample: Sample = Sample(self, self._reader.tell())
			sample.open(self._reader)
			sample.read_header()
			self._files[i] = sample
			self._file_hashes[i] = sample
			# self._reader.seek(sample.compressed_length, 1)

		self._reader.seek(reader_pos, 0)
		self._content_ready = True

	def dump_data(self) -> dict[str, Any]:
		if not self._content_ready:
			return super().dump_data()
		return super().dump_data() | {
			"num_samples": self.num_samples,
			"version": self.version,
			"flags": self.flags,
			
			"files": [sample.dump_data() for sample in self._files]
		}
