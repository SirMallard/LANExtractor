from json import dump

def convert_dict():
	from LANoireTools.newscripts.dictionaries import FILE_FULLNAME_DICTIONARY, OBJECT_TYPES_DICTIONARY
	# FILE_FULLNAME_DICTIONARY: dict[int, str] = {}

	file_name_hashes: dict[int, str] = {}
	object_name_hashes: dict[int, str] = {}

	for k, v in FILE_FULLNAME_DICTIONARY.items():
		if len(v) == 16:
			try:
				_ = int(v, 16)
				continue
			except:
				pass

		file_name_hashes[k] = v

	for k, v in OBJECT_TYPES_DICTIONARY.items():
		object_name_hashes[int.from_bytes(k)] = v

	with open("name_hashes.json", "w") as file:
		dump({
			"object_name_hashes": object_name_hashes,
			"file_name_hashes": file_name_hashes
		}, file, indent="\t")

def main():
	print()

if __name__ == "__main__":
	main()
