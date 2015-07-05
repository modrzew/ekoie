"""Track cutter utility

Used for cutting tracks to proper size.
"""
import os
import os.path
import sys

from mutagen.easyid3 import EasyID3

import audio
import utils


def pretty_print(msg):
    sys.stdout.write('\r{msg}\033[K'.format(msg=msg))


input_dir = input('Input directory (will be read recursively): ')
output_dir = input(
    'Output directory (will be created if not present): [./tracks]'
) or './tracks'
length = input('Track length, in seconds: [70] ') or 70
length = int(length)

if not os.path.exists(output_dir):
    os.mkdir(output_dir)

filenames = utils.get_filenames(input_dir)
filenames_length = len(filenames)
for i, filename in enumerate(filenames.values(), start=1):
    pretty_print(
        'Converting file {i}/{total}... [{filename}]'.format(
            i=i,
            total=filenames_length,
            filename=os.path.basename(filename),
        ),
    )
    track = audio.load(filename)
    track = audio.cut(track, length * 1000)
    new_filename = os.path.join(
        output_dir,
        os.path.basename(filename),
    )
    track.export(new_filename, format='mp3')
    # Copy metadata, too
    data = EasyID3(filename)
    data.save(new_filename, v1=2)
print()
print('Done.')
