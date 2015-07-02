from contextlib import contextmanager
import os
import sys

import npyscreen

from pyaudio_fix import fix_pyaudio
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


class TracksListWidget(npyscreen.TitleSelectOne):
    def when_value_edited(self):
        if not self.value:
            return
        song_info = self.parent.get_widget('song-info')
        song_info.values = ['hurr', 'durr', str(self.value[0])]
        song_info.display()


class MyForm(npyscreen.FormBaseNew):
    def h_play(self, key):
        self.parentApp.notify('Loading file...')
        track = audio.load('sample.mp3')
        audio.play(audio.cut(track))
        self.parentApp.notify('Playing!')

    def h_stop(self, key):
        audio.stop()
        self.parentApp.notify('Stopped.')

    def h_randomize(self, key):
        pass

    def h_goto(self, key):
        pass

    def h_shuffle(self, key):
        pass

    def h_delete(self, key):
        pass

    def set_up_handlers(self):
        super(MyForm, self).set_up_handlers()
        keys = {
            '^q': show_quit_popup,
            'a': self.h_play,
            'd': self.h_delete,
            's': self.h_stop,
            'r': self.h_randomize,
            'g': self.h_goto,
            'f': self.h_shuffle,
        }
        # Make upperkeys available, too!
        for key, func in list(keys.items()):
            keys[key.upper()] = func
        self.handlers.update(keys)


class App(npyscreen.NPSAppManaged):
    def onStart(self):
        form = self.addForm('MAIN', MyForm, name='EKOiE')
        form.add_widget(
            TracksListWidget,
            name='Track number',
            values=range(1, 250),
            w_id='track-number',
            max_height=form.lines-7,
            width=int(form.columns/2),
        )
        self.status = form.add_widget(
            npyscreen.TitleFixedText,
            height=2,
            name='Status',
            rely=-3,
            editable=False,
            w_id='status',
        )
        form.nextrely = 2
        form.nextrelx = int(form.columns/2) + 2
        form.add_widget(
            npyscreen.MultiLineEditableTitle,
            height=6,
            name='Song info',
            editable=False,
            values=[],
            w_id='song-info',
        )
        self.setNextForm('MAIN')

    def notify(self, message):
        self.status.value = message
        self.status.display()


if __name__ == '__main__':
    with use_xterm():
        fix_pyaudio()
        app = App()
        try:
            app.run()
        except KeyboardInterrupt:
            quit()
