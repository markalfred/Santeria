from magicsubl import ms as MS
import xml.etree.ElementTree as ET
import re
import sublime
import sublime_plugin

# MagicSublime  by Mark Battersby

# Sublime Text API can be found at:
#  http://www.sublimetext.com/docs/2/api_reference.html

# Frequently used and global variables:
#   V = shorthand for self.view, a pointer to the currently active file
#   item = region containing the entity on which the user invoked Magic command
#   settings = a pointer to the MagicSublime settings file


def findInXML(root, item):
    """Search elements under root for one with the name item."""
    for i in root:
        try:
            name = i.find('name').text
            if name == item:
                return i
        except(NameError, AttributeError):
            print('Warning: Unexpected values in XML file.')


def getDpm(item):
    """Pull the DPM from the item, or infer it from the file path.

    If the selected item doesn't include the DPM, the DPM is the same as
    that of the procedure. This can be pulled from the filepath,
    ie. '/EDM/PAT/depart/depart.npr' should return 'EDM.PAT'

    The only exception to this is the 'Z' DPM, which is the only one that
    doesn't have two parts (...I think)"""
    dpm = re.sub('[a-z]*', '', item).rstrip('.')
    if dpm == '':
        if sublime.platform() == 'windows':
            d = '\\'
        else:
            d = '/'
        f = str(V.file_name()).split(d)
        if f[len(f) - 3] == 'Z':
            dpm = 'Z'
        else:
            dpm = f[len(f) - 4] + '.' + f[len(f) - 3]
    return dpm


def macroTitle(cursor):
    """Jump to an equivalent macro call.

    When the user invokes the Magic command from a macro call, its position is
    saved in the settings file. If the user jumped to this macro title from
    that saved macro call, jump back to that call. If they didn't jump to this
    title from a call, jump to the first macro call in the procedure."""

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
            sublime.status_message("@%s not found" % item)
        else:
            jump = V.find(item, jump.begin())

    if jump is not None:
        V.sel().clear()
        V.sel().add(jump)
        V.show_at_center(jump)


def macroCall(cursor):
    """Jump to the macro definition.

    When the user invokes the Magic command from a macro call, its position is
    saved in the settings file (see: macroTitle). This allows it to be quickly
    jumped-back-to once the macro has been reviewed. The macro definition is
    then found and its header highlighted."""

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
        sublime.status_message("@%s not found" % item)


def local(cursor):
    """Show top-of-procedure documentation associated with a local variable.

    If there is documentation for the variable in the procedure header, it
    will be displayed in the footer window frame.

    This assumes that the variable has (1) a space before its name and (2) is
    followed by spaces and a hypen/equal. This appears to be true of all
    recent documentation, but if it isn't true, documentation will not be
    found."""

    def findDoc(item):
        """Locate the top-of-procedure documentation for item."""
        i = 0
        while i < V.size():
            location = V.find(' %s *(-|=)' % item, i)
            if location is None:
                break
            else:
                i = location.end()
                if V.substr(V.line(location).begin()) == ';':
                    location = V.find(item, location.begin())
                    return location

    def generateTitle(item, location):
        """Find or generate the variable's section header."""
        pos = location.begin()
        while pos > 0:
            row, col = V.rowcol(pos)
            row -= 1
            col = 0
            pos = V.text_point(row, col)
            line = V.substr(V.line(pos))
            if line.find(':Doc') is not -1:
                title = line
                break
        else:
            if len(item) == 1 and 'ABCDEFGHIJK'.find(item) != -1:
                title = ';//:Doc Arguments'
            else:
                title = ';//:Doc Local Variables'
        return title

    def generateContent(item, location):
        """Arrange and show all lines of documentation."""
        print item, location
        pos = location.begin()
        row, col = V.rowcol(pos)
        content = ""
        while pos < V.size():
            content += ';//     %s\n' % V.substr(V.line(pos))[col:]
            row += 1
            pos = V.text_point(row, col)
            if V.substr(pos) == ' ':
                pass
            elif V.substr(V.line(pos)).find(item) == col:
                pass
            else:
                return content

    item = V.substr(V.word(cursor))
    msg = ""
    location = findDoc(item)
    if location is not None:
        msg += generateTitle(item, location)
        msg += '\n'
        msg += generateContent(item, location)
        MS.show_output(msg)
    else:
        sublime.status_message('%s has no documentation.' % item)


