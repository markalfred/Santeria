from magicsubl import ms
import sublime
import sublime_plugin


class Test10Command(sublime_plugin.TextCommand):
	def run(self, edit):
		cursorPosition = self.view.sel()[0].begin()
		scope = self.scope(cursorPosition)

		if scope == 'variable.other.local':
			self.functionLocal(cursorPosition)
		else:
			print('Incorrect scope.')

	def scope(self, cursorPosition):
		return self.view.scope_name(cursorPosition).split(' ')[1]


	def functionLocal(self, cursorPosition):
		v = self.view
		local = v.substr(v.word(cursorPosition))
		doc = self.findDoc(local)

		if doc is not None:
			syntax = v.settings().get('syntax')
			ms.show_output(doc, syntax)
		else:
			sublime.status_message('%s has no documentation' % local)

	def findDoc(self, local):
		v = self.view
		i = 0

		# Find the first instance of this variable that is in a comment
		while i < v.size():
			search = v.find(' ' + local + ' *(-|=)', i)
			if search is None:
				docFound = None
				break
			else:
				docFound = sublime.Region(search.begin() + 1, search.begin() + 1 + len(local))
				i = docFound.end()
				if self.scope(docFound.begin()) == 'comment.line.semicolon':
					break

		# If this variable exists in a comment, docFound contains its region
		if docFound is not None:
			doc = self.docSection(docFound, local) + self.docContent(docFound, local)
			return doc
		else:
			return None


	# Find the section header (ie. :Doc Arguments), or generate one if this doesn't exist
	def docSection(self, docFound, local):
		v = self.view
		pos = docFound.begin()
		docSection = None

		while pos > 0:
			row, col = v.rowcol(pos)
			row -= 1
			col = 0
			pos = v.text_point(row, col)
			line = v.substr(v.full_line(pos))
			if line.find(':Doc') is not -1:
				docSection = line
				break
		if docSection is None:
			docSection = ';//:Doc ' + self.looksLike(local) + '\n'
		return docSection

	def looksLike(self, local):
		if len(local) == 1:
			return 'Arguments'
		else:
			return 'Local Variables'

	def docContent(self, docFound, local):
		v = self.view
		pos = docFound.begin()
		row, col = v.rowcol(pos)
		indent = col
		docContent = ';//' + (' ' * 5) + v.substr(v.full_line(docFound))[indent:]
		while True:
			row += 1
			col = indent
			pos = v.text_point(row, col)
			while v.substr(pos)==' ':
				col += 1
				pos = v.text_point(row, col)

			if col>indent:
				docContent = docContent + ';//' + (' ' * 5) + v.substr(v.full_line(pos))[indent:]
			else:
				break
		return docContent