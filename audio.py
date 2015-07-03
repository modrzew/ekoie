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
    return pydub.AudioSegment.from_mp3(filename)


def speed_up(segment, speed):
    if speed <= 1:
        raise ValueError('speed must not be lower than 1')
    return segment.speedup(playback_speed=speed, chunk_size=80, crossfade=5)


def reverse(segment):
    return segment.reverse()


def frequency(segment, frequency):
    return segment.set_frame_rate(frequency)


def volume_changer(segment, slice_length=250):
    # Split segment into equally sized slices
    slices = make_chunks(segment, slice_length)
    result = slices[0]
    for i, s in enumerate(slices[1:]):
        if i % 2 == 0:
            s -= 15
        result += s
    return result


def pitch(segment, rate):
    return segment._spawn(
        segment._data,
        {'frame_rate': int(segment.frame_rate*rate)},
    )


def tone_down(segment, rate):
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
    segments_count = len(segments)
    # Make sure that segments have the same length
    first_segment_length = len(segments[0])
    slices = []
    for segment in segments:
        if len(segment) != first_segment_length:
            raise ValueError('all segments need to have the same length')
        slices.append(make_chunks(segment, slice_length))
    first = slices[0][0]
    for i, s in enumerate(slices[1:]):
        first += slices[i % segments_count][i]


def cut(segment, length=None):
    """Selects random sample from the segment"""
    if not length:
        length = SEGMENT_LENGTH_SECONDS * 1000
    start = random.randint(
        MINIMUM_STARTING_POINT * 1000,
        MAXIMUM_STARTING_POINT * 1000,
    )
    end = start + length
    if len(segment) < end:  # segment is too short?
        end = len(segment) - 1
        start = end - length
    return segment[start:end]


def get_info(filename):
    info = EasyID3(filename)
    return (
        ', '.join(info['title']),
        ', '.join(info['artist']),
        os.path.basename(filename),
    )