def dataDef(cursor):
    """Show the ELE documentation for a given data element or segment.

    The source of the documentation is
    MagicSublime/lib/Data Definitions/[app]/[dpm].xml.
    This file is generated via the Z.zcus.export.data.to.xml procedure which
    can be found in the CUS2/IMPPROG56 directory.

    This documentation should be searchable, so that any element or segment
    in it can lead to more documentation."""

    def generateEleDoc(root):
        """Grab all elements under root and make into pretty documentation."""
        try:
            element = dpm + '.' + root.find('name').text
            local = root.find('local').text
            physical = root.find('physical').text
            segment = root.find('segment').text
            pointer = root.find('pointer').text
            dataType = root.find('type').text
            length = root.find('length').text
            attributes = root.find('attributes').text
            description = root.find('description').text
            documentation = root.find('documentation').text
        except(AttributeError):
            print('Warning: Missing values in XML file.')

        msg = "Element        %s\n" % element
        msg += "Local          %s\n" % local
        msg += "Physical       %s\n" % physical
        msg += '\n'
        msg += "Segment        %s\n" % segment
        msg += "Pointer        %s\n" % pointer
        msg += "Data Type      %s\n" % dataType
        msg += "Length         %s\n" % length
        msg += '\n'
        if attributes is not None:
            msg += "Attributes\n%s\n\n" % attributes
        if description is not None:
            msg += "Description\n%s\n\n" % description
        if documentation is not None:
            msg += "Technical Documentation\n%s" % documentation

        return msg.rstrip()

    def generateSegDoc(root):
        """Grab all elements under root and make into pretty documentation."""
        msg = segment = physical = children = elements = subscripts = ""

        try:
            segment = dpm + '.' + root.find('name').text
            physical = root.find('physical').text
            value = root.find('value').text

            for i in root.find('children').findall('child'):
                children += '\n  %s' % i.text
            for i in root.find('elements').findall('element'):
                elementName = str(i.find('name').text)
                elementLocal = str(i.find('local').text)
                elementPhysical = str(i.find('physical').text)
                elements += ('\n' +
                             elementName +
                             ' ' * (30 - len(elementName)) +
                             elementLocal +
                             ' ' * (10 - len(elementLocal)) +
                             elementPhysical)
            for i in root.find('subscripts').findall('subscript'):
                subscripts += '\n  %s' % i.text

        except(AttributeError):
            print('Warning: Missing values in XML file.')

        msg += "Segment        %s\n" % segment
        msg += "Physical       %s\n" % physical
        msg += "Children %s\n" % children
        msg += '\n'
        if elements != "":
            msg += "Element                       Local     Physical"
            msg += '\n'
            msg += str(elements)
        elif subscripts != "":
            msg += "Subscripts %s\n\n" % subscripts
            msg += "Value %s" % value

        return msg

    item = V.substr(V.word(cursor))
    if item[:2] == 't.' or item[:2] == 'c.' or item[:2] == 'p.':
        item = item[2:]
    dpm = getDpm(item)
    app = dpm.split('.')[0]
    item = item.lstrip(dpm)  # If the item contained the DPM, remove it.
    filepath = (sublime.packages_path() +
                '/MagicSublime/lib/Data Definitions/' +
                app + '/' + dpm + '.xml')
    try:
        segments = ET.parse(filepath).getroot()
    except(IOError):
        sublime.status_message('"%s" definitions not found!!' % dpm)
        raise

    # Try first to find a segment with the name item
    seg = findInXML(segments, item)
    if seg is not None:
        msg = generateSegDoc(seg)
        MS.show_output(msg)
    else:
        for s in segments:
            elements = s.find('elements')
            ele = findInXML(elements, item)
            if ele is not None:
                msg = generateEleDoc(ele)
                MS.show_output(msg)
                break
        else:
            sublime.status_message("%s not found" % item)


def nprMacro(cursor):
    """Show NPR Macro documentation.

    The source of the documentation is MagicSublime/lib/npr_macros.xml.

    Its format:
    <macrodb>
        <macro>
            <name></name>
            <etc.../>
        </macro>
    </macrodb>"""

    def generateNprDoc(root):
        """Grab all elements under root and make into pretty documentation."""
        msg = name = syntax = description = code = comment = ""

        try:
            name = root.find('name').text
            syntax = root.find('stx').text
            description = root.find('dsc').text
            code = root.find('code').text
            comment = root.find('cmt').text
        except(AttributeError):
            print('Warning: Missing values in XML file.')

        print(syntax, name)
        # Syntax will contain the name and more. Use if it exists, else name
        if syntax is None:
            syntax = '@%s' % name

        msg += "Syntax         %s\n" % syntax  # content at col 16
        msg += "Description    %s\n" % description
        msg += "Code           %s\n" % code
        msg += "Notes\n"
        comment = comment.splitlines()
        for line in comment:
            msg += "  %s\n" % line.rstrip()
        return msg.rstrip()

    item = V.substr(V.word(cursor))
    filepath = (sublime.packages_path() +
                '/MagicSublime/lib/npr_macros.xml')
    root = ET.parse(filepath).getroot()
    macro = findInXML(root, item)
    if macro is not None:
        msg = generateNprDoc(macro)
        MS.show_output(msg)
    else:
        sublime.status_message("@%s not found" % item)


def procedure(cursor):
    """Open the selected procedure in a new tab."""
    item = V.substr(V.word(cursor))
    filepath = procedure = ""

    if sublime.platform() == 'windows':
        d = '\\'
    else:
        d = '/'
    f = str(V.file_name()).split(d)

    if f[len(f) - 3] == 'Z':
        e = len(f) - 3
    else:
        e = len(f) - 4

    for i in f[:e]:
        filepath += i + d

    for i in item.split('.'):
        if i.upper() == i:
            filepath += i + d
        else:
            procedure += i + '.'
    filepath += procedure.rstrip('.') + d + procedure + 'npr'

    V.window().open_file(filepath)


# Global maps
functions = {
    'entity.name.section.macro.title': macroTitle,
    'entity.name.function.macro.call': macroCall,
    'variable.other.local': local,
    'storage.temp.data.def': dataDef,
    'support.constant.data.def': dataDef,
    'variable.other.local.data.def': dataDef,
    'support.function.npr.macro': nprMacro,
    'entity.function.program.call': procedure
}


class MagicCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        """Dispatch of the MagicSublime master hotkey.

        This takes the scope, according to the NPR syntax definition, and
        performs the action specified in the global maps above."""

        global V        # The current view, used by nearly all functions

        V = self.view
        cursor = V.sel()[0].begin()
        scope = MS.scope(self, cursor)

        if scope in functions:
            functions[scope](cursor)
        else:
            sublime.status_message('"%s" function not yet written.' % scope)
