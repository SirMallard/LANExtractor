from pathlib import Path
from imgui_bundle import ImVec2, imgui
from imgui_bundle.python_backends.glfw_backend import GlfwRenderer
from numpy import array
from threading import Thread

from gui.app_data import AppData
from gui.windows.file_info import render_info_view
from gui.windows.hash import render_hash_window
from gui.windows.list_view import render_list_view
from gui.windows.tool_bar import render_tool_bar
from gui.windows.tree_view import render_tree_view

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

	app_data: AppData

	show_demo_window: bool = False
	show_style_editor: bool = False
	show_hash_window: bool = False

	icons: dict[str, int]

	def __init__(self) -> None:
		self.app_data = AppData(Path("X:\\SteamLibrary\\steamapps\\common\\L.A.Noire"))
		self.icons = {}

	def init_on_window(self) -> None:
		# self.app_data.generate_node()
		return

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
				thread: Thread = Thread(target=self.init_on_window)
				thread.start()
				first_time = False

		impl.shutdown()
		glfw.terminate()
	
	def quit(self) -> None:
		sys.exit(0)

	def render(self, first_time: bool):
		self.build_dockspace(first_time)

		self.render_menu_bar()
		self.render_status_bar()
		render_tool_bar(self.app_data)

		render_list_view(self.app_data)
		render_tree_view(self.app_data)
		render_info_view(self.app_data)

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
					self.show_hash_window = imgui.menu_item("Hash", "", self.show_hash_window)[1]
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

		if self.show_hash_window:
			self.show_hash_window = render_hash_window(self.app_data, self.show_hash_window)

	def render_status_bar(self):
		flags: imgui.WindowFlags = imgui.WindowFlags_.no_scrollbar.value | imgui.WindowFlags_.menu_bar.value
		if internal.begin_viewport_side_bar("##StatusBar", imgui.get_main_viewport(), imgui.Dir_.down.value, imgui.get_frame_height(), flags):
			if imgui.begin_menu_bar():
				imgui.text(self.app_data.status_text["file_scan"])
				imgui.text(self.app_data.status_text["archive_scan"])
				imgui.text(self.app_data.status_text["folders"])
				imgui.text(self.app_data.status_text["files"])
				imgui.end_menu_bar()
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
