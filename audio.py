"""Audio tools and helpers

`segment` in function arguments stands for AudioSegment.
"""
import os.path
import random
import threading

from pydub.utils import make_chunks
from mutagen.easyid3 import EasyID3
import pyaudio
import pydub


SEGMENT_LENGTH_SECONDS = 35  # 35
MINIMUM_STARTING_POINT = 30  # skip at least 30 seconds from the beginning
MAXIMUM_STARTING_POINT = 90  # ...and no more than 90 seconds

_CURRENT_SONG_PLAYER = None


class PyaudioPlayer(threading.Thread):
    """Improved audio player, based on pydub.playback

    This player is based on threading, with simple method to stop playing
    without raising KeyboardInterruption.
    """
    def __init__(self, segment, notifier=None):
        super(PyaudioPlayer, self).__init__()
        self.segment = segment
        self._playing = True
        self._notifier = notifier

    def run(self):
        player = pyaudio.PyAudio()
        stream = player.open(
            format=player.get_format_from_width(self.segment.sample_width),
            channels=self.segment.channels,
            rate=self.segment.frame_rate,
            output=True,
        )

        # break audio into quarter-second chunks (to allows interrupts)
        for i, chunk in enumerate(make_chunks(self.segment, 250)):
            if self._notifier:
                self._notifier(i*250)
            if not self._playing:
                break
            stream.write(chunk._data)

        stream.stop_stream()
        stream.close()
        player.terminate()

    def stop(self):
        """Stops playing current song"""
        self._playing = False


def play(segment, notifier=None):
    """Plays segment using global player

    If another song is being played, it's stopped (and its player is
    destroyed).
    """
    global _CURRENT_SONG_PLAYER
    stop()
    _CURRENT_SONG_PLAYER = PyaudioPlayer(segment, notifier)
    _CURRENT_SONG_PLAYER.start()


def stop():
    """Stops playing current song and destroys the player."""
    global _CURRENT_SONG_PLAYER
    if _CURRENT_SONG_PLAYER:
        _CURRENT_SONG_PLAYER.stop()
        _CURRENT_SONG_PLAYER = None


def load(filename):
    """Loads a track based on path

    Note: only MP3 supported right now.
    """
    return pydub.AudioSegment.from_mp3(filename)


def speed_up(segment, speed):
    """Speeds up the track, while keeping the same length

    Note: pydub's speedup is SLOW.
    """
    if speed <= 1:
        raise ValueError('speed must not be lower than 1')
    return segment.speedup(playback_speed=speed, chunk_size=80, crossfade=5)


def reverse(segment):
    """Reverses the track"""
    return segment.reverse()


def frequency(segment, frequency):
    """Changes frequency

    Lower frequency worsenes the quality.
    """
    return segment.set_frame_rate(frequency)


def volume_changer(segment, slice_length=250):
    """Changes volume of the track on set interval

    The track becomes something like this:
    H L H L H L H L...
    where H means high volume, and L stands for low (reduced) volume.
    """
    # Split segment into equally sized slices
    slices = make_chunks(segment, slice_length)
    result = slices[0]
    for i, s in enumerate(slices[1:]):
        if i % 2 == 0:
            s -= 15
        result += s
    return result


def pitch(segment, rate):
    """Changes the pitch, and also track's speed"""
    return segment._spawn(
        segment._data,
        {'frame_rate': int(segment.frame_rate*rate)},
    )


def tone_down(segment, rate):
    """Lowers track's tone while keeping the same speed

    Basically does the same thing as pitch, but retains the speed.
    Note: pydub's speedup is SLOW.
    """
    result = segment._spawn(
        segment._data,
        {'frame_rate': int(segment.frame_rate*rate)},
    )
    return result.speedup(
        playback_speed=round(1/rate, 2),
        chunk_size=80,
        crossfade=5,
    )


def mix_segments(segments, slice_length=500):
    """Mixes two tracks together

    Given two tracks 1 and 2, output becomes something like this:
    1 2 1 2 1 2 1 2...
    """
    segments_count = len(segments)
    # Cut to the shortest segment
    shortest_length = min(len(segment) for segment in segments)
    segments = [segment[:shortest_length] for segment in segments]
    slices = [make_chunks(segment, slice_length) for segment in segments]
    first = slices[0][0]
    for i, s in enumerate(slices[0][1:], start=1):
        first += slices[i % segments_count][i]
    return first


def cut(segment, length=None, min_start=None, max_start=None):
    """Selects random sample from the segment"""
    if not length:
        length = SEGMENT_LENGTH_SECONDS * 1000
    start = random.randint(
        min_start if min_start is not None else MINIMUM_STARTING_POINT * 1000,
        max_start if max_start is not None else MAXIMUM_STARTING_POINT * 1000,
    )
    end = start + length
    if len(segment) < end:  # segment is too short?
        end = len(segment) - 1
        start = end - length
    return segment[start:end]


def get_info(filename):
    """Returns tuple of string info about the song

    Note: only MP3 supported right now.
    """
    info = EasyID3(filename)
    return (
        ', '.join(info['title']),
        ', '.join(info['artist']),
        os.path.basename(filename),
    )


def overlay(tracks):
    """Mixes multiple tracks together by layering one onto another"""
    main_track = tracks[0]
    for track in tracks[1:]:
        main_track = main_track.overlay(track, loop=True)
    return main_track
