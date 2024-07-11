from imgui_bundle import ImVec2, imgui
from gui.app_data import AppData

def render_files(app_data: AppData):
	for folder in app_data.current_node.folders.values():
		imgui.table_next_row(imgui.TableRowFlags_.none.value, imgui.get_frame_height())

		if imgui.table_set_column_index(0):
			imgui.image(1, ImVec2(imgui.get_text_line_height(), imgui.get_text_line_height()))
			imgui.same_line()
			(hit, _) = imgui.selectable(folder.name, False, imgui.SelectableFlags_.allow_double_click.value | imgui.SelectableFlags_.span_all_columns.value | imgui.internal.SelectableFlagsPrivate_.no_pad_with_half_spacing.value, ImVec2(0, imgui.get_frame_height()))
			if hit:
				if imgui.is_mouse_double_clicked(0):
					app_data.set_current_node(folder)

			imgui.table_next_column()
			imgui.text(folder.type)

			imgui.table_next_column()
			imgui.text(str(folder.size))

			imgui.table_next_column()
			imgui.text(", ".join(folder.attributes))

	for file in app_data.current_node.files.values():
		imgui.table_next_row(imgui.TableRowFlags_.none.value, imgui.get_frame_height())

		if imgui.table_set_column_index(0):
			imgui.image(0, ImVec2(imgui.get_text_line_height(), imgui.get_text_line_height()))
			imgui.same_line()
			(hit, _) = imgui.selectable(file.name, False, imgui.SelectableFlags_.allow_double_click.value | imgui.SelectableFlags_.span_all_columns.value | imgui.internal.SelectableFlagsPrivate_.no_pad_with_half_spacing.value, ImVec2(0, imgui.get_frame_height()))

			imgui.table_next_column()
			imgui.text(file.type)

			imgui.table_next_column()
			imgui.text(str(file.size))

			imgui.table_next_column()
			imgui.text(", ".join(file.attributes))
		


def render_list_view(app_data: AppData):
	flags: imgui.WindowFlags =  imgui.WindowFlags_.no_collapse.value | imgui.WindowFlags_.no_move.value

	# imgui.push_style_var(imgui.StyleVar_.window_padding.value, ImVec2(0, 0))
	# imgui.push_style_var(imgui.StyleVar_.window_border_size.value, 0)
	# imgui.push_style_var(imgui.StyleVar_.frame_border_size.value, 0)
	if not imgui.begin("List View", None, flags)[0]:
		# imgui.pop_style_var(3)
		imgui.end()
		return
	# imgui.pop_style_var()

	style: imgui.Style = imgui.get_style()
	imgui.push_style_var(imgui.StyleVar_.cell_padding.value, ImVec2(style.cell_padding.x, 0))
	table_flags: imgui.TableFlags = imgui.TableFlags_.resizable.value + imgui.TableFlags_.reorderable.value | imgui.TableFlags_.sortable.value | imgui.TableFlags_.borders_outer.value | imgui.TableFlags_.borders_inner_v.value | imgui.TableFlags_.scroll_y.value
	if imgui.begin_table("##FileTable", 4, table_flags, ImVec2(0, 0)):
		column_flags: imgui.TableColumnFlags = imgui.TableColumnFlags_.width_fixed.value
		imgui.table_setup_column("Name", column_flags, 400)
		imgui.table_setup_column("Type", column_flags, 160)
		imgui.table_setup_column("Size", column_flags, 100)
		imgui.table_setup_column("Attributes", column_flags, 160)
		
		imgui.table_setup_scroll_freeze(1, 1)
		
		imgui.table_next_row(imgui.TableRowFlags_.headers.value, imgui.get_frame_height())
		
		for i in range(imgui.table_get_column_count()):
			if (not imgui.table_set_column_index(i)):
				continue
			imgui.table_header(imgui.table_get_column_name(i))

		render_files(app_data)


		imgui.end_table()
	imgui.pop_style_var()

	# imgui.pop_style_var(2)
	imgui.end()
