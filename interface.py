from contextlib import contextmanager
import os
import sys

import npyscreen

import audio


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
    audio.stop()
    sys.exit(0)


def show_quit_popup(key=None):
    """Display popup asking whether to quit application"""
    result = npyscreen.notify_yes_no(
        message='Do you really want to quit?',
        title='Quit',
        editw=1,  # select No button by default
    )
    if result:
        quit()


class MyForm(npyscreen.FormBaseNew):
    def h_play(self, key):
        self.parentApp.notify('Loading file...')
        track = audio.load('sample.mp3')
        self.parentApp.notify('Cutting into pieces...')
        cut = audio.cut(track)
        self.parentApp.notify('Trying to play...')
        audio.play(cut)
        self.parentApp.notify('Playing!')

    def h_stop(self, key):
        audio.stop()

    def set_up_handlers(self):
        super(MyForm, self).set_up_handlers()
        keys = {
            'q': show_quit_popup,
            'p': self.h_play,
            's': self.h_stop,
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
            width=50,
            height=10,
        )
        self.status = form.add_widget(
            npyscreen.TitleFixedText,
            width=50,
            height=3,
            name='Status',
        )
        self.setNextForm('MAIN')

    def notify(self, message):
        self.status.value = message
        self.status.display()


if __name__ == '__main__':
    with use_xterm():
        app = App()
        try:
            app.run()
        except KeyboardInterrupt:
            quit()
