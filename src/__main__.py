from archives.archive import Archive
from archives.big import Big
from archives.wad import Wad
from binary_reader import BinaryReader
from utils.formats import Format

from json import dump
import pickle
from os import listdir, makedirs
from os.path import join, splitext, dirname

SRC_DIRECTORY = "X:\\SteamLibrary\\steamapps\\common\\L.A.Noire\\final\\pc"
# SRC_DIRECTORY = "examples"
OUT_DIRECTORY = "dump"

READ_GAME_FILES = True
DUMP_JSON = True
DUMP_ARCHIVE = True
PICKLE_DATA = False
LIMIT_FILE = True

ARCHIVE_NAMES = ["cases_1_1.big.pc"]
OUT_FILES = [Format.BIN]

def read_game_files() -> dict[str, Archive]:
	print("Reading game files")
	archives: dict[str, Archive] = {}

	for archive_name in listdir(SRC_DIRECTORY):
		(full_type, extension) = splitext(archive_name)
		(_, file_type) = splitext(full_type)
		archive_path: str = join(SRC_DIRECTORY, archive_name)

		assert extension != "pc" "Can only read PC files."
		assert file_type != ".big" or file_type != ".wad" "Can only read BIG and WAD files."

		if LIMIT_FILE and archive_name not in ARCHIVE_NAMES:
			continue

		print(f"\tReading: {archive_name}...", end="")

		with open(archive_path, "rb") as archive_file:

			reader = BinaryReader(archive_file)

			archive: Archive
			if file_type == ".big":
				archive = Big(archive_path, archive_name)
			else:
				archive = Wad(archive_path, archive_name)

			archive.read_header(reader)
			archive.read_files(reader)
			archive.read_contents(reader)
			archives[archive_name] = archive

		print("Done")

	return archives

def read_pickle_file() -> dict[str, Archive]:
	print("Reading pickle file...", end = "")
	archives: dict[str, Archive] = {}
	
	with open(join(OUT_DIRECTORY, "archive_data.pickle"), "rb") as file:
		archives = pickle.load(file)

	print("Done")
	return archives

def dump_archives(archives: dict[str, Archive]):
	print("Dumping archive files.")

	for archive_name, archive in archives.items():
		if LIMIT_FILE and archive_name not in ARCHIVE_NAMES:
			continue

		print(f"\tDumping: {archive_name}...", end="")

		with open(archive.file_path, "rb") as archive_file:
			for file_data in archive.get_files():
				if file_data.type not in OUT_FILES:
					continue

				files: list[tuple[int, int, str]] = file_data.output_file()
				for (offset, size, name) in files:
					out_path: str = join(archive.out_path, name) # type: ignore
					makedirs(dirname(out_path), exist_ok = True)
					
					with open(out_path, "wb") as out_file:
						archive_file.seek(offset, 0)
						out_file.write(archive_file.read(size))

		print("Done")

def dump_json_data(archives: dict[str, Archive]):
	print("Dumping JSON data.")

	# headers: list[str] = []

	for archive_name, archive in archives.items():
		if LIMIT_FILE and archive_name not in ARCHIVE_NAMES:
			continue

		print(f"\tDumping: {archive_name}...", end="")

		# for file in archive.get_files():
		# 	if file.get_header() not in headers:
		# 		headers.append(file.get_header())

		makedirs(archive.out_path, exist_ok = True)
		with open(archive.out_json_path, "w") as out_file:
			dump(archive.dump_data(), out_file, indent="\t")

		print("Done")

	# with open(join(OUT_DIRECTORY, "headers.json"), "w") as file:
	# 	dump(headers, file, indent="\t")

def write_pickle_file(archives: dict[str, Archive]):
	print("Writing pickle file...", end = "")

	makedirs(OUT_DIRECTORY, exist_ok = True)
	with open(join(OUT_DIRECTORY, "archive_data.pickle"), "wb") as file:
		pickle.dump(archives, file)

	print("Done")

def main():
	archives: dict[str, Archive] = read_game_files() if READ_GAME_FILES else read_pickle_file()

	if DUMP_JSON:
		dump_json_data(archives)
	if DUMP_ARCHIVE:
		dump_archives(archives)
	if PICKLE_DATA:
		write_pickle_file(archives)


if __name__ == "__main__":
	main()
