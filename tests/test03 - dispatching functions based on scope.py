import sublime, sublime_plugin

def control(self):
	return "Finding matching brace."

def npr():
	return "Showing NPR documentation."

def ele():
	return "Showing ELE documentation."

def macro():
	return "Finding macro definition / call."

def program():
	return "Pulling up that program's code."

def local():
	return "Showing local doc and/or finding assignments."



def show_output(edit, msg):
	win = sublime.active_window()
	if win:
		panel = win.get_output_panel("Test")
		panel.set_read_only(False)
		panel.insert(edit, panel.size(), msg)
		panel.set_read_only(True)
		win.run_command("show_panel",
			{"panel": "output.Test"})



#class Test3Command(sublime_plugin.TextCommand):

	def run(self, edit):
		selection = self.view.sel()[0]
		start = selection.begin()
		scope = self.view.scope_name(start)

		functions = {
			"source.npr keyword.control.if " : control,
			"source.npr keyword.control.do " : control,
			"source.npr keyword.control.brace " : control,
			"source.npr support.function.npr.macro " : npr,
			"source.npr storage.temp.data.def " : ele,
			"source.npr support.constant.data.def " : ele,
			"source.npr entity.name.function.macro.call " : macro,
			"source.npr entity.name.section.macro.title " : macro,
			"source.npr entity.function.program.call " : program,
			"source.npr variable.other.local " : local,
			"source.npr storage.slash.value " : local,
		}

		if scope in functions:
			msg = functions[scope](self)
			show_output(edit, msg)