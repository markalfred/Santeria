import sublime, sublime_plugin

class Test2Command(sublime_plugin.TextCommand):

	def run(self, edit):
		self.view.run_command("expand_selection",
			{"to": "scope"})
		region = self.view.sel()[0]
		start = region.begin()
		msg = self.view.scope_name(start)
		self.show_output(edit, msg)


	def show_output(self, edit, msg):
		win = sublime.active_window()
		if win:
			panel = win.get_output_panel("Test")
			panel.set_read_only(False)
			panel.insert(edit, panel.size(), msg)
			panel.set_read_only(True)
			win.run_command("show_panel",
				{"panel": "output.Test"})