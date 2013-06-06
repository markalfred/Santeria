from magicsubl import ms
import sublime
import sublime_plugin
import time

class Test6Command(sublime_plugin.TextCommand):
	def run(self, edit):
		settings = sublime.load_settings("MagicSublime.sublime-settings")

		# Grab first selection
		sel = self.view.sel()[0]
		selBegin = sel.begin()
		# Grab scope of entity at the beginning of the selection
		scopeData = self.view.scope_name(selBegin).split(' ')
		scopeName = scopeData[0]
		scope = scopeData[1]

		if scopeName != 'source.npr':
			sublime.status_message("Syntax is not NPR.")

		elif scope == 'entity.name.section.macro.title':
			macroRegion = -1
			lastMacro = settings.get('last_macro', -1)

			macroTitle = self.view.substr(self.view.line(selBegin)).lstrip('#')

			if lastMacro != -1:
				# If lastMacro has a value, we might be jumping back to the call from which we came.
				jumpRegion = sublime.Region(lastMacro, lastMacro + len(macroTitle))
				if self.view.substr(jumpRegion) == macroTitle:
					macroRegion = jumpRegion

			if macroRegion == -1:
				# If we're not jumping back to a call, find the first macro call in the file instead.
				# Include @ and a non-period char in search, but don't highlight either.
				macroFound = self.view.find('@' + macroTitle + '[^.]', 0)
				if macroFound == None:
					sublime.status_message("@" + macroTitle + " not found")
				else:
					macroRegion = sublime.Region(macroFound.begin()+1, macroFound.end()-1)

			if macroRegion != -1:
				self.view.sel().clear()
				self.view.sel().add(macroRegion)
				self.view.show(macroRegion)

		elif scope == 'entity.name.function.macro.call':
			self.view.run_command('expand_selection', {'to': 'word'})
			settings.set('last_macro', int(self.view.sel()[0].begin()))

			macroTitle = self.view.substr(self.view.sel()[0]).lstrip('@')
			macroFound = self.view.find('\n#?' + macroTitle + '\n', 0)
			macroRegion = sublime.Region(macroFound.begin()+1, macroFound.end()-1)

			self.view.sel().clear()
			self.view.sel().add(macroRegion)
			self.view.show(macroRegion)

		if scope != 'entity.name.function.macro.call':
			settings.erase('last_macro')

		sublime.save_settings("MagicSublime.sublime-settings")