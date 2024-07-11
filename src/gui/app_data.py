from pathlib import Path

from archives.archive import Archive
from archives.big import Big
from archives.wad import Wad

class Node:
	name: str
	path: Path
	full_path: Path

	size: int
	type: str
	attributes: list[str]

	def __init__(self, name: str, path: Path, full_path: Path) -> None:
		self.name = name
		self.path = path
		self.full_path = full_path

		self.size = 0
		self.type = ""
		self.attributes = []

class FolderNode(Node):
	parent: 'FolderNode'

	is_archive: bool
	is_game_archive: bool

	files: dict[str, 'FileNode']
	folders: dict[str, 'FolderNode']

	def __init__(self, name: str, path: Path, full_path: Path) -> None:
		super().__init__(name, path, full_path)

		self.is_archive = False
		self.is_game_file = False

		self.files = {}
		self.folders = {}

		self.type = "Folder"

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

class FileNode(Node):
	name: str
	path: Path
	full_path: Path
	
	parent: FolderNode

	is_game_file: bool

	def __init__(self, name: str, path: Path, full_path: Path) -> None:
		super().__init__(name, path, full_path)

		self.is_game_file = False

		self.type = "File"

class Tools:
	hashed_string: int = 0
	string: str = ""

class AppData:
	game_path: Path

	tools: Tools

	status_text: dict[str, str]

	root_node: FolderNode
	current_node: FolderNode

	archives: list[Archive]

	def __init__(self, game_path: Path) -> None:
		self.game_path = game_path
		self.root_node = FolderNode("L.A. Noire", Path(""), Path(self.game_path))
		self.root_node.parent = self.root_node
		self.current_node = self.root_node

		self.tools = Tools()

		self.status_text = {
			"file_scan": "",
			"archive_scan": "",
			"folders": "",
			"files": "",
		}

	def set_status_text(self, topic: str, status: str):
		self.status_text[topic] = status

	def set_current_node(self, node: FolderNode):
		self.current_node = node
		self.set_status_text("folders", f"Folders: {len(node.folders)}")
		self.set_status_text("files", f"Files: {len(node.files)}")

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
		self.set_current_node(self.root_node)

	def archive_generate_node(self, path: Path) -> FolderNode:
		archive_node = FolderNode(path.name, path, self.game_path / path)
		archive_node.is_archive = True
		archive_node.type = "Archive"

		self.set_status_text("file_scan", f"Scanning archive: {path.name}...")
		
		archive: Archive
		if path.suffixes[-2] == ".big":
			archive = Big(path.name, path, self.game_path / path)
			archive_node.attributes.append("BIG Archive")
		else:
			archive = Wad(path.name, path, self.game_path / path)
			archive_node.attributes.append("WAD Archive")

		archive.open()
		archive.scan_archive()
		archive.close()

		for file in archive.files:
			parent_node: FolderNode | None = archive_node

			self.set_status_text("archive_scan", f"Scanning game file: {file.name}...")

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
			file_node.type = file.type.name
			parent_node.add_file(file_node)

		return archive_node
