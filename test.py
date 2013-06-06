from magicsubl import ms
import sublime
import sublime_plugin
import xml.etree.ElementTree as ET


class TestCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        v = self.view
        cursorPosition = v.sel()[0].begin()
        scope = ms.scope(self, cursorPosition)
        self.functionEle(cursorPosition)

    def functionEle(self, cursorPosition):
        v = self.view
        selectedApp = "EDM"
        selectedDPM = "PAT"
        selectedItem = "status.event"
        filepath = (sublime.packages_path() +
                    '/MagicSublime/lib/Data Definitions/' +
                    selectedApp + '/' +
                    selectedDPM + '.xml')
        tree = ET.parse(filepath)
        dpm = tree.getroot()
        segments = dpm.find('segments')

        segment = self.findSegInXML(segments, selectedItem)

        if segment is not None:
            self.displaySegment(dpm, segment)
        else:
            print('Segment', selectedItem, 'not found. Searching for element.')
            segment, element = self.findEleInXML(segments, selectedItem)

        if element is not None:
            self.displayElement(dpm, segment, element)
        else:
            print('Element', selectedItem, 'not found. Bad news bears.')

    def findSegInXML(self, segments, selectedItem):
        return None

    def findEleInXML(self, segments, selectedItem):
        print selectedItem
        for segment in segments:
            elements = segment.find('elements')
            for element in elements:
                try:
                    name = element.get('name')
                    if name == selectedItem:
                        return (segment, element)
                except (NameError, AttributeError):
                    if element is not None and segment is not None:
                        print('Error in ' +
                              str(segment) + ' - ' + srt(element))
                    elif segment is not None:
                        print('Error in segment' + str(segment))
                    elif element is not None:
                        print('Error in element' + str(element))
                    else:
                        print('Error: bad XML!')

    def displayElement(self, dpm, segment, element):
        msg = ""
        name = dpm.get('name') + '.' + element.get('name')
        local = element.find('local').text
        physical = element.find('physical').text
        segment = segment.get('name')

        if name is not None:
            msg = msg + 'Element        %s\n' % name
        if local is not None:
            msg = msg + 'Local          %s\n' % local
        if physical is not None:
            msg = msg + 'Physical       %s\n' % physical
        if segment is not None:
            msg = msg + 'Segment        %s\n' % segment

        ms.show_output(msg, 'Packages/Text/Plain text.tmLanguage')
