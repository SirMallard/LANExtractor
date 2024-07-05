from imgui_bundle import imgui
from imgui_bundle.python_backends.glfw_backend import GlfwRenderer

from gui.file_info import FileInfo
internal = imgui.internal
import OpenGL.GL as gl
import glfw
import sys
from PIL import Image

from gui.file_explorer import FileExplorer


WINDOW_WIDTH: int = 1280
WINDOW_HEIGHT: int = 720
WINDOW_NAME: str = "L.A. Noire Extractor"

class Gui():
	window: glfw._GLFWwindow # type: ignore
	file_explorer: FileExplorer
	file_info: FileInfo

	def __init__(self) -> None:
		self.file_explorer = FileExplorer()
		self.file_info = FileInfo()
	
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

		io: imgui.IO = imgui.get_io()
		io.config_flags |= imgui.ConfigFlags_.docking_enable.value
		io.config_flags |= imgui.ConfigFlags_.nav_enable_keyboard.value

		imgui.style_colors_dark()
		
		# We need to initialize the OpenGL backend (so that we can later call opengl3_new_frame)
		# imgui.backends.glfw_init_for_opengl(window.)
		imgui.backends.opengl3_init("#version 150")
		imgui.backends.opengl3_new_frame()
		
		io.set_ini_filename("")
		impl = GlfwRenderer(self.window)

		first_time: bool = True
		while not glfw.window_should_close(self.window):
			glfw.poll_events()
			impl.process_inputs()

			# imgui.backends.glfw_new_frame()
			imgui.new_frame()

			self.run_window(first_time)

			gl.glClearColor(0.0, 0.0, 0.0, 1)
			gl.glClear(gl.GL_COLOR_BUFFER_BIT)

			imgui.render()
			impl.render(imgui.get_draw_data())
			glfw.swap_buffers(self.window)

			if first_time:
				first_time = False

		impl.shutdown()
		glfw.terminate()
	
	def run_window(self, first_time: bool):
		self.dock_builder(first_time)

		window_flags: imgui.WindowFlags = imgui.WindowFlags_.always_vertical_scrollbar.value | imgui.WindowFlags_.no_collapse.value | imgui.WindowFlags_.no_move.value

		imgui.begin("Tree Explorer", None, window_flags);
		imgui.text("Tree Explorer");
		imgui.end();

		self.file_info.render(window_flags)
		
		imgui.begin("Status Bar", None, window_flags)
		imgui.text("Status Bar")
		imgui.end()

		self.file_explorer.render(window_flags)

	def dock_builder(self, first_time: bool):
		viewport: imgui.Viewport = imgui.get_main_viewport()

		dockspace_id: imgui.ID = imgui.dock_space_over_viewport(viewport, imgui.DockNodeFlags_.passthru_central_node.value)

		if first_time:
			docknode_flags: imgui.DockNodeFlags = imgui.DockNodeFlags_.no_undocking.value | imgui.DockNodeFlags_.auto_hide_tab_bar.value | imgui.DockNodeFlags_.no_resize.value
			internal.dock_builder_remove_node(dockspace_id)
			internal.dock_builder_add_node(dockspace_id, docknode_flags)
			internal.dock_builder_set_node_size(dockspace_id, viewport.size)

			(_, bottom, top) = internal.dock_builder_split_node_py(dockspace_id, imgui.Dir_.down.value, 0.2)
			(_, left, center) = internal.dock_builder_split_node_py(top, imgui.Dir_.left.value, 0.2)
			(_, right, center) = internal.dock_builder_split_node_py(center, imgui.Dir_.right.value, 0.3)

			internal.dock_builder_get_node(bottom).local_flags |= docknode_flags
			internal.dock_builder_get_node(left).local_flags |= docknode_flags
			internal.dock_builder_get_node(right).local_flags |= docknode_flags

			internal.dock_builder_dock_window("Status Bar", bottom)
			internal.dock_builder_dock_window("Tree Explorer", left)
			internal.dock_builder_dock_window("File Info", right)
			internal.dock_builder_dock_window("File View", center)
			internal.dock_builder_finish(dockspace_id)
