from magicsubl import ms as MS
import xml.etree.ElementTree as ET
import sublime
import sublime_plugin

# MagicSublime  by Mark Battersby

# Sublime Text API can be found at:
#  http://www.sublimetext.com/docs/2/api_reference.html

# Frequently used and global variables:
#   V = shorthand for self.view, a pointer to the currently active file
#   item = region containing the entity on which the user invoked Magic command
#   settings = a pointer to the MagicSublime settings file


# Global maps
scope = {
    'entity.name.section.macro.title': 'Macro Title',
    'entity.name.function.macro.call': 'Macro Call',
    'variable.other.local': 'Local Variable',
    'storage.temp.data.def': 'Data Definition',
    'support.constant.data.def': 'Data Definition',
    'support.function.npr.macro': 'NPR Macro',
    'entity.function.program.call': 'Procedure'
}

functions = {
    # 'Macro Title': macroTitle,
    # 'Macro Call': macroCall,
    # 'Local Variable': local,
    # 'Data Definition': dataDef,
    # 'NPR Macro': nprMacro,
    # 'Procedure': procedure
}


def macroTitle(cursor):
    """Jump to an equivalent macro call.

    When the user invokes the Magic command from a macro call, its position is saved in the settings file. If the user jumped to this macro title from that saved macro call, jump back to that call. If they didn't jump to this title from a call, jump to the first macro call in the procedure."""

    item = V.substr(V.word(cursor))    # The item on which Magic was invoked
    settings = sublime.load_settings('MagicSublime.sublime-settings')

    lastMacro = settings.get('last_macro', sublime.Region(-1))
    if item == V.substr(V.word(lastMacro)):
        jump = sublime.Region(lastMacro,
                              lastMacro + len(item))
    else:
        jump = V.find('@' + item + '[^.]', 0)
        # Find a macro call (@) with a non-period char following it
        if jump is None:
            sublime.status_message("@" + item + " not found")
        else:
            jump = V.find(item, jump.begin())

    if jump is not None:
        V.sel().clear()
        V.sel().add(jump)
        V.show_at_center(jump)


def macroCall(cursor):
    """Jump to the macro definition.

    When the user invokes the Magic command from a macro call, its position is saved in the settings file (see: macroTitle). This allows it to be quickly jumped-back-to once the macro has been reviewed. The macro definition is then found and its header highlighted."""

    item = V.substr(V.word(cursor))
    settings = sublime.load_settings('MagicSublime.sublime-settings')
    settings.set('last_macro', int(V.word(cursor).begin()))  # Note pos of call

    try:
        jump = V.find('\n#?' + item + '\n', 0)
        # Macro title will have \n and optional # before, and \n after
        jump = V.find(item, jump.begin())
        # But don't highlight any of those characters

        V.sel().clear()
        V.sel().add(jump)
        V.show_at_center(jump)
        sublime.save_settings('MagicSublime.sublime-settings')
        # If successful, save the macro call position
    except(AttributeError):
        sublime.status_message("@" + item + " not found")


def local(cursor):
    """Show top-of-procedure documentation associated with a local variable.

    If there is documentation for the variable in the procedure header, it will be displayed in the footer window frame."""
    pass


def dataDef(cursor):
    """Show the ELE documentation for a given data element or segment.

    The source of the documentation is the XML file in lib/Data Definitions/_app_/_dpm_.xml. This file is generated via the Z.zcus.export.data.to.xml procedure which can be found in the CUS2/IMPPROG56 directory.

    This documentation should be searchable, so that any element or segment in it can lead to more documentation."""
    pass


def nprMacro(cursor):
    """Show NPR Macro documentation.

    The source of the documentation is the XML file in lib/npr_macros.xml.
    Its format:
    <macrodb>
        <macro>
            <name></name>
            <etc.../>
        </macro>
    </macrodb>"""

    def findMacroInXML(root, item):
        """Search elements under _root_ for one with the name _item_."""
        for macro in root:
            try:
                name = macro.find('name').text
                if name == item:
                    return macro
            except(NameError, AttributeError):
                print('Warning: Unexpected values in XML file.')
        else:
            sublime.status_message("@" + item + " not found")
            return None

    def generateDoc(root):
        """Grab all elements under _root_ and make into pretty documentation."""
        msg = ""
        name = root.find('name').text
        syntax = root.find('stx').text
        description = root.find('dsc').text
        code = root.find('code').text
        comment = root.find('cmt').text

        if syntax is not None:
            msg =

    item = V.substr(V.word(cursor))
    filepath = (sublime.packages_path() +
                '/MagicSublime/lib/npr_macros.xml')
    macrodb = ET.parse(filepath).getroot()
    macro = findMacroInXML(macrodb, item)
    if macro is not None:
        doc = generateDoc(macro)
        MS.show_output(doc, 'Packages/Text/Plain text.tmLanguage')
    else:
        sublime.status_message("@" + item + " not found")
        return None


def procedure(cursor):
    """Open the selected procedure in a new tab / Show documentation for procedure

    Not sure which yet."""


class MagicCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        """Dispatch of the MagicSublime master hotkey.

        This takes the scope, according to the NPR syntax definition, and performs the action specified in the global maps above."""

        global V        # The current view, used by nearly all functions

        V = self.view
        cursor = V.sel()[0].begin()
        scope = MS.scope(self, cursor)

        if scope in functions:
            functions[scope](cursor)
        else:
            sublime.status_message('"%s" function not yet written.' % scope)
