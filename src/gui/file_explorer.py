from archives.archive import Archive
from files.base import BaseFile
from gui.app_info import APP

from imgui_bundle import imgui

class FileExplorer():
	def __init__(self) -> None:
		pass

	def render(self, window_flags: int) -> None:
		if not imgui.begin("File View", None, window_flags)[0]:
			imgui.end()
			return

		if imgui.arrow_button("##directory_up", imgui.Dir_.up.value):
			if APP.current_file != None:
				APP.move_up_file()
			elif APP.current_archive != None:
				APP.close_archive()
			else:
				APP.move_up_directory()

		imgui.same_line()
		imgui.text(str(APP.current_directory))

		table_flags: int = imgui.TableFlags_.sortable.value | imgui.TableFlags_.row_bg.value | imgui.TableFlags_.sortable.value | imgui.TableFlags_.borders.value | imgui.TableFlags_.sizing_fixed_fit.value
		imgui.begin_group()
		if imgui.begin_table("##file_table", 3, table_flags, imgui.ImVec2(0, 200)):
			imgui.table_setup_column("Name", imgui.TableColumnFlags_.width_stretch.value | imgui.TableColumnFlags_.default_sort.value, 5)
			imgui.table_setup_column("Size", imgui.TableColumnFlags_.width_stretch.value, 1)
			imgui.table_setup_column("Type", imgui.TableColumnFlags_.width_stretch.value, 1)
			imgui.table_setup_scroll_freeze(0, 1)
			imgui.table_headers_row()

			for file in APP.get_files():
				imgui.table_next_row()
				imgui.table_set_column_index(0)
				name: str = file.name
				if file.is_game_file:
					name += f" ({hex(file.hash)})"

				if imgui.selectable(name, APP.selected == file.file, imgui.SelectableFlags_.allow_double_click.value)[0]:
					if imgui.is_mouse_double_clicked(0):
						if file.is_dir:
							APP.move_down_directory(file.name)
						elif file.is_archive:
							APP.open_archive(file.name)
						elif file.is_game_archive_file:
							print("Move down file:", APP.move_down_file(file.hash))
					else:
						APP.selected = file.file
						if isinstance(file.file, BaseFile):
							file.file.read_contents()

				imgui.table_set_column_index(1)
				imgui.text(f"{file.size}")
				imgui.table_set_column_index(2)
				if isinstance(file.file, Archive):
					imgui.text(file.file.type.name + " Archive")
				elif isinstance(file.file, BaseFile):
					imgui.text(file.file.type.name)
				elif file.is_dir:
					imgui.text("Folder")
				else:
					imgui.text("File")

		imgui.end_table()
		imgui.end_group()

		imgui.end()
