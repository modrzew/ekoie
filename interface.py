from contextlib import contextmanager
from datetime import datetime
import os
import random
import sys

import npyscreen

from pyaudio_fix import fix_pyaudio
import audio
import filters
import utils


DIRECTORY = '/media/d/OneDrive/Muzyka/Chińskie bajki'  # TODO: change this


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
        value = self.value[0]
        song_info = self.parent.get_widget('song-info')
        filename = self.parent.parentApp.filenames.get(value)
        info = audio.get_info(filename)
        song_info.values = info
        song_info.display()
        # Load info!
        self.parent.parentApp.notify('Loading {title}...'.format(title=info[0]))
        self.parent.set_status('Loading')
        track = audio.load(filename)
        self.parent.parentApp.current_track = audio.cut(track, 70000)
        self.parent.parentApp.current_track_no = self.values[value]
        self.parent.parentApp.notify('Loaded!')
        self.parent.set_status('Ready to play')


class MyForm(npyscreen.FormBaseNew):
    def h_play(self, key):
        app = self.parentApp
        if not app.current_track:
            return
        try:
            self.get_widget('track-list').values.remove(app.current_track_no)
        except ValueError:
            pass
        self.get_widget('track-list').value = []
        app.notify('Loading file...')
        track = audio.cut(app.current_track)
        app.notify('Applying filters...')
        track = filters.apply(track, self.parentApp.filters)
        audio.play(track)
        app.notify('Playing!')
        self.set_status('Playing')

    def h_stop(self, key):
        audio.stop()
        self.parentApp.notify('Stopped.')
        self.set_status('Ready to play')

    def h_select_filters(self, key):
        selected = filters.get_random_filters()
        self.parentApp.filters = selected
        values = [filters.FILTERS_LIST.index(f) for f in selected]
        widget = self.get_widget('filters')
        widget.value = values
        widget.display()
        self.parentApp.notify('Filters randomized.')

    def set_status(self, message):
        song_status = self.get_widget('song-status')
        song_status.value = message
        song_status.display()

    def set_up_handlers(self):
        super(MyForm, self).set_up_handlers()
        keys = {
            '^q': show_quit_popup,
            'a': self.h_play,
            's': self.h_stop,
            'f': self.h_select_filters,
        }
        # Make upperkeys available, too!
        for key, func in list(keys.items()):
            keys[key.upper()] = func
        self.handlers.update(keys)


class App(npyscreen.NPSAppManaged):
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)
        self._filenames = []
        self.current_track = None
        self.current_track_no = None
        self.filters = []

    @property
    def filenames(self):
        return self._filenames

    @filenames.setter
    def filenames(self, value):
        self._filenames = value
        track_number = self.getForm('MAIN').get_widget('track-list')
        track_number.values = list(self._filenames.keys())
        track_number.display()

    def onStart(self):
        form = self.addForm('MAIN', MyForm, name='EKOiE')
        form.add_widget(
            TracksListWidget,
            name='Track number',
            values=[],
            w_id='track-list',
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
        # Split screen vertically in half
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
        form.add_widget(
            npyscreen.TitleFixedText,
            height=3,
            name='Song status',
            editable=False,
            w_id='song-status',
        )
        form.add_widget(
            npyscreen.TitleMultiSelect,
            editable=False,
            height=15,
            name='Filters',
            w_id='filters',
            values=filters.FILTERS_LIST,
        )
        self.setNextForm('MAIN')

        self.load_filenames()

    def notify(self, message):
        self.status.value = '[{time}] {message}'.format(
            time=datetime.now().strftime('%H:%M:%S'),
            message=message,
        )
        self.status.display()

    def load_filenames(self):
        self.notify(
            'Loading files from {directory}...'.format(directory=DIRECTORY),
        )
        self.filenames = utils.shuffle(utils.get_filenames(DIRECTORY))
        self.notify('{count} files loaded.'.format(count=len(self.filenames)))


if __name__ == '__main__':
    with use_xterm():
        fix_pyaudio()
        app = App()
        try:
            app.run()
        except KeyboardInterrupt:
            quit()
