from typing import Callable
from imgui_bundle import imgui
from files.fsb4 import FSB4
from gui.files.base import BaseFileWindow
from files.base import BaseAudioFile, BaseFile

class AudioPlayer(BaseFileWindow):
	audio_files: list[BaseAudioFile]

	def __init__(self, file: BaseFile | BaseAudioFile, terminate: Callable[[], None]) -> None:
		super().__init__(file, terminate)

		if isinstance(file, FSB4):
			self.audio_files = file.files
		elif isinstance(file, BaseAudioFile):
			self.audio_files = [file]

	def render_player(self):
		if not imgui.begin_tab_item("Player"):
			return

		table_flags: imgui.TableFlags = imgui.TableFlags_.resizable.value + imgui.TableFlags_.reorderable.value | imgui.TableFlags_.sortable.value | imgui.TableFlags_.borders_outer.value | imgui.TableFlags_.borders_inner_v.value | imgui.TableFlags_.scroll_y.value
		if imgui.begin_table("##AudioPlayer", 4, table_flags):
			column_flags: imgui.TableColumnFlags = imgui.TableColumnFlags_.width_fixed.value
			imgui.table_setup_column("Name", column_flags, 240)
			imgui.table_setup_column("Type", column_flags, 80)
			imgui.table_setup_column("Length", column_flags, 80)
			imgui.table_setup_column("Size", column_flags, 80)

			imgui.table_setup_scroll_freeze(1, 1)

			imgui.table_headers_row()

			flags: imgui.SelectableFlags = imgui.SelectableFlags_.allow_double_click.value | imgui.SelectableFlags_.span_all_columns.value | imgui.internal.SelectableFlagsPrivate_.no_pad_with_half_spacing.value
			for file in self.audio_files:
				imgui.table_next_row()

				if imgui.table_set_column_index(0):
					imgui.selectable(file.name, False, flags)

					imgui.table_next_column()
					imgui.text(file.type.name)
					
					imgui.table_next_column()
					imgui.text(f"{int(file.length // 60):2}:{int(file.length % 60)}")
					
					imgui.table_next_column()
					imgui.text(str(file.size))
					
			imgui.end_table()
			
		imgui.end_tab_item()

	def render(self) -> None:
		(visible, is_open) = imgui.begin(f"{self.file.name} - Audio Player", True)
		if not is_open:
			imgui.end()
			self.terminate()
			return
		if not visible:
			imgui.end()
			return

		if imgui.begin_tab_bar("##AudioPlayerTabBar"):
			self.render_player()
			imgui.end_tab_bar()
		
		imgui.end()
