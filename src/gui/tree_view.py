from imgui_bundle import ImVec2, imgui

from gui.app_data import AppData, FolderNode

def render_tree(app_data: AppData, node: FolderNode):
	open: bool = imgui.tree_node_ex("##" + node.name, imgui.TreeNodeFlags_.span_full_width.value | imgui.TreeNodeFlags_.frame_padding.value | imgui.TreeNodeFlags_.open_on_double_click.value | imgui.TreeNodeFlags_.open_on_arrow.value)
	if imgui.is_mouse_double_clicked(0) and imgui.is_item_hovered():
		app_data.set_current_node(node)
	imgui.same_line()
	imgui.align_text_to_frame_padding()
	imgui.image(1, ImVec2(imgui.get_text_line_height(), imgui.get_text_line_height()))
	imgui.same_line()
	imgui.text(node.name)
	if open:
		for folder in node.folders.values():
			render_tree(app_data, folder)

		imgui.tree_pop()

def render_tree_view(app_data: AppData):
	flags: imgui.WindowFlags =  imgui.WindowFlags_.no_collapse.value | imgui.WindowFlags_.no_move.value
	if not imgui.begin("Tree View", None, flags)[0]:
		imgui.end()
		return

	style: imgui.Style = imgui.get_style()
	imgui.push_style_var(imgui.StyleVar_.item_spacing.value, ImVec2(style.item_spacing.x, 0))
	render_tree(app_data, app_data.root_node)
	imgui.pop_style_var()

	imgui.end()
