"""Interface for the application

This file can be run, and will properly initialize interface (and rest of the
app) in your terminal.
Battle-tested on Solarized color scheme and under tmux.
"""
from contextlib import contextmanager
from datetime import datetime
import os
import os.path
import sys

import npyscreen

from pyaudio_fix import fix_pyaudio
import audio
import filters
import utils


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
    """Widget displaying list of tracks

    Properly loads the track after selecting.
    """
    def when_value_edited(self):
        """Loads the track to parent app after selecting

        Also cuts it to proper length, if requested.
        """
        if not self.value:
            return
        value = self.values[self.value[0]]
        song_info = self.parent.get_widget('song-info')
        filename = self.parent.parentApp.filenames.get(value)
        info = ('No. {no}'.format(no=value),) + audio.get_info(filename)
        song_info.values = info
        song_info.display()
        # Load info!
        app = self.parent.parentApp
        app.notify('Loading {title}...'.format(title=info[0]))
        self.parent.set_status('Loading')
        track = audio.load(filename)
        if not app._already_cut:
            track = audio.cut(track, app._track_length * 2)
        app.current_track = track
        app.current_track_no = value
        app.notify('Loaded!')
        # Also, clear filters
        self.parent.h_reset_filters()
        self.parent.set_status('Ready to play')


class MainForm(npyscreen.FormBaseNew):
    """Main form of the application"""
    def update_slider(self, value):
        """Sets value of position slider"""
        self.get_widget('position').value = value / 1000
        self.get_widget('position').display()

    def h_play(self, key):
        """Plays currently selected tracki

        Also applies filters, if any are selected.
        """
        app = self.parentApp
        if not app.current_track:
            app.notify('No track selected')
            return
        try:
            self.get_widget('track-list').values.remove(app.current_track_no)
        except ValueError:
            pass
        self.get_widget('track-list').value = []
        app.notify('Loading file...')
        # track = audio.cut(app.current_track
        app.notify('Applying filters...')
        track = filters.apply(app.current_track, self.parentApp.filters)
        track = track[:app._track_length]
        self.get_widget('position').entry_widget.out_of = len(track) / 1000
        self.get_widget('position').display()
        audio.play(track, notifier=self.update_slider)
        app.notify('Playing!')
        self.set_status('Playing')

    def h_stop(self, key):
        """Stops currently played track"""
        audio.stop()
        self.parentApp.notify('Stopped.')
        self.set_status('Ready to play')

    def h_select_filters(self, key):
        """Randomly selects filters"""
        selected = filters.get_random_filters()
        self.parentApp.filters = selected
        values = [filters.FILTERS_LIST.index(f) for f in selected]
        widget = self.get_widget('filters')
        widget.value = values
        widget.display()
        self.parentApp.notify('Filters randomized.')

    def h_reset_filters(self, key=None):
        """Clears filters selection"""
        widget = self.get_widget('filters')
        widget.value = []
        self.parentApp.filters = []
        widget.display()
        self.parentApp.notify('Filters cleared.')

    def set_status(self, message):
        """Sets value for the status widget

        This is kind of useful, because statusbar displays only the last
        message, and it's important to know whether song is playing, stopped
        or loaded.
        """
        song_status = self.get_widget('song-status')
        song_status.value = message
        song_status.display()

    def set_up_handlers(self):
        """Sets up handlers for keypresses

        Bonus: upper keys are also supported, meaning you don't need to worry
        about capslock!
        """
        super(MainForm, self).set_up_handlers()
        keys = {
            '^q': show_quit_popup,
            'a': self.h_play,
            's': self.h_stop,
            'f': self.h_select_filters,
            'r': self.h_reset_filters,
        }
        # Make upperkeys available, too!
        for key, func in list(keys.items()):
            keys[key.upper()] = func
        self.handlers.update(keys)


