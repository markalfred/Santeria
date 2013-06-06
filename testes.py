from magicsubl import ms
import sublime
import sublime_plugin
import xml.etree.ElementTree as ET


class TesteCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        print 'hello!'
        print ms.scopes
