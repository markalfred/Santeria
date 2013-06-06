from magicsubl import ms
import sublime
import sublime_plugin

lastMacro = ""

def control(self, scope, args):
	if args == "expand":
		self.view.run_command("expand_selection", {"to": "scope"})

	self.view.run_command("move_to", {"to": "brackets"})
	return "Finding matching brace."


def macro(self, scope, args):
	if args == lastMacro and lastMacro != "":
		return "Going back to" + args + "."
	elif args != "none":
		return "Finding all calls"
	else:
		return "Finding macro definition"


def local(self, scope, args):
	return "Showing local doc and/or finding assignments."

def npr(self, scope, args):
	return "Showing NPR documentation."

def ele(self, scope, args):
	return "Showing ELE documentation."

def program(self, scope, args):
	return "Pulling up that program's code."



class Test4Command(sublime_plugin.TextCommand):

	def run(self, edit):

		functions = {
			"source.npr keyword.control.if " : control,
			"source.npr keyword.control.do " : control,
			"source.npr keyword.control.brace " : control,
			"source.npr entity.name.function.macro.call " : macro,
			"source.npr entity.name.section.macro.title " : macro,
			"source.npr variable.other.local " : local,
			"source.npr storage.slash.value " : local,
			"source.npr support.function.npr.macro " : npr,
			"source.npr storage.temp.data.def " : ele,
			"source.npr support.constant.data.def " : ele,
			"source.npr variable.other.local.data.def ": ele,
			"source.npr entity.function.program.call " : program,
		}

		arguments = {
			"source.npr keyword.control.if " : "expand",
			"source.npr keyword.control.do " : "expand",
			"source.npr keyword.control.brace " : "none",
			"source.npr entity.name.function.macro.call " : "none",
			"source.npr entity.name.section.macro.title " : lastMacro,
			"source.npr variable.other.local " : "none",
			"source.npr storage.slash.value " : "none",
			"source.npr support.function.npr.macro " : "none",
			"source.npr storage.temp.data.def " : "none",
			"source.npr support.constant.data.def " : "none",
			"source.npr entity.function.program.call " : "none",

		}

		selection = self.view.sel()[0]
		start = selection.begin()

		# Look at the entity just prior to, and just after the cursor.
		priorScope = self.view.scope_name(start-1)
		afterScope = self.view.scope_name(start)

		scope = ""

		if priorScope in functions:
			scope = priorScope
		elif afterScope in functions:
			scope = afterScope

		if scope:
			msg = functions[scope](self, scope, arguments[scope])
			ms.show_output(edit, "scope: " + scope + "\npriorScope: " + priorScope + "\nafterScope: " + afterScope + "\n\n" + msg)