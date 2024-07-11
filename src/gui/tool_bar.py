from imgui_bundle import imgui, ImVec2

from gui.app_data import AppData
internal = imgui.internal

def render_tool_bar(app_data: AppData):
	style: imgui.Style = imgui.get_style()
	if internal.begin_viewport_side_bar("##MenuBar", imgui.get_main_viewport(), imgui.Dir_.up.value, 0, imgui.WindowFlags_.none.value):
		imgui.push_style_var(imgui.StyleVar_.item_spacing.value, ImVec2(style.frame_padding.y, style.item_spacing.y))

		imgui.arrow_button("##BackButton", imgui.Dir_.left.value)
		imgui.same_line()
		imgui.arrow_button("##ForwardButton", imgui.Dir_.right.value)
		imgui.same_line()
		if imgui.arrow_button("##UpButton", imgui.Dir_.up.value):
			app_data.set_current_node(app_data.current_node.parent)

		imgui.same_line()
		imgui.push_item_width(-(2 * imgui.get_frame_height() + 4 * style.item_spacing.x + 1 + max(imgui.get_window_width() * 0.2, 200)))
		imgui.input_text("###Path", str(app_data.current_node.path), imgui.InputTextFlags_.auto_select_all.value)
		imgui.pop_item_width()

		imgui.same_line()
		imgui.arrow_button("##GoButton", imgui.Dir_.right.value)

		imgui.same_line()
		internal.separator_ex(internal.SeparatorFlags_.vertical.value)

		imgui.same_line()
		imgui.push_item_width(-(imgui.get_frame_height() + style.item_spacing.x))
		imgui.input_text_with_hint("###Search", "Search", "", imgui.InputTextFlags_.auto_select_all.value)
		imgui.pop_item_width()

		imgui.same_line()
		imgui.arrow_button("##SearchButton", imgui.Dir_.right.value)

		imgui.pop_style_var()
	imgui.end()
