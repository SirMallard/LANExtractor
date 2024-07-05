from json import dumps
from pathlib import Path
from files.base import BaseFile
from gui.app_info import APP

from imgui_bundle import imgui

class FileInfo():
	def __init__(self) -> None:
		pass

	def render(self, window_flags: int) -> None:
		if not imgui.begin("File Info", None, window_flags)[0]:
			imgui.end()

		selected_file = APP.get_selected_file()
		file = APP.get_file()
		
		if selected_file != None:
			imgui.separator_text(selected_file.name)

			imgui.text(f"name: {selected_file.name}")
			imgui.text(f"hash: {selected_file.hash}")
			imgui.text(f"size: {selected_file.size}")
			if isinstance(selected_file, BaseFile):
				imgui.text(f"type: {selected_file.get_type()}")

			imgui.text(f"is_file: {selected_file.is_file}")
			imgui.text(f"is_dir: {selected_file.is_dir}")
			imgui.text(f"is_archive: {selected_file.is_archive}")
			imgui.text(f"is_game_file: {selected_file.is_game_file}")
			imgui.text(f"is_game_archive_file: {selected_file.is_game_archive_file}")

			if isinstance(selected_file.file, BaseFile):
				if imgui.tree_node("Export"):
					if imgui.button("Export Selected File"):
						for (offset, size, name, reader) in selected_file.file.output_file():
							path: Path = Path("files", "export", name)
							path.parent.mkdir(parents = True, exist_ok = True)
							with path.open("wb") as out_file:
								pos: int = reader.tell()

								reader.seek(offset, 0)
								out_file.write(reader.read_chunk(size))
								
								reader.seek(pos, 0)

					imgui.tree_pop()
				if imgui.tree_node("DUMP"):
					imgui.text_unformatted(dumps(selected_file.file.dump_data(), indent="\t"))
					imgui.tree_pop()

		
		if file != None:
			imgui.separator_text(file.name)

			imgui.text(f"name: {file.name}")
			imgui.text(f"hash: {file.hash}")
			imgui.text(f"size: {file.size}")
			if isinstance(file, BaseFile):
				imgui.text(f"type: {file.get_type()}")

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
