from magicsubl import ms
import xml.etree.ElementTree as ET
import sublime
import sublime_plugin

class MagicDocCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        # Initialization
        global V
        V = self.view    # The current view, used a ton.
        settings = sublime.load_settings("MagicSublime.sublime-settings")
        cursorPosition = V.sel()[0].begin()
        scope = ms.scope(self, cursorPosition)

        functions = {
            'variable.other.local': self.functionLocal,
            'entity.name.section.macro.title': self.functionMacroTitle,
            'entity.name.function.macro.call': self.functionMacroCall,
            'support.function.npr.macro': self.functionNpr,
            # "source.npr keyword.control.if " : control,
            # "source.npr keyword.control.do " : control,
            # "source.npr keyword.control.brace " : control,
            # "source.npr storage.temp.data.def " : ele,
            # "source.npr support.constant.data.def " : ele,
            # "source.npr entity.function.program.call " : program,
            # "source.npr storage.slash.value " : local,
        }
        if scope in functions:
            functions[scope](cursorPosition, settings)
        else:
            sublime.status_message('"%s" function not yet written.' % scope)

        # Cleanup
        if scope != 'entity.name.function.macro.call':
            settings.erase('last_macro')
        sublime.save_settings("MagicSublime.sublime-settings")



    ########################################################
    #################### Local Variable ####################
    ########################################################

    def functionLocal(self, cursorPosition, settings):
        # v = self.view
        local = V.substr(V.word(cursorPosition))
        doc = self.findDoc(local)

        if doc is not None:
            syntax = V.settings().get('syntax')
            ms.show_output(doc, syntax)
        else:
            sublime.status_message('%s has no documentation' % local)

    def findDoc(self, local):
        # v = self.view
        i = 0

        # Find the first instance of this variable that is in a comment
        while i < V.size():
            search = V.find(' ' + local + ' *(-|=)', i)
            if search is None:
                docFound = None
                break
            else:
                docFound = sublime.Region(search.begin() + 1,
                                          search.begin() + 1 + len(local))
                i = docFound.end()
                if ms.scope(self, docFound.begin()) == 'comment.line.semicolon':
                    break

        # If this variable exists in a comment, docFound contains its region
        if docFound is not None:
            doc = (self.docSection(docFound, local) +
                   self.docContent(docFound, local))
            return doc
        else:
            return None

    # Find the section header (ie. :Doc Arguments),
    # or generate one if this doesn't exist
    def docSection(self, docFound, local):
        # v = self.view
        pos = docFound.begin()
        docSection = None

        while pos > 0:
            row, col = V.rowcol(pos)
            row -= 1
            col = 0
            pos = V.text_point(row, col)
            line = V.substr(V.full_line(pos))
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
        # v = self.view
        pos = docFound.begin()
        row, col = V.rowcol(pos)
        indent = col
        docContent = (';//' + (' ' * 5) +
                      V.substr(V.full_line(docFound))[indent:])
        while True:
            row += 1
            col = indent
            pos = V.text_point(row, col)
            while V.substr(pos) == ' ':  # or == local
                col += 1
                pos = V.text_point(row, col)

            if col > indent:
                docContent = (docContent + ';//' + (' ' * 5) +
                              V.substr(V.full_line(pos))[indent:])
            else:
                break
        return docContent.rstrip()



    ############################################################
    ######################## Macro Title #######################
    ############################################################

    def functionMacroTitle(self, cursorPosition, settings):
        # v = self.view
        macroRegion = -1
        lastMacro = settings.get('last_macro', -1)

        macroTitle = V.substr(V.line(cursorPosition)).lstrip('#')

        if lastMacro != -1:
            # If lastMacro has a value, we might be jumping back to the call
            # from which we came.
            jumpRegion = sublime.Region(lastMacro, lastMacro + len(macroTitle))
            if V.substr(jumpRegion) == macroTitle:
                macroRegion = jumpRegion

        if macroRegion == -1:
            # If we're not jumping back to a call, find the first macro call in
            # the file instead. Include @ and a non-period char in search,
            # but don't highlight either.
            macroFound = V.find('@' + macroTitle + '[^.]', 0)
            if macroFound == None:
                sublime.status_message("@" + macroTitle + " not found")
            else:
                macroRegion = sublime.Region(macroFound.begin() + 1,
                                             macroFound.end() - 1)

        if macroRegion != -1:
            V.sel().clear()
            V.sel().add(macroRegion)
            V.show(macroRegion)



    ############################################################
    ######################## Macro Call ########################
    ############################################################


        # v = self.view
        V.run_command('expand_selection', {'to': 'word'})
        settings.set('last_macro', int(V.sel()[0].begin()))

        macroTitle = V.substr(V.sel()[0]).lstrip('@')
        macroFound = V.find('\n#?' + macroTitle + '\n', 0)
        macroRegion = sublime.Region(macroFound.begin() + 1,
                                     macroFound.end() - 1)

        V.sel().clear()
        V.sel().add(macroRegion)
        V.show(macroRegion)



    ############################################################
    ######################## NPR  Macro ########################
    ############################################################

    def functionNpr(self, cursorPosition, settings):
        # v = self.view
        selectedMacro = V.substr(V.word(cursorPosition))
        print sublime.packages_path()
        filepath = (sublime.packages_path() +
                    '/MagicSublime/lib/npr_macros.xml')
        macro = self.findMacroInXML(filepath, selectedMacro)

        if macro is None:
            sublime.status_message('Documentation for @%s not found.'
                                   % selectedMacro)
        else:
            msg = self.generateDoc(macro)
            ms.show_output(msg, 'Packages/Text/Plain text.tmLanguage')

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
                print('Warning: Possibly corrupt XML file.')

    def generateDoc(self, macro):
        msg = ""
        name = macro.find('name')
        syntax = macro.find('stx')
        description = macro.find('dsc')
        code = macro.find('code')
        comment = macro.find('cmt')

        # Don't need to show the name -- syntax is better.
        # If syntax tag doesn't exist, its usage is: @.sd, @.device, etc.
        if syntax is not None:
            syntax = syntax.text
        if syntax is not None:
            msg = msg + "     Syntax:   " + syntax + '\n'
        else:
            if name is not None:
                name = name.text
            if name is not None:
                msg = msg + "     Syntax:   " + '@' + name + '\n'

        if description is not None:
            description = description.text
        if description is not None:
            msg = msg + "Description:   " + description + '\n'
        if code is not None:
            code = code.text
        if code is not None:
            msg = msg + "       Code:   " + code + '\n'
        if comment is not None:
            comment = comment.text
        if comment is not None:
            comment = comment.rstrip()
        if comment is not None:
            msg = msg + '\n' + "Notes:\n" + comment

        return msg.rstrip()
