from pathlib import Path
from dataclasses import dataclass

from archives.archive import Archive
from archives.big import Big
from archives.wad import Wad
from files.base import BaseFile
from gui.files.audio_player import AudioPlayer
from gui.files.base import BaseFileWindow
from utils.formats import Format, format_file_size

class Node:
	name: str
	path: Path
	full_path: Path

	icon: int
	size: str
	type: str
	attributes: list[str]

	def __init__(self, name: str, path: Path, full_path: Path) -> None:
		self.name = name
		self.path = path
		self.full_path = full_path

		self.size = ""
		self.type = ""
		self.attributes = []

	def get_size(self):
		return self.size

class FolderNode(Node):
	parent: 'FolderNode'

	is_archive: bool
	is_game_archive: bool

	type = "Folder"
	files: dict[str, 'FileNode']
	folders: dict[str, 'FolderNode']

	def __init__(self, name: str, path: Path, full_path: Path) -> None:
		super().__init__(name, path, full_path)

		self.is_archive = False
		self.is_game_archive = False

		self.files = {}
		self.folders = {}

	def add_file(self, file: 'FileNode') -> None:
		self.files[file.name] = file

	def get_file(self, file: 'FileNode') -> 'FileNode | None':
		return self.files.get(file.name)

	def get_file_by_name(self, name: str) -> 'FileNode | None':
		return self.files.get(name)

	def remove_file(self, file: 'FileNode') -> 'FileNode | None':
		return self.files.pop(file.name, None)

	def add_folder(self, child: 'FolderNode') -> None:
		self.folders[child.name] = child
		child.parent = self

	def get_folder(self, child: 'FolderNode') -> 'FolderNode | None':
		return self.folders.get(child.name)

	def get_folder_by_name(self, name: str) -> 'FolderNode | None':
		return self.folders.get(name)

	def remove_folder(self, child: 'FolderNode') -> 'FolderNode | None':
		return self.folders.pop(child.name)

	def get_size(self):
		return f"{len(self.files) + len(self.folders)} Items"

class FileNode(Node):
	parent: FolderNode

	file: BaseFile | None
	is_game_file: bool

	type: str = "File"

	def __init__(self, name: str, path: Path, full_path: Path) -> None:
		super().__init__(name, path, full_path)

		self.file = None
		self.is_game_file = False

class Tools:
	hashed_string: int = 0
	string: str = ""

@dataclass
class FileAssociation:
	format: Format = Format.UNKNOWN
	name: str = "Unknown"
	icon: int = 0
	action: type[BaseFileWindow] | None = None

	def apply_to_node(self, node: Node):
		node.type = self.name
		node.icon = self.icon

