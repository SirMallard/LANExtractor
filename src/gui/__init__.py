from imgui_bundle import ImVec2, imgui
from imgui_bundle.python_backends.glfw_backend import GlfwRenderer
from numpy import array

internal = imgui.internal
import OpenGL.GL as gl
import glfw
import sys
from PIL import Image

WINDOW_WIDTH: int = 1280
WINDOW_HEIGHT: int = 720
WINDOW_NAME: str = "L.A. Noire Extractor"

class Gui():
	window: glfw._GLFWwindow # type: ignore

	show_demo_window: bool = False
	show_style_editor: bool = False

	icons: dict[str, int]

	def __init__(self) -> None:
		self.icons = {}

	def load_image(self, file: str) -> int:
		image = Image.open(file)
		data = array(list(image.getdata())) # type: ignore

		imageID: int = gl.glGenTextures(1)
		gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
		gl.glBindTexture(gl.GL_TEXTURE_2D, imageID)
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_BORDER)
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_BORDER)
		gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_BASE_LEVEL, 0)
		gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAX_LEVEL, 0)
		gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, image.size[0], image.size[1], 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, data)
		return imageID

	def init_style(self) -> None:
		io: imgui.IO = imgui.get_io()
		io.config_flags |= imgui.ConfigFlags_.docking_enable.value
		io.config_flags |= imgui.ConfigFlags_.nav_enable_keyboard.value

		default: imgui.ImFont = io.fonts.add_font_from_file_ttf("C:\\Windows\\Fonts\\segoeui.ttf", 16)
		io.font_default = default

		style: imgui.Style = imgui.get_style()
		imgui.style_colors_light()
		style.tab_rounding = 0
		style.frame_border_size = 1
		style.tab_bar_border_size = 2
		style.window_menu_button_position = imgui.Dir_.none.value
		
		io.set_ini_filename("")

	def run(self) -> None:
		imgui.create_context()

		if not glfw.init():
			print("Could not initialize OpenGL context")
			sys.exit(1)

		# OS X supports only forward-compatible core profiles from 3.2
		glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
		glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 2)
		glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

		glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

		# Create a windowed mode window and its OpenGL context
		window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_NAME, None, None)

		if window == None:
			glfw.terminate()
			print("Could not create OpenGL window.")
			sys.exit(1)

		self.window = window
		glfw.make_context_current(self.window)

		with Image.open(f"{__file__}\\..\\..\\assets\\icon.png") as image:
			glfw.set_window_icon(self.window, 1, image)
		glfw.make_context_current(self.window)
		glfw.swap_interval(1)

		# We need to initialize the OpenGL backend (so that we can later call opengl3_new_frame)
		# imgui.backends.glfw_init_for_opengl(window.)
		imgui.backends.opengl3_init("#version 150")

		self.icons["folder"] = self.load_image("src\\assets\\folder.ico")
		self.icons["archive"] = self.load_image("src\\assets\\archive.ico")

		imgui.backends.opengl3_new_frame()

		self.init_style()
		
		impl = GlfwRenderer(self.window)

		first_time: bool = True
		while not glfw.window_should_close(self.window):
			glfw.poll_events()
			impl.process_inputs()

			# imgui.backends.glfw_new_frame()
			imgui.new_frame()

			self.render(first_time)

			gl.glClearColor(0.0, 0.0, 0.0, 1)
			gl.glClear(gl.GL_COLOR_BUFFER_BIT)

			imgui.render()
			impl.render(imgui.get_draw_data())
			glfw.swap_buffers(self.window)

			if first_time:
				first_time = False

		impl.shutdown()
		glfw.terminate()
	
	def quit(self):
		sys.exit(0)

	def render(self, first_time: bool):
		self.build_dockspace(first_time)

		self.render_menu_bar()
		self.render_status_bar()
		self.render_tool_bar()

		self.render_list_view()
		self.render_tree_view()
		self.render_info_view()

	def render_menu_bar(self):
		flags: imgui.WindowFlags = imgui.WindowFlags_.no_scrollbar.value | imgui.WindowFlags_.menu_bar.value
		style: imgui.Style = imgui.get_style()
		imgui.push_style_var(imgui.StyleVar_.window_padding.value, ImVec2(style.frame_padding.x + int(style.window_border_size), style.frame_padding.y))
		if internal.begin_viewport_side_bar("##MenuBar", imgui.get_main_viewport(), imgui.Dir_.up.value, 2 * (imgui.get_frame_height() + style.frame_padding.y), flags):
			if imgui.begin_menu_bar():
				if imgui.begin_menu("File"):
					imgui.menu_item("Open folder", "", False)
					if imgui.menu_item("Quit", "Alt+F4", False)[0]:
						self.quit()
					imgui.end_menu()
				if imgui.begin_menu("Edit"):
					imgui.menu_item("Export", "Ctrl+E", False, False)
					imgui.menu_item("Export contents", "Ctrl+Shift+E", False, False)
					imgui.menu_item("Export JSON", "", False, False)
					imgui.separator()
					imgui.menu_item("Copy", "Ctrl+C", False, False)
					imgui.menu_item("Copy path", "Ctrl+Alt+C", False, False)
					imgui.separator()
					imgui.menu_item("Select all", "Ctrl+A", False)
					imgui.end_menu()
				if imgui.begin_menu("View"):
					imgui.end_menu()
				if imgui.begin_menu("Tools"):
					imgui.menu_item("Hash Lookup", "", False)
					imgui.menu_item("Archive search", "Ctrl+Shift+F", False)
					if imgui.begin_menu("Debug"):
						self.show_demo_window = imgui.menu_item("Demo Window", "", self.show_demo_window)[1]
						self.show_style_editor = imgui.menu_item("Style editor", "", self.show_style_editor)[1]
						imgui.end_menu()
					imgui.end_menu()
				imgui.end_menu_bar()
		imgui.pop_style_var()
		imgui.end()

		
		if self.show_demo_window:
			toggle = imgui.show_demo_window(self.show_demo_window)
			self.show_demo_window = toggle if toggle != None else self.show_demo_window
		if self.show_style_editor:
			imgui.show_style_editor()

	def render_status_bar(self):
		flags: imgui.WindowFlags = imgui.WindowFlags_.no_scrollbar.value | imgui.WindowFlags_.menu_bar.value
		if internal.begin_viewport_side_bar("##StatusBar", imgui.get_main_viewport(), imgui.Dir_.down.value, imgui.get_frame_height(), flags):
			if imgui.begin_menu_bar():
				imgui.text("LA Noire!")
				imgui.end_menu_bar()
		imgui.end()

	def render_tool_bar(self):
		style: imgui.Style = imgui.get_style()
		if internal.begin_viewport_side_bar("##MenuBar", imgui.get_main_viewport(), imgui.Dir_.up.value, 0, imgui.WindowFlags_.none.value):
			imgui.push_style_var(imgui.StyleVar_.item_spacing.value, ImVec2(style.frame_padding.y, style.item_spacing.y))

			imgui.arrow_button("##BackButton", imgui.Dir_.left.value)
			imgui.same_line()
			imgui.arrow_button("##ForwardButton", imgui.Dir_.right.value)
			imgui.same_line()
			imgui.arrow_button("##UpButton", imgui.Dir_.up.value)

			imgui.same_line()
			imgui.push_item_width(-(2 * imgui.get_frame_height() + 4 * style.item_spacing.x + 1 + max(imgui.get_window_width() * 0.2, 200)))
			imgui.input_text("###Path", "X:\\SteamLibrary\\steamapps\\common\\L.A.Noire\\final\\pc", imgui.InputTextFlags_.auto_select_all.value)
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

	def render_list_view(self):
		flags: imgui.WindowFlags =  imgui.WindowFlags_.no_collapse.value | imgui.WindowFlags_.no_move.value

		# imgui.push_style_var(imgui.StyleVar_.window_padding.value, ImVec2(0, 0))
		# imgui.push_style_var(imgui.StyleVar_.window_border_size.value, 0)
		# imgui.push_style_var(imgui.StyleVar_.frame_border_size.value, 0)
		if not imgui.begin("List View", None, flags)[0]:
			# imgui.pop_style_var(3)
			imgui.end()
			return
		# imgui.pop_style_var()

		table_flags: imgui.TableFlags = imgui.TableFlags_.resizable.value + imgui.TableFlags_.reorderable.value | imgui.TableFlags_.sortable.value | imgui.TableFlags_.borders_outer.value | imgui.TableFlags_.borders_inner_v.value | imgui.TableFlags_.scroll_y.value
		if imgui.begin_table("##FileTable", 4, table_flags, ImVec2(0, 0)):
			column_flags: imgui.TableColumnFlags = imgui.TableColumnFlags_.width_fixed.value
			imgui.table_setup_column("Name", column_flags, 400)
			imgui.table_setup_column("Type", column_flags, 160)
			imgui.table_setup_column("Size", column_flags, 100)
			imgui.table_setup_column("Attributes", column_flags, 160)
			
			imgui.table_setup_scroll_freeze(1, 1)
			imgui.table_headers_row()

			for i in range(100):
				imgui.table_next_row()

				if imgui.table_set_column_index(0):
					imgui.image(self.icons.get("folder", 0) if i % 2 == 0 else self.icons.get("archive", 0), ImVec2(imgui.get_text_line_height(), imgui.get_text_line_height()))
					imgui.same_line()
					(hit, select) = imgui.selectable(f"Asset-{i}", False, imgui.SelectableFlags_.allow_double_click.value | imgui.SelectableFlags_.span_all_columns.value)
					if hit:
						print(f"Hit: {i} {select}")

					imgui.table_next_column()
					imgui.text("Folder" if i % 2 == 0 else "Archive")

					imgui.table_next_column()
					imgui.text("3.142 5GB")

					imgui.table_next_column()
					imgui.text("BIG Archive")


			imgui.end_table()

		# imgui.pop_style_var(2)
		imgui.end()

	def render_tree_view(self):
		flags: imgui.WindowFlags =  imgui.WindowFlags_.no_collapse.value | imgui.WindowFlags_.no_move.value
		if not imgui.begin("Tree View", None, flags)[0]:
			imgui.end()
			return

		imgui.text("Tree view!")

		imgui.end()

	def render_info_view(self):
		flags: imgui.WindowFlags =  imgui.WindowFlags_.no_collapse.value | imgui.WindowFlags_.no_move.value
		if not imgui.begin("File Info", None, flags)[0]:
			imgui.end()
			return

		imgui.text("File Info!")

		imgui.end()

	def build_dockspace(self, first_time: bool):
		viewport: imgui.Viewport = imgui.get_main_viewport()

		dockspace_id: imgui.ID = imgui.dock_space_over_viewport(viewport, imgui.DockNodeFlags_.passthru_central_node.value)

		if first_time:
			docknode_flags: imgui.DockNodeFlags = imgui.DockNodeFlags_.no_undocking.value
			internal.dock_builder_set_node_size(dockspace_id, viewport.size)

			(_, left, center) = internal.dock_builder_split_node_py(dockspace_id, imgui.Dir_.left.value, 0.2)
			(_, right, center) = internal.dock_builder_split_node_py(center, imgui.Dir_.right.value, 0.3)

			internal.dock_builder_get_node(dockspace_id).local_flags |= docknode_flags | imgui.DockNodeFlags_.passthru_central_node.value
			internal.dock_builder_get_node(left).local_flags |= docknode_flags
			internal.dock_builder_get_node(center).local_flags |= docknode_flags
			internal.dock_builder_get_node(right).local_flags |= docknode_flags

			internal.dock_builder_dock_window("Tree View", left)
			internal.dock_builder_dock_window("List View", center)
			internal.dock_builder_dock_window("File Info", right)
			internal.dock_builder_finish(dockspace_id)
