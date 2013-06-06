from magicsubl import ms
import sublime
import sublime_plugin

class Test5Command(sublime_plugin.TextCommand):
	def run(self, edit):
		sel = self.view.sel()[0]
		selBegin = sel.begin()
		scopeName, scope = self.view.scope_name(selBegin).rstrip().split(' ')

		if scope == 'entity.name.section.macro.title':
			# Include @ and a non-period char in search, but don't highlight either.
			macroTitle = self.view.substr(self.view.line(selBegin)).lstrip('#')
			macroFound = self.view.find('@' + macroTitle + '[^.]', 0)
			macroRegion = sublime.Region(macroFound.begin()+1, macroFound.end()-1)

			self.view.sel().clear()
			self.view.sel().add(macroRegion)
			self.view.show(macroRegion)

		print macroTitle