from imgui_bundle import imgui
from gui.app_data import AppData

def render_info_view(app_data: AppData):
	flags: imgui.WindowFlags =  imgui.WindowFlags_.no_collapse.value | imgui.WindowFlags_.no_move.value
	if not imgui.begin("File Info", None, flags)[0]:
		imgui.end()
		return

	imgui.text("File Info!")

	imgui.end()
