from magicsubl import ms
import sublime
import sublime_plugin

class Test8Command(sublime_plugin.TextCommand):
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

		docRegion = self.findDoc(localName)
		'''maybe rewrite findDoc to return lines and doc content'''

		if docRegion is not None:
			docContent = self.view.substr(docRegion)
			docTitle = self.findDocTitle(docRegion)
			msg = docTitle + '\n;//\n' + docContent + '\n'
			syntax = self.view.settings().get('syntax')
			ms.show_output(msg, syntax)
		else:
			sublime.status_message('%s has no documentation' % localName)


	def findDoc(self, localName):
		i = 0
		while i < self.view.size():
			search = self.view.find(' ' + localName + ' *(-|=)', i)
			if search is None:
				docNameRegion = None
				break
			else:
				docNameRegion = sublime.Region(search.begin() + 1, search.begin() + 1 + len(localName))
				i = docNameRegion.end()
				if self.scope(docNameRegion.begin()) == 'comment.line.semicolon':
					break

		if docNameRegion is not None:
			docRegion = self.view.line(docNameRegion)
			return docRegion
			'''still need to find additional doc lines if they exist'''
		else:
			return None


	def findDocTitle(self, docRegion):
		i = docRegion.begin()
		docTitle = None
		while i > 0:
			row, col = self.view.rowcol(i)
			row = row-1
			col = 0
			i = self.view.text_point(row, col)
			line = self.view.substr(self.view.line(i))
			if line.find(':Doc') is not -1:
				docTitle = line
				break

		if docTitle is None:
			docTitle = ''';//:Doc Automatically generate title'''

		return docTitle


	def scope(self, cursorPosition):
		return self.view.scope_name(cursorPosition).split(' ')[1]