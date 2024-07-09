from pathlib import Path

from archives.archive import Archive

class FolderNode:
	name: str
	path: Path
	full_path: Path

	parent: 'FolderNode'

	files: list[Path]
	children: list['FolderNode']

	def __init__(self, name: str, path: Path, full_path: Path) -> None:
		self.name = name
		self.path = path
		self.full_path = full_path

		self.files = []
		self.children = []

	def add_file(self, file: Path) -> None:
		self.files.append(file)

	def remove_file(self, file: Path) -> None:
		self.files.remove(file)

	def add_child(self, child: 'FolderNode') -> None:
		self.children.append(child)
		child.parent = self


class AppData:
	game_path: Path

	root_node: FolderNode
	current_node: FolderNode

	archives: list[Archive]

	def __init__(self, game_path: Path) -> None:
		self.game_path = game_path


	def generate_node(self):
		self.root_node = FolderNode("L.A. Noire", Path(""), Path(self.game_path))

		for path in self.game_path.glob("**/*"):
			relative: Path = path.relative_to(self.game_path)
			is_file: bool = path.is_file()

			parent_node: FolderNode | None = None

			parent_node = self.root_node



			if is_file:
				if path.suffix == ".pc":
					pass
				else:
					parent_node.add_file(path)