class AppData:
	game_path: Path

	tools: Tools
	icons: dict[str, int]
	file_associations: dict[str, FileAssociation]

	status_text: dict[str, str]

	root_node: FolderNode
	current_node: FolderNode
	selected_node: Node | None

	open_windows: list[BaseFileWindow]

	archives: list[Archive]

	def __init__(self, game_path: Path) -> None:
		self.game_path = game_path
		self.root_node = FolderNode("L.A. Noire", Path(""), Path(self.game_path))
		self.root_node.parent = self.root_node
		self.current_node = self.root_node
		self.selected_node = None

		self.tools = Tools()
		self.icons = {}
		self.file_associations = {}

		self.open_windows = []

		self.status_text = {
			"file_scan": "",
			"archive_scan": "",
			"folders": "",
			"files": "",
		}

	def add_file_associations(self):
		FolderNode.icon = self.icons.get("folder", 0)
		FileNode.icon = self.icons.get("unknown", 0)
		FileAssociation.icon = self.icons.get("unknown", 0)

		self.file_associations["BIG"] = FileAssociation(Format.BIG, "BIG Archive", self.icons.get("archive", 0))
		self.file_associations["WAD"] = FileAssociation(Format.WAD, "WAD Archive", self.icons.get("archive", 0))
		
		self.file_associations["SGES"] = FileAssociation(Format.SGES, "Segmented (SGES)", self.icons.get("file", 0))
		self.file_associations["DDS "] = FileAssociation(Format.DDS, "DirectDraw Surface (DDS)", self.icons.get("image_file", 0))
		self.file_associations["FSB4"] = FileAssociation(Format.FSB4, "FMOD Sound Bank (FSB4)", self.icons.get("audio_file", 0), AudioPlayer)
		self.file_associations["OggS"] = FileAssociation(Format.OGG, "Ogg Audio (OggS)", self.icons.get("audio_file", 0), AudioPlayer)
		self.file_associations["BIKi"] = FileAssociation(Format.BINK, "Bink Video (BIKi)", self.icons.get("video_file", 0))
		self.file_associations["ATB\x04"] = FileAssociation(Format.ATB, "Config (ATB)", self.icons.get("config_file", 0))
		self.file_associations["FNT\x03"] = FileAssociation(Format.FNT, "Font (FNT)", self.icons.get("font_file", 0))

	def set_status_text(self, topic: str, status: str):
		self.status_text[topic] = status

	def set_current_node(self, node: FolderNode):
		self.current_node = node
		self.set_status_text("folders", f"Folders: {len(node.folders)}")
		self.set_status_text("files", f"Files: {len(node.files)}")
		self.set_selected_node(None)

	def set_selected_node(self, node: Node | None):
		self.selected_node = node

	def generate_node(self):
		for path in self.game_path.glob("**/*"):
			relative: Path = path.relative_to(self.game_path)
			is_file: bool = path.is_file()

			self.set_status_text("file_scan", f"Scanning {"file" if is_file else "folder"}: {str(relative)}...")
			parent_node: FolderNode | None = self.root_node

			current_path: Path = Path("")
			for part in relative.parts[: -1 if is_file else None]:
				current_path /= part

				node: FolderNode | None = parent_node.get_folder_by_name(part)
				if node == None:
					node = FolderNode(part, current_path, self.game_path / current_path)

				parent_node.add_folder(node)
				parent_node = node

			if is_file:
				if path.suffix == ".pc":
					parent_node.add_folder(self.archive_generate_node(relative))
				else:
					parent_node.add_file(FileNode(path.name, path, self.game_path / path))

		self.set_status_text("file_scan", "Scanning: Done")
		self.set_status_text("archive_scan", "")

	def archive_generate_node(self, path: Path) -> FolderNode:
		archive_node = FolderNode(path.name, path, self.game_path / path)
		archive_node.is_archive = True
		archive_node.type = "Archive"

		self.set_status_text("archive_scan", f"Scanning archive: {path.name}...")
		
		archive: Archive
		if path.suffixes[-2] == ".big":
			archive = Big(path.name, path, self.game_path / path)
			archive_node.attributes.append("BIG Archive")
			self.file_associations["BIG"].apply_to_node(archive_node)
		else:
			archive = Wad(path.name, path, self.game_path / path)
			archive_node.attributes.append("WAD Archive")
			self.file_associations["WAD"].apply_to_node(archive_node)

		archive.open()
		archive.scan_archive()
		archive.close()

		for file in archive.files:
			parent_node: FolderNode | None = archive_node

			self.set_status_text("file_scan", f"Scanning game file: {file.name}...")

			current_path: Path = Path("")
			for part in file.path.parts[: -1]:
				current_path /= part

				node: FolderNode | None = parent_node.get_folder_by_name(part)
				if node == None:
					node = FolderNode(part, current_path, archive.full_path / current_path)

				parent_node.add_folder(node)
				parent_node = node

			file_node: FileNode = FileNode(file.path.name, file.path, archive.full_path / file.path)
			file_node.is_game_file = True
			file_node.file = file
			file_node.size = format_file_size(file.size)
			file_node.type = file.type.name
			file_node.attributes.extend(file.get_attributes())
			if association := self.file_associations.get(file.header):
				association.apply_to_node(file_node)
			parent_node.add_file(file_node)

		return archive_node

	def open_file(self, file_node: FileNode):
		if file := file_node.file:
			if association := self.file_associations.get(file_node.file.header):
				if action := association.action:
					file.archive.open()
					file.archive.open_file(file)
					file.read_header()
					file.read_contents()
					file.archive.close()
					
					window = action(file, lambda : self.open_windows.remove(window))
					self.open_windows.append(window)

	def export_raw_file(self, file_node: FileNode):
		if file := file_node.file:
			file.archive.open()
			file.archive.open_file(file)
			file.export_raw_file(Path("export"))
			file.close()
			file.archive.close()

	def export_file(self, file_node: FileNode):
		if file := file_node.file:
			file.archive.open()
			file.archive.open_file(file)
			file.read_header()
			file.read_contents()
			file.export_file(Path("export"))
			file.close()
			file.archive.close()

	def export_contents(self, file_node: FileNode):
		if file := file_node.file:
			file.archive.open()
			file.archive.open_file(file)
			file.read_header()
			file.read_contents()
			file.export_contents(Path("export"))
			file.close()
			file.archive.close()