class SettingsForm(npyscreen.Form):
    """Form with settings

    Mainly used to get working directory path. You can also customize some
    other things here.
    Should be displayed before main form.
    """
    def afterEditing(self):
        """Sets proper values in the parent app after pressing OK button"""
        app = self.parentApp
        path = self.get_widget('path').value
        status = self.get_widget('status')
        track_length = self.get_widget('track_length').value
        already_cut = self.get_widget('track_cut').value
        seed = self.get_widget('seed').value
        if not path:
            status.value = 'Enter something'
            return
        if not os.path.isdir(path):
            status.value = 'That is not a directory'
            return
        app._path = path
        app._track_length = int(track_length) * 1000
        app._seed = seed
        app._already_cut = already_cut
        app.load_filenames(path)
        app.initialize_panzer()
        app.setNextForm('MAIN')


class App(npyscreen.NPSAppManaged):
    """Main application class"""
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)
        self._filenames = []
        self._path = None
        self.current_track = None
        self.current_track_no = None
        self._track_length = 35000  # in ms
        self._seed = None
        self._already_cut = False
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
        """Initializes all forms and populates it with widgets

        TODO: maybe put each form code into:
        1) separate method in App?
        2) init method in each form?
        Either of these would increase readability.
        """
        # Directory form
        directory_form = self.addForm(
            'directory',
            SettingsForm,
            name='Settings',
        )
        directory_form.add_widget(
            npyscreen.TitleText,
            name='Path',
            w_id='path',
        )
        directory_form.nextrely += 1
        directory_form.add_widget(
            npyscreen.FixedText,
            w_id='status',
            editable=False,
        )
        directory_form.add_widget(
            npyscreen.TitleText,
            name='Track length',
            value='35',
            w_id='track_length',
        )
        directory_form.add_widget(
            npyscreen.Checkbox,
            name='Already cut?',
            value=True,
            w_id='track_cut',
            relx=18,
        )
        directory_form.add_widget(
            npyscreen.TitleText,
            name='Random seed',
            value='this is some random seed',
            w_id='seed',
        )
        # Main form
        form = self.addForm('MAIN', MainForm, name='EKOiE')
        form.add_widget(
            TracksListWidget,
            name='Track number',
            values=[],
            w_id='track-list',
            max_height=form.lines-7,
            width=int(form.columns/2),
        )
        form.add_widget(
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
        # Song status
        form.add_widget(
            npyscreen.TitleFixedText,
            height=1,
            editable=False,
            name='Song status',
            w_id='song-status',
        )
        form.nextrely += 2
        # Slider
        form.add_widget(
            npyscreen.TitleSlider,
            name='Position',
            out_of=35,
            lowest=0,
            value=0,
            label=True,
            w_id='position',
        )
        form.nextrely += 2
        form.add_widget(
            npyscreen.TitleMultiSelect,
            editable=False,
            height=15,
            name='Filters',
            w_id='filters',
            values=filters.FILTERS_LIST,
        )
        self.setNextForm('directory')

    def notify(self, message):
        """Displays notification in the bottom of the screen"""
        status = self.getForm('MAIN').get_widget('status')
        status.value = '[{time}] {message}'.format(
            time=datetime.now().strftime('%H:%M:%S'),
            message=message,
        )
        status.display()

    def load_filenames(self, path):
        """Loads filenames of tracks from working directory"""
        self.notify(
            'Loading files from {path}...'.format(path=path),
        )
        self.filenames = utils.shuffle(
            utils.get_filenames(path),
            seed=self._seed,
        )
        self.notify('{count} files loaded.'.format(count=len(self.filenames)))

    def initialize_panzer(self):
        self.notify('Initializing panzerfaust filter...')
        filters.initialize_panzer_tracks()
        self.notify('Panzerfaust filter initialized.')


if __name__ == '__main__':
    with use_xterm():
        fix_pyaudio()
        app = App()
        try:
            app.run()
        except KeyboardInterrupt:
            quit()
