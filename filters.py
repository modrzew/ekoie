import os
import os.path
import random

from . import (
    audio,
    config
)


_PANZER_TRACKS = []
_PANZER_PATH = 'panzerfaust'
_OVERLAY_TRACKS = []
_OVERLAY_PATH = 'overlay'


def initialize_panzer_tracks():
    """Initializes panzerfaust tracks, to keep them in memory for later use"""
    if not os.path.exists(_PANZER_PATH):
        return
    for filename in os.listdir(_PANZER_PATH):
        if not filename.endswith('.mp3'):
            continue
        path = os.path.join(_PANZER_PATH, filename)
        track = audio.load(path)
        _PANZER_TRACKS.append(track)


def initialize_overlay_tracks():
    """Initializes overlay tracks, to keep them in memory for later use"""
    if not os.path.exists(_OVERLAY_PATH):
        return
    for filename in os.listdir(_OVERLAY_PATH):
        if not filename.endswith('.mp3'):
            continue
        path = os.path.join(_OVERLAY_PATH, filename)
        track = audio.load(path)
        _OVERLAY_TRACKS.append(track)


def _prepare(track):
    """Cut track to exact number of seconds we need

    This function is required, because all incoming tracks are twice as long,
    in order to be able to properly use speed up/tone down filters.
    """
    return track[:audio.SEGMENT_LENGTH_SECONDS]


def speed_up(track):
    """Speeds up the track"""
    rate = random.uniform(*config.SPEED_UP_RANGE)
    return audio.pitch(track, round(rate, 2))


def slow_down(track):
    """Slows down the track"""
    rate = random.uniform(*config.SLOW_DOWN_RANGE)
    return audio.pitch(track, round(rate, 2))


def reverse(track):
    """Reverses the track"""
    return audio.reverse(track)


def frequency(track):
    """Changes frequency, effectively worsening the quality"""
    frequency = random.randint(*config.FREQUENCY_RANGE)
    return audio.frequency(track, frequency)


def volume_changer(track):
    """Changes volume of the track"""
    slice_length = random.choice(config.SLICE_LENGTH)
    return audio.volume_changer(track, slice_length)


def tone_down(track):
    """Lowers tone of the track without lowering speed"""
    rate = random.uniform(*config.TONE_DOWN_RANGE)
    return audio.tone_down(track, round(rate, 2))


def panzerfaust(track):
    """Mixes track with one of the panzer tracks"""
    if not _PANZER_TRACKS:
        return track
    panzer_track = random.choice(_PANZER_TRACKS)
    # Cut panzer track to track's length
    track_length = len(track)
    # Fix: not all panzer tracks have proper length!
    while len(panzer_track) < track_length:
        panzer_track = panzer_track + panzer_track
    panzer_track = panzer_track[:track_length]
    # Lower volume of panzer track
    panzer_track -= config.PANZER_VOLUME_DECREASE
    slice_length = random.choice(config.SLICE_LENGTH)
    return audio.mix_segments([track, panzer_track], slice_length)


def multiple_tracks(tracks):
    """Mixes multiple tracks into single one

    Tracks will be mixed with either of these methods, chosen randomly:
    - mix_segments
    - overlay
    """
    slice_length = random.choice(config.MULTIPLE_TRACKS_LENGTH)
    return audio.mix_segments(tracks, slice_length)


def overlay_music(track):
    """Adds another song layer"""
    if not _OVERLAY_TRACKS:
        return track
    overlay_track = random.choice(_OVERLAY_TRACKS)
    # Cut overlay track to track's length
    track_length = len(track)
    overlay_track = audio.cut(overlay_track, track_length)
    # Lower volume of our track
    track -= config.PANZER_VOLUME_DECREASE
    return audio.overlay([track, overlay_track])


# NOTE (2015.07.02): all filters that use pydub's speedup function are
# currently turned off, due to my netbook being too slow to be able to use it
FILTERS = {
    'speed up': speed_up,
    'slow down': slow_down,
    'reverse': reverse,
    'frequency': frequency,
    'volume changer': volume_changer,
    # 'tone down': tone_down,
    'panzerfaust': panzerfaust,
    'overlay': overlay_music,
}
FILTERS_LIST = list(FILTERS)
DONT_LIKE_EACH_OTHER = {
    'speed up': ('slow down',),
    'slow down': ('speed up',),
    'reverse': (),
    'frequency': (),
    'volume changer': (),
    'tone down': ('slow down',),
    'panzerfaust': ('volume changer', 'speed up', 'slow down'),
    'overlay': ('panzerfaust', 'speed up'),
}


def get_random_filters():
    """Returns list of up to 3 random filters than can be applied

    Filters that "don't like each other" are excluded.
    """
    value = random.random()
    if value < config.MULTIPLE_FILTERS_CHANCES[0]:
        count = 0
    elif value < config.MULTIPLE_FILTERS_CHANCES[1]:
        count = 1
    elif value < config.MULTIPLE_FILTERS_CHANCES[2]:
        count = 2
    else:
        count = 3
    choose_from = list(FILTERS)
    filters = []
    for i in range(count):
        choice = None
        while not choice and choose_from:
            choice = random.choice(choose_from)
            for not_liked in DONT_LIKE_EACH_OTHER[choice]:
                if not_liked in choose_from:
                    choose_from.remove(not_liked)
        if choice:
            filters.append(choice)
            choose_from.remove(choice)
    return filters


def apply(track, filters):
    """Applies given filters on the track

    Filters list must be passed as list of strings.
    """
    for fil in filters:
        track = FILTERS[fil](track)
    return track
