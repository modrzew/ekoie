from contextlib import contextmanager
import os
import sys

import npyscreen


@contextmanager
def use_xterm():
    """Helper setting proper TERM value

    Required for colors to work under 16-color tmux.
    """
    old_value = os.environ.get('TERM')
    os.environ['TERM'] = 'xterm'
    yield
    if old_value is not None:
        os.environ['TERM'] = old_value


def quit():
    """Close application gracefully"""
    sys.exit(0)


def show_quit_popup():
    """Display popup asking whether to quit application"""
    result = npyscreen.notify_yes_no(
        message='Do you really want to quit?',
        title='Quit',
        editw=1,  # select No button by default
    )
    if result:
        quit()


class MyForm(npyscreen.FormBaseNew):
    def set_up_handlers(self):
        super(MyForm, self).set_up_handlers()
        keys = {
            'q': show_quit_popup,
        }
        # Make upperkeys available, too!
        for key, func in list(keys.items()):
            keys[key.upper()] = func
        self.handlers.update(keys)


class App(npyscreen.NPSAppManaged):
    def onStart(self):
        form = self.addForm('MAIN', MyForm, name='EKOiE')
        form.add_widget(
            npyscreen.TitleSelectOne,
            name='Track number',
            values=[1, 2, 3, 4, 5],
        )
        self.setNextForm('MAIN')


if __name__ == '__main__':
    with use_xterm():
        app = App()
        try:
            app.run()
        except KeyboardInterrupt:
            quit()
