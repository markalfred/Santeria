# Repository of tools for MagicSublime

import sublime
import sublime_plugin


def show_output(msg, syntax='Packages/Text/Plain text.tmLanguage'):
    win = sublime.active_window()
    if win:
        panel = win.get_output_panel('ms_doc')
        panel.set_read_only(False)
        edit = panel.begin_edit()
        panel.set_syntax_file(syntax)
        panel.settings().set('gutter', True)
        panel.settings().set('line_numbers', False)
        panel.settings().set('word_wrap', True)
        panel.settings().set('wrap_width', 0)
        panel.settings().set('scroll_past_end', False)
        panel.insert(edit, 0, msg + '\n')
        panel.end_edit(edit)
        panel.set_read_only(True)
        win.run_command('show_panel',
                        {'panel': 'output.ms_doc'})


def scope(self, cursorPosition):
    return self.view.scope_name(cursorPosition).split(' ')[1]
