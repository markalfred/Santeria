from magicsubl import ms
import sublime
import sublime_plugin

class Test7Command(sublime_plugin.TextCommand):
	def run(self, edit):
		cursorPosition = self.view.sel()[0].begin()
		scope = self.scope(cursorPosition)

		if scope == 'variable.other.local':
			self.functionLocal(cursorPosition)
		else:
			print('Incorrect scope.')


	def functionLocal(self, cursorPosition):
		sourceRegion = self.view.word(cursorPosition)
		localName = self.view.substr(sourceRegion)

		i = 0
		while i < self.view.size():
			targetRegion = self.view.find(' ' + localName + ' (-|=)', i)
			if targetRegion is None:
				i = self.view.size()
			else:
				i = targetRegion.end()
				if self.scope(targetRegion.begin()) == 'comment.line.semicolon':
					break

		if targetRegion is None:
			sublime.status_message('%s has no documentation' % localName)
		else:
			# self.view.sel().clear()
			# self.view.sel().add(targetRegion)
			# self.view.show(targetRegion)

			msg = self.view.substr(self.view.line(targetRegion))
			syntax = self.view.settings().get('syntax')
			ms.show_output(msg, syntax)


	def scope(self, cursorPosition):
		return self.view.scope_name(cursorPosition).split(' ')[1]