from pathlib import Path
from archives.archive import Archive
from archives.big import Big
from archives.wad import Wad
from binary_reader import BinaryReader
from utils.formats import Format

from json import dump
import pickle
from collections import Counter

SRC_DIRECTORY: Path = Path("X:\\SteamLibrary\\steamapps\\common\\L.A.Noire\\final\\pc")
# SRC_DIRECTORY = "examples"
OUT_DIRECTORY: Path = Path("dump")

READ_GAME_FILES: bool = True
DUMP_JSON: bool = True
DUMP_ARCHIVE: bool = False
PICKLE_DATA: bool = False
LIMIT_ARCHIVE: bool = True

ARCHIVE_NAMES: list[str] = ["vehicles.big.pc"]
OUT_FILES = Format

def read_game_files() -> dict[str, Archive]:
	print("Reading game files")
	archives: dict[str, Archive] = {}

	for archive_path in SRC_DIRECTORY.iterdir():
		archive_name: str = archive_path.name
		extension: str = archive_path.suffix
		file_type: str = Path(archive_path.stem).suffix

		assert extension != "pc" "Can only read PC files."
		assert file_type != ".big" or file_type != ".wad" "Can only read BIG and WAD files."

		if LIMIT_ARCHIVE and archive_name not in ARCHIVE_NAMES:
			continue

		print(f"\tReading: {archive_name}...", end="")

		archive: Archive
		if file_type == ".big":
			archive = Big(archive_name, Path(archive_name), archive_path)
		else:
			archive = Wad(archive_name, Path(archive_name), archive_path)

		archive.open()
		archive.read_header()
		archive.read_file_headers()
		archive.read_file_contents()
		archive.close()
		archives[archive_name] = archive

		print("Done")

	return archives

def read_pickle_file() -> dict[str, Archive]:
	print("Reading pickle file...", end = "")
	archives: dict[str, Archive] = {}
	
	with open(OUT_DIRECTORY / "archive_data.pickle", "rb") as file:
		archives = pickle.load(file)

	print("Done")
	return archives

def dump_archives(archives: dict[str, Archive]):
	print("Dumping archive files.")

	for archive_name, archive in archives.items():
		if LIMIT_ARCHIVE and archive_name not in ARCHIVE_NAMES:
			continue

		print(f"\tDumping: {archive_name}...", end="")

		archive.open()
		for file_data in archive.files:
			if file_data.type not in OUT_FILES:
				continue

			files: list[tuple[int, int, str, BinaryReader]] = file_data.output_file()
			for (offset, size, name, reader) in files:
				path: Path = Path(OUT_DIRECTORY, *archive.archive_name.replace("_", ".").split("."), f"{archive.name}.json", name)
				path.parent.mkdir(parents = True, exist_ok = True)
				reader.seek(offset, 0)
				path.write_bytes(reader.read_chunk(size))

		archive.close()

		print("Done")

def dump_json_data(archives: dict[str, Archive]):
	print("Dumping JSON data.")

	headers: list[str] = []

	for archive_name, archive in archives.items():
		if LIMIT_ARCHIVE and archive_name not in ARCHIVE_NAMES:
			continue

		print(f"\tDumping: {archive_name}...", end="")
		headers.extend([file.get_type() for file in archive.files])

		path: Path = Path(OUT_DIRECTORY, *archive.archive_name.replace("_", ".").split("."), f"{archive.name}.json")
		path.parent.mkdir(parents = True, exist_ok = True)
		with open(path, "w") as out_file:
			dump(archive.dump_data(), out_file, indent="\t")

		print("Done")

	with open(OUT_DIRECTORY / "headers.json", "w") as file:
		dump(Counter(headers), file, indent="\t", sort_keys=True)

def write_pickle_file(archives: dict[str, Archive]):
	print("Writing pickle file...", end = "")

	OUT_DIRECTORY.mkdir(parents = True, exist_ok = True)
	with open(OUT_DIRECTORY / "archive_data.pickle", "wb") as file:
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
	from gui import Gui

	gui = Gui()
	gui.run()

	# main() 
