import random

import audio


def _prepare(track):
    """Cut track to exact number of seconds we need

    This function is required, because all incoming tracks are twice as long,
    in order to be able to properly use speed up/tone down filters.
    """
    return track[:audio.SEGMENT_LENGTH_SECONDS]


def speed_up(track):
    """Speeds up the track"""
    rate = 1.4 + round(0.5 * random.random(), 2)
    return audio.pitch(track, rate)


def slow_down(track):
    """Slows down the track"""
    rate = 0.4 + round(0.5 * random.random(), 2)
    return audio.pitch(track, rate)


def reverse(track):
    """Reverses the track"""
    return audio.reverse(track)


def frequency(track):
    """Changes frequency, effectively worsening the quality"""
    frequency = random.randint(4000, 20000)
    return audio.frequency(track, frequency)


def volume_changer(track):
    slice_length = random.choice((250, 500, 750))
    return audio.volume_changer(track, slice_length)


def tone_down(track):
    rate = 0.4 + round(0.5 * random.random(), 2)
    return audio.tone_down(track, rate)


# NOTE (2015.07.02): all filters that use pydub's speedup function are currently
# turned off, due to my netbook being too slow to be able to use it
FILTERS = {
    'speed up': speed_up,
    'slow down': slow_down,
    'reverse': reverse,
    'frequency': frequency,
    'volume changer': volume_changer,
    # 'tone down': tone_down,
}
FILTERS_LIST = list(FILTERS)
DONT_LIKE_EACH_OTHER = {
    'speed up': ('slow down',),
    'slow down': ('speed up',),
    'reverse': (),
    'frequency': (),
    'volume changer': (),
    'tone down': ('slow down',),
}


def get_random_filters():
    """Returns list of up to 3 random filters than can be applied

    Filters that "don't like each other" are excluded.
    """
    value = random.random()
    if value < 0.15:
        count = 0
    elif value < 0.5:
        count = 1
    elif value < 0.8:
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
