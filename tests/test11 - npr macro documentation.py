from magicsubl import ms
import sublime
import sublime_plugin
import xml.etree.ElementTree as ET


class Test11Command(sublime_plugin.TextCommand):
	def run(self, edit):
		v = self.view
		cursorPosition = v.sel()[0].begin()
		scope = ms.scope(self, cursorPosition)

		if scope == 'support.function.npr.macro':
			self.functionNpr(cursorPosition)
		else:
			print('Incorrect scope.')

	def functionNpr(self, cursorPosition):
		v = self.view
		selectedMacro = v.substr(v.word(cursorPosition))
		print sublime.packages_path()
		filepath = sublime.packages_path() + '\\MagicSublime\\lib\\npr_macros.xml'
		macro = self.findMacroInXML(filepath, selectedMacro)

		if macro is None:
			print('@%s could not be found.' % selectedMacro)
		else:
			print('Found @%s!!!' % selectedMacro)
			msg = self.generateDoc(macro)
			syntax = v.settings().get('syntax')
			print syntax
			ms.show_output(msg, 'Packages/Text/Plain text.tmLanguage')
			# print msg

	def findMacroInXML(self, filepath, selectedMacro):
		tree = ET.parse(filepath)
		root = tree.getroot()
		for macro in root:
			try:
				name = macro.find('name').text
				active = macro.find('act').text
				if name == selectedMacro:
					if active != "Y":
						print('%s is inactive!' % name)
						return None
					else:
						return macro
			except (NameError, AttributeError):
				print('Error: Missing flags in XML file.')

	def generateDoc(self, macro):
		msg = ""
		name = macro.find('name')
		syntax = macro.find('stx')
		description = macro.find('dsc')
		code = macro.find('code')
		comment = macro.find('cmt')

		if name is not None:
			name = name.text
		if name is not None:
			pad = 10 - len(name)
			if pad < 0:
				pad = 0
			msg = msg + (' '*pad) + '@' + name + ': \n\n'
		if syntax is not None:
			syntax = syntax.text
		if syntax is not None:
			msg = msg + "     Syntax:   " + syntax + '\n'
		if description is not None:
			description = description.text
		if description is not None:
			msg = msg + "Description:   " + description + '\n'
		if code is not None:
			code = code.text
		if code is not None:
			msg = msg + "       Code:   " + code + '\n'
		if comment is not None:
			comment = comment.text.rstrip()
		if comment is not None:
			msg = msg + '\n;' + (' -' * 30) + '\n\n' + comment

		return msg.rstrip()