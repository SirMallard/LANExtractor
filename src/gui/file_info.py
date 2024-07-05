from json import dumps
from files.base import BaseFile
from gui.app_info import APP

from imgui_bundle import imgui

class FileInfo():
	def __init__(self) -> None:
		pass

	def render(self, window_flags: int) -> None:
		if not imgui.begin("File Info", None, window_flags)[0]:
			imgui.end()

		file = APP.get_file()
		if file != None:
			imgui.separator_text(file.name)

			imgui.text(f"name: {file.name}")
			imgui.text(f"hash: {file.hash}")
			imgui.text(f"size: {file.size}")

			imgui.text(f"is_file: {file.is_file}")
			imgui.text(f"is_dir: {file.is_dir}")
			imgui.text(f"is_archive: {file.is_archive}")
			imgui.text(f"is_game_file: {file.is_game_file}")
			imgui.text(f"is_game_archive_file: {file.is_game_archive_file}")

			if isinstance(file.file, BaseFile):
				if imgui.tree_node("DUMP"):
					imgui.text_unformatted(dumps(file.file.dump_data(), indent="\t"))
					imgui.tree_pop()

		
		imgui.end()
