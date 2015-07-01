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


class QuitPopup(npyscreen.ActionPopup):
    """Popup used for exiting the app"""
    def on_ok(self):
        self.parentApp.setNextForm(None)

    def on_cancel(self):
        self.parentApp.switchFormPrevious()


class MyForm(npyscreen.FormBaseNew):
    def h_quit(self, key):
        self.parentApp.switchForm('quit_popup')

    def set_up_handlers(self):
        super(MyForm, self).set_up_handlers()
        keys = {
            'q': self.h_quit,
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

        quit_popup = self.addForm(
            'quit_popup',
            QuitPopup,
            name='Really quit?',
            lines=5,
        )
        quit_popup.show_atx = 40
        quit_popup.show_aty = 20

        self.setNextForm('MAIN')


if __name__ == '__main__':
    with use_xterm():
        app = App()
        try:
            app.run()
        except KeyboardInterrupt:
            quit()
