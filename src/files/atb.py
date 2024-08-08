from typing import Any
from utils.dictionaries import ATB_POINTER_TYPES, ATB_TYPES, OBJECT_NAME_HASHES
from utils.formats import Format
from binary_reader import BinaryReader
from files.base import BaseFile

class ATB(BaseFile):
	type: Format = Format.ATB

	num_containers: int
	containers: list[dict[str, Any]]
	
	def __init__(self, archive: Any, hash: int, offset: int = 0, size: int = 0) -> None:
		super().__init__(archive, hash, offset, size)

	def read_header(self) -> None:
		if not self._open or self._reader == None:
			return
		
		reader_pos: int = self._reader.seek(self.offset)

		self.header = self._reader.read_string(4)
		self.num_containers = self._reader.read_uint16()
		self.containers = [None] * self.num_containers # type: ignore

		self._reader.seek(reader_pos)

	def read_contents(self) -> None:
		if not self._open or self._reader == None:
			return
		
		reader_pos: int = self._reader.seek(self.offset + 4 + self._reader.UINT16)

		# for i in range(self.num_containers):
		# 	container: dict[str, Any] = self.read_object(self._reader)
		# 	self.containers[i] = container

		self._reader.seek(reader_pos)
		self._content_ready = True

	def read_object(self) -> dict[str, Any]:
		if not self._open or self._reader == None:
			return {}
		
		hash: int = self._reader.read_uint32()
		name: str = self._reader.read_sized_string(BinaryReader.BYTE)

		type: str = OBJECT_NAME_HASHES.get(str(hash), "Object")

		object: dict[str, Any] = {
			"hash": hash,
			"name": name,
			"type": type,
			"variables": []
		}

		while True:
			end, variables = self.read_variables()
			if end == True:
				break
			object["variables"].append(variables)

		array_size: int = self._reader.read_uint16()
		if array_size > 0:
			object["elements"] = []
			
			for _ in range(array_size):
				element: dict[str, Any] = self.read_object()
				object["elements"].append(element) # type: ignore

		return object

	def read_variables(self, array_type: int = 0) -> tuple[bool, dict[str, Any]]:
		if not self._open or self._reader == None:
			return True, {}
		
		type_value: int = self._reader.read_uint8() if array_type == 0 else array_type
		
		if type_value == 0:
			return True, {}

		type: str = ATB_TYPES.get(type_value, "element")
		hash: int = self._reader.read_uint32() if array_type == 0 else 0
		name: str = OBJECT_NAME_HASHES.get(str(hash), hex(hash))

		object: dict[str, Any] = {
			"hash": hash,
			"name": name,
			"type": type
		}

		if ATB_POINTER_TYPES.get(type_value, False) == True:
			string_len: int = self._reader.read_int16()
			if (string_len != -1) and (string_len != 0):
				value = self._reader.read_string(string_len)
				return False, object | {
					"value": value,
					"real_size": string_len,
				}
			
			return False, object | {
				"value": "",
				"real_size": string_len
			}

		value: Any = ""
		if (type_value == 70) or (type_value == 30):
			value = self._reader.read_uint32()
			if value != 0 or type_value == 70:
				sub_name: str = OBJECT_NAME_HASHES.get(str(value), hex(value))

				child_object: list[dict[str, Any]] = []
				while True:
					end, variables = self.read_variables()
					if end == True:
						break
					child_object.append(variables)

				return False, object | {
					"value": sub_name,
					"object": child_object
				}	

		elif type_value == 60:
			array_type = self._reader.read_uint8()
			array_size: int = self._reader.read_uint16()

			array: list[Any] = self.read_array(array_type, array_size)
			return False, object | {
				"elements": array
			}
		elif type_value == 50:
			value = bin(self._reader.read_uint64())
		elif type_value == 40:
			value = self._reader.read_int16()
		elif type_value == 10:
			value = [self._reader.read_float32() for _ in range(4)]
		elif type_value == 9:
			value = self._reader.read_uint64()
		elif type_value == 7:
			value = [self._reader.read_float32() for _ in range(16)]
		elif type_value == 6:
			value = [self._reader.read_float32() for _ in range(2)]
		elif type_value == 5:
			value = [self._reader.read_float32() for _ in range(3)]
		elif type_value == 4:
			value = self._reader.read_uint8()
		elif type_value == 3:
			value = self._reader.read_float32()
		elif type_value == 2:
			value = self._reader.read_uint32()
		elif type_value == 1:
			value = self._reader.read_int32()
		
		return False, object | {
			"value": value
		}

	def read_array(self, type: int, size: int) -> list[Any]:
		if not self._open or self._reader == None:
			return []
		
		return [self.read_variables(type)[1] for _ in range(size)]

	def dump_data(self) -> dict[str, Any]:
		if not self._content_ready:
			return super().dump_data()
		return super().dump_data() | {
			"num_containers": self.num_containers,
			"containers": self.containers
		}
