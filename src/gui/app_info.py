from pathlib import Path
from archives.archive import Archive
from archives.big import Big
from archives.wad import Wad
from files.base import BaseArchiveFile, BaseFile

"""

[PATHS]

split into folder\\folder\\folder\\archive\\file\\file\\file

"""

class AppFile:
	file: Path | Archive | BaseFile

	name: str
	hash: int
	size: int

	is_file: bool
	is_dir: bool
	is_archive: bool
	is_game_file: bool
	is_game_archive_file: bool

	def __init__(self, file: Path | Archive | BaseFile, name: str, hash: int, size: int) -> None:
		self.file = file
		self.name = name
		self.hash = hash
		self.size = size

	def update(self, is_file: bool,is_dir: bool,is_archive: bool,is_game_file: bool,is_game_archive_file: bool):
		self.is_file = is_file
		self.is_dir = is_dir
		self.is_archive = is_archive
		self.is_game_file = is_game_file
		self.is_game_archive_file = is_game_archive_file

class AppInfo:
	files: list[BaseArchiveFile]

	selected: Path | Archive | BaseFile | None

	current_directory: Path
	current_archive: Archive | None
	current_file: BaseArchiveFile | None

	def __init__(self) -> None:
		self.files = []

		self.selected = None

		self.current_directory = Path("X:\\SteamLibrary\\steamapps\\common\\L.A.Noire\\final\\pc")
		self.current_archive = None
		self.current_file = None

	def move_directory(self, directories: str) -> None:
		self.close_archive()
		self.selected = None

		self.current_directory = Path(directories)

	def move_up_directory(self) -> str:
		self.close_archive()
		self.selected = None

		old_directory: Path = self.current_directory
		self.current_directory = self.current_directory.parent
		return str(old_directory)

	def move_down_directory(self, folder: str) -> None:
		self.close_archive()
		self.selected = None

		self.current_directory /= folder


	def open_archive(self, archive_name: str) -> bool:
		self.close_archive()
		self.selected = None

		archive_path: Path = self.current_directory / archive_name
		suffixes: list[str] = archive_path.suffixes
		if len(suffixes) < 2:
			return False

		extension: str = suffixes[-1]
		file_type: str = suffixes[-2]
		
		if extension != ".pc":
			return False # "Can only read PC files."
		if file_type != ".big" and file_type != ".wad":
			return False # "Can only read BIG and WAD files."

		archive: Archive
		if file_type == ".big":
			archive = Big(str(archive_path), archive_name)
		else:
			archive = Wad(str(archive_path), archive_name)

		archive.open()
		archive.read_header()
		archive.read_file_headers()

		self.current_archive = archive

		return True

	def close_archive(self) -> None:
		self.close_all_files()
		self.selected = None

		if self.current_archive != None:
			self.current_archive.close()
			self.current_archive = None


	def open_file(self, hash: int) -> bool:
		self.selected = None

		file: BaseFile | None = None
		if self.current_file != None:
			file = self.current_file.get_file_by_hash(hash)
		elif self.current_archive != None:
			file = self.current_archive.get_file_by_hash(hash)

		if file == None:
			return False

		file.read_contents()
		if isinstance(file, BaseArchiveFile):
			self.files.append(file)
			self.current_file = file

		return True

	def close_file(self) -> bool:
		self.selected = None

		if self.current_file == None:
			return True

		self.files.pop().close()
		if len(self.files) > 0:
			self.current_file = self.files[-1]
		else:
			self.current_file = None

		return True

	def close_all_files(self) -> None:
		self.selected = None

		if self.current_file != None:
			for _ in range(len(self.files)):
				self.files.pop().close()
			self.current_file = None

	def move_files(self, files: list[int]) -> bool:
		self.close_all_files()
		self.selected = None

		for file in files:
			if not self.open_file(file):
				return False

		return True

	def move_up_file(self) -> BaseArchiveFile | None:
		self.selected = None

		file: BaseArchiveFile | None = self.current_file
		self.close_file()
		return file

	def move_down_file(self, hash: int) -> bool:
		return self.open_file(hash)

	def get_selected_file(self) -> AppFile | None:
		file: Path | Archive | BaseFile | None = self.selected
		if file == None:
			return None
		elif isinstance(file, BaseFile):
			app_file: AppFile = AppFile(file, file.get_name(), file.get_hash(), file.get_size())
			app_file.update(False, False, False, True, isinstance(file, BaseArchiveFile))
			return app_file
		elif isinstance(file, Archive):
			app_file = AppFile(file, file.name, -1, 0)
			app_file.update(False, False, True, False, False)
			return app_file
		else:
			app_file = AppFile(file, file.name, -1, file.stat().st_size)
			app_file.update(file.is_file(), file.is_dir(), file.suffix == ".pc", False, False)
			return app_file

	def get_file(self) -> AppFile | None:
		if self.current_file != None:
			file = self.current_file
			app_file: AppFile = AppFile(file, file.get_name(), file.get_hash(), file.get_size())
			app_file.update(False, False, False, True, True)
			return app_file
		elif self.current_archive != None:
			file = self.current_archive
			app_file = AppFile(file, file.name, -1, 0)
			app_file.update(False, False, True, False, False)
			return app_file
		else:
			file = self.current_directory
			app_file = AppFile(file, file.name, -1, file.stat().st_size)
			app_file.update(file.is_file(), file.is_dir(), file.suffix == ".pc", False, False)
			return app_file

	def get_files(self) -> list[AppFile]:
		app_files: list[AppFile] = []
		if self.current_file != None:
			for file in self.current_file.get_files():
				app_file: AppFile = AppFile(file, file.get_name(), file.get_hash(), file.get_size())
				app_file.update(False, False, False, True, isinstance(file, BaseArchiveFile))
				app_files.append(app_file)
		elif self.current_archive != None:
			for file in self.current_archive.get_files():
				app_file = AppFile(file, file.get_name(), file.get_hash(), file.get_size())
				app_file.update(False, False, False, True, isinstance(file, BaseArchiveFile))
				app_files.append(app_file)
		else:
			for file in [x for x in self.current_directory.iterdir()]:
				app_file = AppFile(file, file.name, -1, file.stat().st_size)
				app_file.update(file.is_file(), file.is_dir(), file.suffix == ".pc", False, False)
				app_files.append(app_file)
		
		return app_files

APP = AppInfo()
