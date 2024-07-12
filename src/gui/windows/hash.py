from imgui_bundle import ImVec2, imgui

from gui.app_data import AppData
from utils.dictionaries import CRC32_KEY

def crc32_hash(value: str) -> int:
	value = value.lower()

	result: int = 0xFFFFFFFF

	for i in range(len(value)):
		symbol: int = ord(value[i])

		result = CRC32_KEY[(result & 0xFF) ^ symbol] ^ (result >> 8)

	return ~(result & 0xFFFFFFFF) & 0xFFFFFFFF

def render_hash_window(app_data: AppData, show_hash_window: bool) -> bool:
	imgui.set_next_window_size(ImVec2(500, 100))
	(is_open, show) = imgui.begin("Hash", show_hash_window, imgui.WindowFlags_.no_resize.value)
	show = show or False
	if not is_open:
		imgui.end()
		return show

	window_width: float = imgui.get_window_width()
	text_width: float = imgui.calc_text_size("Input").x + imgui.get_style().item_inner_spacing.x

	imgui.push_item_width(-text_width)
	(entered, app_data.tools.string) = imgui.input_text("Input", app_data.tools.string, imgui.InputTextFlags_.enter_returns_true.value | imgui.InputTextFlags_.auto_select_all.value)
	imgui.pop_item_width()

	if entered:
		app_data.tools.hashed_string = crc32_hash(app_data.tools.string)

	imgui.push_item_width((window_width - text_width) / 2)
	imgui.input_text("##IntHash", hex(app_data.tools.hashed_string), imgui.InputTextFlags_.read_only.value)
	imgui.pop_item_width()
	imgui.same_line()
	imgui.push_item_width(-text_width)
	imgui.input_text("Hash##HexHash", str(app_data.tools.hashed_string), imgui.InputTextFlags_.read_only.value)
	imgui.pop_item_width()

	imgui.end()
	return show
