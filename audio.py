"""Audio tools and helpers

`segment` in function arguments stands for AudioSegment.
"""
import random

import pydub
import pydub.playback


SEGMENT_LENGTH_SECONDS = 35  # 35
MINIMUM_STARTING_POINT = 30  # skip at least 30 seconds from the beginning
MAXIMUM_STARTING_POINT = 90  # ...and no more than 90 seconds


def play(segment):
    pydub.playback.play(segment)


def speed_up(segment, speed):
    if speed <= 1:
        raise ValueError('speed must not be lower than 1')
    return segment.speedup(playback_speed=speed, chunk_size=80, crossfade=5)


def reverse(segment):
    return segment.reverse()


def random_frequency(segment):
    frequency = random.randint(4000, 20000)
    return segment.set_frame_rate(frequency)


def volume_changer(segment, slice_length=250):
    # Split segment into equally sized slices
    slices = [
        segment[i:i+slice_length]
        for i in range(0, len(segment), slice_length)
    ]
    result = slices[0]
    for i, s in enumerate(slices[1:]):
        if i % 2 == 0:
            s -= 30
        result += s
    return result


def pitch(segment, rate):
    return segment._spawn(
        segment._data,
        {'frame_rate': segment.frame_rate*rate},
    )


def tone_down(segment, rate):
    result = segment._spawn(
        segment._data,
        {'frame_rate': segment.frame_rate*rate},
    )
    return result.speedup(playback_speed=2, chunk_size=80, crossfade=5)


def mix_segments(segments, slice_length=500):
    segments_count = len(segments)
    # Make sure that segments have the same length
    first_segment_length = len(segments[0])
    slices = []
    for segment in segments:
        if len(segment) != first_segment_length:
            raise ValueError('all segments need to have the same length')
        slices.append([segment[i:i+500] for i in range(0, len(segment), 500)])
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
